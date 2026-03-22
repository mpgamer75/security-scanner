FROM kalilinux/kali-rolling:latest

LABEL maintainer="mpgamer75" \
      description="Security Scanner - Red Team Assessment Tool" \
      version="2.4.0"

# Avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    masscan \
    gobuster \
    sqlmap \
    whois \
    nikto \
    whatweb \
    dnsutils \
    openssl \
    curl \
    wget \
    git \
    python3 \
    python3-pip \
    netcat-traditional \
    enum4linux \
    smbclient \
    sslscan \
    hydra \
    golang-go \
    jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pinned Go tools
ENV GOPATH=/root/go
ENV PATH=$GOPATH/bin:$PATH

RUN go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@v2.6.6 2>/dev/null || true && \
    go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@v3.2.4 2>/dev/null || true && \
    go install github.com/tomnomnom/assetfinder@v0.1.1 2>/dev/null || true

# Install Python tools
RUN pip3 install wafw00f --break-system-packages 2>/dev/null || pip3 install wafw00f || true

# Create non-root user for running scans
RUN useradd -m -s /bin/bash scanner

# Set up working directory
WORKDIR /scanner

# Copy scanner files
COPY security /usr/local/bin/security
COPY html_generator.py /usr/local/bin/html_generator.py

# Make scripts executable
RUN chmod +x /usr/local/bin/security

# Set up output directory with correct permissions
RUN mkdir -p /scanner/output && chown scanner:scanner /scanner/output

# Set restrictive umask for output files
ENV UMASK=077

VOLUME ["/scanner/output"]

# Default entrypoint runs as root (nmap requires it for raw sockets)
ENTRYPOINT ["/usr/local/bin/security"]
CMD ["--help"]
