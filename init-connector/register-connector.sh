#!/bin/sh

echo "Waiting for Kafka Connect to be ready..."

while [ "$(curl -s -o /dev/null -w %{http_code} http://connect:8083/connectors)" -ne 200 ]; do
  echo "Kafka Connect not ready yet, waiting 5 seconds..."
  sleep 5
done

echo "Kafka Connect is ready. Registering Debezium connector..."

# Prepare values from env
CONNECTOR_NAME="${CONNECTOR_NAME:-my-postgres-connector}"
POSTGRES_HOST="${POSTGRES_HOST:-my_postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-myuser}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-mypassword}"
POSTGRES_DB="${POSTGRES_DB:-mydatabase}"
SCHEMA_REGISTRY_HOST="${SCHEMA_REGISTRY_HOST:-schema-registry}"
SCHEMA_REGISTRY_PORT="${SCHEMA_REGISTRY_PORT:-8081}"
SCHEMA_REGISTRY_URL="http://${SCHEMA_REGISTRY_HOST}:${SCHEMA_REGISTRY_PORT}"

# Send connector config
response=$(curl -w "\nHTTP status: %{http_code}\n" -s -X POST http://connect:8083/connectors \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"${CONNECTOR_NAME}\",
    \"config\": {
      \"connector.class\": \"io.debezium.connector.postgresql.PostgresConnector\",
      \"database.hostname\": \"${POSTGRES_HOST}\",
      \"database.port\": \"${POSTGRES_PORT}\",
      \"database.user\": \"${POSTGRES_USER}\",
      \"database.password\": \"${POSTGRES_PASSWORD}\",
      \"database.dbname\": \"${POSTGRES_DB}\",
      \"database.server.name\": \"${POSTGRES_DB}\",
      \"topic.prefix\": \"${POSTGRES_DB}\",
      \"plugin.name\": \"pgoutput\",
      \"publication.autocreate.mode\": \"all_tables\",
      \"slot.name\": \"debezium_slot\",
      \"key.converter\": \"io.confluent.connect.avro.AvroConverter\",
      \"value.converter\": \"io.confluent.connect.avro.AvroConverter\",
      \"key.converter.schema.registry.url\": \"${SCHEMA_REGISTRY_URL}\",
      \"value.converter.schema.registry.url\": \"${SCHEMA_REGISTRY_URL}\"
    }
  }")

echo "Debezium connector registration response:"
echo "$response"