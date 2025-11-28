# reveng-toolkit Dockerfile
FROM eclipse-temurin:17-jdk

# install basic tools and python
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    wget unzip curl graphviz python3 python3-venv python3-pip \
    nodejs npm git && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /tools

# install plantuml (jar)
RUN mkdir -p /tools/plantuml && \
    wget -q -O /tools/plantuml/plantuml.jar https://downloads.sourceforge.net/project/plantuml/plantuml.jar

# install Structurizr CLI (zip)
RUN mkdir -p /tools/structurizr && \
    curl -L -o /tools/structurizr/structurizr-cli.tar.gz \
        https://github.com/structurizr/cli/releases/download/v1.33.0/structurizr-cli-1.33.0.tar.gz && \
    apt-get update && apt-get install -y tar && \
    tar -xzf /tools/structurizr/structurizr-cli.tar.gz -C /tools/structurizr && \
    mv /tools/structurizr/structurizr-cli-1.33.0/structurizr-cli.jar /tools/structurizr/structurizr-cli.jar && \
    chmod +x /tools/structurizr/structurizr-cli.jar && \
    rm -rf /tools/structurizr/structurizr-cli.tar.gz /tools/structurizr/structurizr-cli-1.33.0

# install mermaid-cli (npm)
RUN npm install -g @mermaid-js/mermaid-cli

RUN apt-get update && apt-get install -y dos2unix

# copy local helper scripts into image
COPY analyzer.py /tools/analyzer.py
COPY entrypoint.sh /tools/entrypoint.sh
RUN find /tools -type f -exec dos2unix {} \;
RUN chmod +x /tools/entrypoint.sh /tools/analyzer.py

# default workdir (where user mount their repo)
WORKDIR /workspace

ENTRYPOINT ["/tools/entrypoint.sh"]
