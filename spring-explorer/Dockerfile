FROM eclipse-temurin:17-jdk

# ------------------------------
# Base utilities and dependencies
# ------------------------------
RUN apt-get update && apt-get install -y \
    wget unzip git maven graphviz curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tools

# ------------------------------
# 1. Install Spring Explorer (static Spring Boot architecture)
# ------------------------------
RUN wget https://github.com/demoiselle/spring-explorer/archive/refs/heads/main.zip -O se.zip && \
    unzip se.zip && rm se.zip && \
    mv spring-explorer-main spring-explorer && \
    cd spring-explorer && mvn -q -DskipTests package

# ------------------------------
# 2. Install Structurizr CLI
# ------------------------------
RUN mkdir /tools/structurizr && \
    wget https://github.com/structurizr/cli/releases/latest/download/structurizr-cli.zip -O cli.zip && \
    unzip cli.zip -d /tools/structurizr && rm cli.zip

# ------------------------------
# 3. Install Structurizr Lite (local web UI)
# ------------------------------
RUN wget https://github.com/structurizr/lite/releases/latest/download/structurizr-lite.zip -O lite.zip && \
    unzip lite.zip -d /tools/structurizr/lite && rm lite.zip

# ------------------------------
# 4. Install PlantUML (jar)
# ------------------------------
RUN mkdir /tools/plantuml && \
    wget https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar -O /tools/plantuml/plantuml.jar

# ------------------------------
# 5. Install Mermaid CLI
# ------------------------------
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @mermaid-js/mermaid-cli

# ------------------------------
# 6. Set PATH shortcuts
# ------------------------------
ENV PATH="/tools/structurizr:${PATH}"
ENV PATH="/tools/spring-explorer:${PATH}"

# ------------------------------
# WORK DIRECTORY FOR USER CODE
# ------------------------------
WORKDIR /workspace

# ------------------------------
# Provide helper scripts
# ------------------------------
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
