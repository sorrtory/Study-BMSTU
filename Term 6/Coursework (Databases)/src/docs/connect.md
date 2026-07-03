# Connection to CLI


## psql

```bash
docker exec -it coursework_postgres sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

## mongosh

```bash
docker exec -it coursework_mongo sh -lc 'mongosh -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin "$MONGO_INITDB_DATABASE"'
```


