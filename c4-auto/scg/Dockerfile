FROM openjdk:17-jdk-slim

WORKDIR /app

# download SCG CLI release
RUN apt-get update && apt-get install -y wget unzip && rm -rf /var/lib/apt/lists/*

RUN wget -O scg.zip https://releases.jkcl.org/scg-cli-latest.zip \
    && unzip scg.zip \
    && rm scg.zip

ENTRYPOINT ["java", "-jar", "scg-cli.jar"]
