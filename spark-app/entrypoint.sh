#!/bin/bash

echo "✅ Spark-app container started. Waiting for the connector to be RUNNING..."

until curl -sf http://connect:8083/connectors/my-postgres-connector/status | grep RUNNING; do
    echo "⏳ Connector is not ready yet. Sleeping 5s..."
    sleep 5
done

echo "🎉 Connector is RUNNING. Waiting for schemas to be available..."

TOPICS=("customers" "products" "orders")
for topic in "${TOPICS[@]}"; do
    SCHEMA_URL="http://schema-registry:8081/subjects/mydatabase.public.${topic}-value/versions/latest"
    until curl -sf "$SCHEMA_URL"; do
        echo "⏳ Schema for mydatabase.public.${topic} not found yet. Sleeping 5s..."
        sleep 5
    done
    echo "✅ Schema for mydatabase.public.${topic} is ready."
done

echo "✅ Schemas are ready. Starting Spark job now..."

exec /opt/bitnami/spark/bin/spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-avro_2.12:3.3.0,io.delta:delta-core_2.12:2.4.0,io.delta:delta-storage:2.4.0,io.delta:delta-contribs_2.12:2.4.0 \
  --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
  --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" \
  --conf "spark.hadoop.fs.s3a.endpoint=http://minio:9000" \
  --conf "spark.hadoop.fs.s3a.access.key=minioadmin" \
  --conf "spark.hadoop.fs.s3a.secret.key=minioadmin123" \
  --conf "spark.hadoop.fs.s3a.path.style.access=true" \
  --conf "spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem" \
  /app/main.py