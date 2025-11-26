FROM eclipse-temurin:17-jre-jammy

RUN apt-get update && apt-get install -y \
    wget \
    graphviz \
    python3 \
    python3-pip

RUN wget -O /plantuml.jar https://github.com/plantuml/plantuml/releases/download/v1.2023.12/plantuml-1.2023.12.jar

WORKDIR /workspace
COPY . /workspace

# Use the validated C4 generator
CMD ["python3", "validated-c4-diagrams.py"]