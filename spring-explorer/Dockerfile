FROM eclipse-temurin:17-jdk

WORKDIR /app

RUN apt-get update && apt-get install -y wget unzip maven graphviz && \
    rm -rf /var/lib/apt/lists/*

# Correct download URL (branch = main)
RUN wget https://github.com/demoiselle/spring-explorer/archive/refs/heads/main.zip -O source.zip && \
    unzip source.zip && \
    rm source.zip && \
    mv spring-explorer-main/* . && \
    rm -rf spring-explorer-main

RUN mvn -q -DskipTests package

CMD [ "java", "-jar", "target/spring-explorer.jar" ]
