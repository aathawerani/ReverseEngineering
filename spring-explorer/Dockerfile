FROM eclipse-temurin:17-jdk

WORKDIR /app

RUN apt-get update && apt-get install -y git maven graphviz \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/demoiselle/spring-explorer.git .

RUN mvn -q -DskipTests package

ENTRYPOINT ["java", "-jar", "target/spring-explorer.jar"]
