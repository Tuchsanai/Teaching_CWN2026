# build context = ROOT (docker-compose.yml)
FROM pgvector/pgvector:pg16
ENV LANG=C.UTF-8
COPY db/init/*.sql /docker-entrypoint-initdb.d/
