FROM eclipse-temurin:17-jdk

WORKDIR /app

RUN apt-get update && apt-get install -y wget unzip && rm -rf /var/lib/apt/lists/*

# download SCG CLI release (latest)
RUN wget -O scg.zip https://downloads.jkcl.org/scg-cli-latest.zip \
    && unzip scg.zip \
    && rm scg.zip

ENTRYPOINT ["java", "-jar", "scg-cli.jar"]
