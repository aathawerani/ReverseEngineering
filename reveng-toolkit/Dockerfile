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

# install Structurizr CLI - CORRECTED INSTALLATION
RUN mkdir -p /tools/structurizr && \
    # Download the correct version (check latest from https://github.com/structurizr/cli/releases)
    curl -L -o /tools/structurizr/structurizr-cli.zip \
        https://github.com/structurizr/cli/releases/latest/download/structurizr-cli.zip && \
    unzip /tools/structurizr/structurizr-cli.zip -d /tools/structurizr && \
    # The CLI creates multiple files, find and make the main script executable
    find /tools/structurizr -name "structurizr*" -type f -exec chmod +x {} \; && \
    rm -f /tools/structurizr/structurizr-cli.zip

# Alternative Structurizr CLI installation if the above fails
# RUN mkdir -p /tools/structurizr && \
#     wget -q -O /tools/structurizr/structurizr-cli.jar \
#         https://github.com/structurizr/cli/releases/latest/download/structurizr-cli.jar && \
#     echo '#!/bin/bash\njava -jar /tools/structurizr/structurizr-cli.jar "$@"' > /tools/structurizr/structurizr-cli && \
#     chmod +x /tools/structurizr/structurizr-cli

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