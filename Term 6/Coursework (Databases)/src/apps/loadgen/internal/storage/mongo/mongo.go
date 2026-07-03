package mongo

import (
	"context"
	"fmt"
	"loadgen/internal/logger"
	"loadgen/internal/workload"
	"time"

	"go.mongodb.org/mongo-driver/v2/bson"
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.mongodb.org/mongo-driver/v2/mongo/options"
)

type MongoEngine struct {
	log                *logger.Logger
	MongoHost          string
	MongoPort          int
	MongoUser          string
	MongoPassword      string
	MongoDatabase      string
	NestedDatabase     string
	NormalizedDatabase string
	Client             *mongo.Client
}

func NewMongoEngine(log *logger.Logger, host string, port int, user, password, dbName, nestedDB, normalizedDB string) *MongoEngine {
	if log == nil {
		panic("logger cannot be nil")
	}
	if host == "" {
		panic("host cannot be empty")
	}
	if port <= 0 {
		panic("port must be a positive integer")
	}
	if user == "" {
		panic("user cannot be empty")
	}
	if password == "" {
		panic("password cannot be empty")
	}
	if dbName == "" {
		panic("dbName cannot be empty")
	}
	return &MongoEngine{
		log:                log,
		MongoHost:          host,
		MongoPort:          port,
		MongoUser:          user,
		MongoPassword:      password,
		MongoDatabase:      dbName,
		NestedDatabase:     nestedDB,
		NormalizedDatabase: normalizedDB,
	}
}

func (m *MongoEngine) Connect(numberOfConnections int) error {
	if numberOfConnections <= 0 {
		return fmt.Errorf("numberOfConnections must be a positive integer")
	}

	m.log.Info().Msg("Connecting to MongoDB")
	uri := fmt.Sprintf(
		"mongodb://%s:%s@%s:%d/%s?authSource=admin",
		m.MongoUser, m.MongoPassword, m.MongoHost, m.MongoPort, m.MongoDatabase)
	clientOptions := options.Client().
		ApplyURI(uri).
		SetMaxPoolSize(uint64(numberOfConnections)).
		SetMinPoolSize(uint64(numberOfConnections)).
		SetMaxConnIdleTime(30 * time.Second).
		SetConnectTimeout(10 * time.Second).
		SetServerSelectionTimeout(5 * time.Second).
		SetMaxConnIdleTime(10 * time.Minute)

	// Create MongoDB client
	client, err := mongo.Connect(clientOptions)
	if err != nil {
		return fmt.Errorf("failed to create MongoDB client: %w", err)
	}
	m.Client = client
	return nil
}

func (m *MongoEngine) Ping() error {
	m.log.Info().Msg("Pinging MongoDB")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := m.Client.Ping(ctx, nil); err != nil {
		return fmt.Errorf("failed to ping MongoDB: %w", err)
	}
	m.log.Info().Msg("MongoDB ping successful")
	return nil
}

func (m *MongoEngine) Close() error {
	m.log.Info().Msg("Closing MongoDB connection")
	if m.Client != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		if err := m.Client.Disconnect(ctx); err != nil {
			return fmt.Errorf("failed to disconnect MongoDB client: %w", err)
		}
	}
	return nil
}

func (m *MongoEngine) Status() (string, error) {
	m.log.Info().Msg("Checking MongoDB status")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := m.Client.Ping(ctx, nil); err != nil {
		return "unhealthy", fmt.Errorf("MongoDB is unhealthy: %w", err)
	}
	return "healthy", nil
}

func (m *MongoEngine) ChangePoolSize(newSize int) error {
	if newSize <= 0 {
		return fmt.Errorf("newSize must be a positive integer")
	}
	m.log.Info().
		Int("newSize", newSize).
		Msg("Changing MongoDB connection pool size")

	clientOptions := options.Client().
		SetMaxPoolSize(uint64(newSize)).
		SetMinPoolSize(uint64(newSize))

	// We need to wait for existing connections to be closed
	// before we can create a new client with the updated pool size
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := m.Client.Disconnect(ctx); err != nil {
		return fmt.Errorf("failed to disconnect existing MongoDB client: %w", err)
	}

	client, err := mongo.Connect(clientOptions)
	if err != nil {
		return fmt.Errorf("failed to create new MongoDB client: %w", err)
	}
	m.Client = client
	return nil
}

func (m *MongoEngine) GetType() string {
	return "mongo"
}

func (m *MongoEngine) Clear(ctx context.Context, model string) error {
	db, collections, err := m.modelDB(model)
	if err != nil {
		return err
	}
	for _, collection := range collections {
		if _, err := db.Collection(collection).DeleteMany(ctx, bson.D{}); err != nil {
			return fmt.Errorf("clear %s: %w", collection, err)
		}
	}
	return nil
}

