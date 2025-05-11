FROM bitnami/spark:3.4.0

USER root

# Install curl (required by entrypoint.sh)
RUN install_packages curl

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy Spark application
COPY main.py /app/main.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Add required JARs for Delta Lake and S3 support
ADD https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.4.0/delta-core_2.12-2.4.0.jar /opt/bitnami/spark/jars/
ADD https://repo1.maven.org/maven2/io/delta/delta-storage/2.4.0/delta-storage-2.4.0.jar /opt/bitnami/spark/jars/
ADD https://repo1.maven.org/maven2/io/delta/delta-contribs_2.12/2.4.0/delta-contribs_2.12-2.4.0.jar /opt/bitnami/spark/jars/

ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.1/hadoop-aws-3.3.1.jar /opt/bitnami/spark/jars/
ADD https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.1026/aws-java-sdk-bundle-1.11.1026.jar /opt/bitnami/spark/jars/

ENTRYPOINT ["/entrypoint.sh"]
