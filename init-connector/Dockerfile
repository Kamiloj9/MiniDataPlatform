FROM curlimages/curl:8.8.0

COPY register-connector.sh /register-connector.sh

USER root
RUN chmod +x /register-connector.sh

ENTRYPOINT ["/bin/sh", "/register-connector.sh"]
