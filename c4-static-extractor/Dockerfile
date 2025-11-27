FROM eclipse-temurin:17-jdk

# Install git
RUN apt-get update && apt-get install -y git maven && rm -rf /var/lib/apt/lists/*

# Clone the official structurizr java repo
RUN git clone https://github.com/structurizr/java.git /tool

WORKDIR /tool

# Build only the analysis module (static code parser)
RUN mvn -q -DskipTests -pl structurizr-analysis -am package

# Runtime command
ENTRYPOINT ["java", "-cp", "/tool/structurizr-analysis/target/structurizr-analysis-*.jar", "com.structurizr.analysis.StructurizrAnalysis"]
