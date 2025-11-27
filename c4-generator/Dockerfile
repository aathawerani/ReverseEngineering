FROM eclipse-temurin:17-jdk-jammy

# Install required tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    graphviz \
    git \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install structurizr-cli for C4 diagram generation
RUN curl -L https://github.com/structurizr/cli/releases/latest/download/structurizr-cli.zip -o /tmp/structurizr-cli.zip \
    && unzip /tmp/structurizr-cli.zip -d /opt/structurizr \
    && chmod +x /opt/structurizr/structurizr.sh \
    && rm /tmp/structurizr-cli.zip

# Install Python dependencies for code analysis
RUN pip3 install --no-cache-dir \
    javalang \
    pyyaml \
    jinja2

# Create working directories
WORKDIR /workspace
RUN mkdir -p /output

# Add structurizr to PATH
ENV PATH="/opt/structurizr:${PATH}"

# Copy the analysis script
COPY analyze_springboot.py /scripts/analyze_springboot.py

CMD ["/bin/bash"]