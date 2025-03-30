package main

import (
	"context"
	"log"

	firebase "firebase.google.com/go/v4"
	"firebase.google.com/go/v4/db"
	"google.golang.org/api/option"
)


func connectDB() *db.Ref {
	opt := option.WithCredentialsFile("key.json")
	config := &firebase.Config{ProjectID: "lab7-ff266", DatabaseURL: "https://lab7-ff266-default-rtdb.europe-west1.firebasedatabase.app/"}
	app, err := firebase.NewApp(context.Background(), config, opt)
	if err != nil {
		log.Fatalf("error initializing app: %v\n", err)
	}

	// Initialize a database client
	client, err := app.Database(context.Background())
	if err != nil {
		log.Fatalf("Error initializing database client: %v", err)
	}

	ref := client.NewRef("/")
	return ref
}

func clearDB(ref *db.Ref) {
	ref.Delete(context.Background())
}