FROM eclipse-temurin:17-jdk

WORKDIR /app

RUN apt-get update && apt-get install -y wget unzip maven graphviz && \
    rm -rf /var/lib/apt/lists/*

# Download repo as ZIP instead of git clone
RUN wget https://github.com/demoiselle/spring-explorer/archive/refs/heads/master.zip -O source.zip && \
    unzip source.zip && \
    rm source.zip && \
    mv spring-explorer-master/* . && \
    rm -rf spring-explorer-master

RUN mvn -q -DskipTests package

CMD [ "java", "-jar", "target/spring-explorer.jar" ]
