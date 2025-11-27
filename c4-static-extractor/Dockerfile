FROM eclipse-temurin:17-jre

# Install git & unzip (needed for script)
RUN apt-get update && apt-get install -y git unzip && rm -rf /var/lib/apt/lists/*

# Download the static extractor (no compile required)
RUN git clone https://github.com/avasseur-cbo/structurizr-source-code-parser.git /tool

WORKDIR /tool

# Build a runnable fat-JAR from sources (only needs JRE)
RUN ./mvnw -q -DskipTests package

# Runtime entrypoint
ENTRYPOINT ["java", "-jar", "/tool/target/structurizr-source-code-parser.jar"]