func (m *MongoEngine) Seed(ctx context.Context, model string, world workload.World) error {
	switch model {
	case workload.ModelMongoNested:
		return m.seedNested(ctx, world)
	case workload.ModelMongoNormalized:
		return m.seedNormalized(ctx, world)
	default:
		return fmt.Errorf("unsupported MongoDB model: %s", model)
	}
}

func (m *MongoEngine) WriteComplexEventBatch(ctx context.Context, model string, req workload.OperationRequest) (workload.OperationResult, error) {
	events := workload.GenerateEvents(req)
	switch model {
	case workload.ModelMongoNested:
		return m.insertNestedEvents(ctx, events)
	case workload.ModelMongoNormalized:
		return m.insertNormalizedEvents(ctx, events)
	default:
		return workload.OperationResult{}, fmt.Errorf("unsupported MongoDB model: %s", model)
	}
}

func (m *MongoEngine) WriteTelemetryStream(ctx context.Context, model string, req workload.OperationRequest) (workload.OperationResult, error) {
	records := workload.GenerateTelemetry(req)
	switch model {
	case workload.ModelMongoNested:
		return m.insertNestedTelemetry(ctx, records)
	case workload.ModelMongoNormalized:
		return m.insertNormalizedTelemetry(ctx, records)
	default:
		return workload.OperationResult{}, fmt.Errorf("unsupported MongoDB model: %s", model)
	}
}

func (m *MongoEngine) AggObjectActivityByArea(ctx context.Context, model string, req workload.OperationRequest) (workload.OperationResult, error) {
	switch model {
	case workload.ModelMongoNested:
		return m.aggNestedObjectActivityByArea(ctx, req)
	case workload.ModelMongoNormalized:
		return m.aggNormalizedObjectActivityByArea(ctx, req)
	default:
		return workload.OperationResult{}, fmt.Errorf("unsupported MongoDB model: %s", model)
	}
}

func (m *MongoEngine) AggTelemetryHealthWindow(ctx context.Context, model string, req workload.OperationRequest) (workload.OperationResult, error) {
	switch model {
	case workload.ModelMongoNested:
		return m.aggNestedTelemetryHealthWindow(ctx, req)
	case workload.ModelMongoNormalized:
		return m.aggNormalizedTelemetryHealthWindow(ctx, req)
	default:
		return workload.OperationResult{}, fmt.Errorf("unsupported MongoDB model: %s", model)
	}
}

func (m *MongoEngine) ReadIncidentTimeline(ctx context.Context, model string, req workload.OperationRequest) (workload.OperationResult, error) {
	switch model {
	case workload.ModelMongoNested:
		return m.readNestedIncidentTimeline(ctx, req)
	case workload.ModelMongoNormalized:
		return m.readNormalizedIncidentTimeline(ctx, req)
	default:
		return workload.OperationResult{}, fmt.Errorf("unsupported MongoDB model: %s", model)
	}
}

func (m *MongoEngine) aggregate(ctx context.Context, collection *mongo.Collection, pipeline mongo.Pipeline) (workload.OperationResult, error) {
	cursor, err := collection.Aggregate(ctx, pipeline)
	if err != nil {
		return workload.OperationResult{}, err
	}
	defer func() {
		_ = cursor.Close(ctx)
	}()
	rows := 0
	bytes := 0
	for cursor.Next(ctx) {
		var doc bson.M
		if err := cursor.Decode(&doc); err != nil {
			return workload.OperationResult{}, err
		}
		rows++
		bytes += approxBytes(doc)
	}
	return workload.OperationResult{Rows: rows, Bytes: bytes}, cursor.Err()
}

func (m *MongoEngine) modelDB(model string) (*mongo.Database, []string, error) {
	switch model {
	case workload.ModelMongoNested:
		return m.Client.Database(m.NestedDatabase), nestedCollections, nil
	case workload.ModelMongoNormalized:
		return m.Client.Database(m.NormalizedDatabase), normalizedCollections, nil
	default:
		return nil, nil, fmt.Errorf("unsupported MongoDB model: %s", model)
	}
}

func replaceAll(ctx context.Context, collection *mongo.Collection, docs []any) error {
	if len(docs) == 0 {
		return nil
	}
	// DeleteMany keeps collection validators and indexes intact; Drop would erase schema objects.
	if _, err := collection.DeleteMany(ctx, bson.D{}); err != nil {
		return err
	}
	_, err := collection.InsertMany(ctx, docs)
	return err
}

func approxBytes(doc any) int {
	raw, err := bson.Marshal(doc)
	if err != nil {
		return len(fmt.Sprint(doc))
	}
	return len(raw)
}

func mongoWindow(now time.Time) (time.Time, time.Time) {
	return now.Add(-24 * time.Hour), now.Add(time.Hour)
}
