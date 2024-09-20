FROM postgres:latest

# Set environment variables for Postgres
ENV POSTGRES_USER=user
ENV POSTGRES_PASSWORD=pass
ENV POSTGRES_DB=app

# Install the build dependencies
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    postgresql-server-dev-all \
    && rm -rf /var/lib/apt/lists/*

# Clone, build, and install the pgvector extension
RUN cd /tmp \
    && git clone --branch v0.6.0 https://github.com/pgvector/pgvector.git \
    && cd pgvector \
    && make \
    && make install