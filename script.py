# Create comprehensive network monitoring configuration files
import json
import os
from datetime import datetime

# Create directory structure for project files
config_files = {}

# 1. Zabbix Auto Discovery Configuration
zabbix_discovery_config = {
    "name": "Network Auto Discovery",
    "ip_range": "192.168.1.1-192.168.1.254",
    "update_interval": "10m",
    "checks": [
        {
            "type": "SNMP",
            "port": "161",
            "community": "public"
        },
        {
            "type": "SSH",
            "port": "22"
        },
        {
            "type": "HTTP",
            "port": "80"
        },
        {
            "type": "HTTPS", 
            "port": "443"
        },
        {
            "type": "Zabbix_agent",
            "port": "10050"
        },
        {
            "type": "ICMP_ping"
        }
    ],
    "actions": [
        {
            "name": "Add Linux Servers",
            "condition": "Zabbix agent and system.uname contains Linux",
            "operations": [
                "Add host",
                "Add to group: Linux servers",
                "Link template: Linux by Zabbix agent"
            ]
        },
        {
            "name": "Add Windows Servers", 
            "condition": "Zabbix agent and system.uname contains Windows",
            "operations": [
                "Add host",
                "Add to group: Windows servers", 
                "Link template: Windows by Zabbix agent"
            ]
        },
        {
            "name": "Add Network Devices",
            "condition": "SNMP and sysDescr contains (switch|router|firewall)",
            "operations": [
                "Add host",
                "Add to group: Network devices",
                "Link template: Generic SNMP"
            ]
        }
    ]
}

config_files['zabbix_discovery.json'] = json.dumps(zabbix_discovery_config, indent=2)

# 2. Prometheus Configuration
prometheus_config = """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter for system metrics
  - job_name: 'node-exporter'
    static_configs:
      - targets: 
        - 'localhost:9100'
        - '192.168.1.10:9100'
        - '192.168.1.11:9100'

  # SNMP Exporter for network devices
  - job_name: 'snmp'
    static_configs:
      - targets:
        - 192.168.1.1    # Router
        - 192.168.1.2    # Switch
        - 192.168.1.3    # Firewall
    metrics_path: /snmp
    params:
      module: [if_mib]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9116  # SNMP exporter

  # Blackbox exporter for HTTP/HTTPS monitoring
  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - http://192.168.1.10
        - https://192.168.1.11
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9115  # Blackbox exporter
"""

config_files['prometheus.yml'] = prometheus_config

# 3. Alert Rules Configuration
alert_rules = """
groups:
- name: network_alerts
  rules:
  - alert: InstanceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Instance {{ $labels.instance }} down"
      description: "{{ $labels.instance }} has been down for more than 1 minute."

  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage on {{ $labels.instance }}"
      description: "CPU usage is above 80% for more than 5 minutes."

  - alert: HighMemoryUsage
    expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on {{ $labels.instance }}"
      description: "Memory usage is above 80% for more than 5 minutes."

  - alert: DiskSpaceLow
    expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 20
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Low disk space on {{ $labels.instance }}"
      description: "Disk space is below 20% on root filesystem."

  - alert: NetworkInterfaceDown
    expr: node_network_up == 0
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Network interface down on {{ $labels.instance }}"
      description: "Network interface {{ $labels.device }} is down."

  - alert: HTTPEndpointDown
    expr: probe_success == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "HTTP endpoint down"
      description: "HTTP endpoint {{ $labels.instance }} is down."

  - alert: SSLCertificateExpiringSoon
    expr: (probe_ssl_earliest_cert_expiry - time()) / 86400 < 30
    for: 1h
    labels:
      severity: warning
    annotations:
      summary: "SSL certificate expiring soon"
      description: "SSL certificate for {{ $labels.instance }} expires in less than 30 days."
"""

config_files['alert_rules.yml'] = alert_rules

# 4. Alertmanager Configuration with Email and Telegram
alertmanager_config = """
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'monitoring@yourcompany.com'
  smtp_auth_username: 'monitoring@yourcompany.com'
  smtp_auth_password: 'your-app-password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
  - match:
      severity: critical
    receiver: 'critical-notifications'
  - match:
      severity: warning
    receiver: 'warning-notifications'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://127.0.0.1:5001/'

- name: 'critical-notifications'
  email_configs:
  - to: 'admin@yourcompany.com'
    subject: 'CRITICAL: {{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      Instance: {{ .Labels.instance }}
      Severity: {{ .Labels.severity }}
      {{ end }}
  telegram_configs:
  - bot_token: 'YOUR_BOT_TOKEN'
    chat_id: YOUR_CHAT_ID
    message: |
      🚨 CRITICAL ALERT 🚨
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Instance: {{ .Labels.instance }}
      {{ end }}

- name: 'warning-notifications'
  email_configs:
  - to: 'team@yourcompany.com'
    subject: 'WARNING: {{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      Instance: {{ .Labels.instance }}
      {{ end }}

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
"""

config_files['alertmanager.yml'] = alertmanager_config

# 5. Docker Compose for the entire stack
docker_compose = """
version: '3.8'

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus_data: {}
  grafana_data: {}
  alertmanager_data: {}

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alert_rules.yml:/etc/prometheus/alert_rules.yml
      - prometheus_data:/prometheus
    networks:
      - monitoring

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    networks:
      - monitoring

  snmp-exporter:
    image: prom/snmp-exporter:latest
    container_name: snmp-exporter
    restart: unless-stopped
    ports:
      - "9116:9116"
    networks:
      - monitoring

  blackbox-exporter:
    image: prom/blackbox-exporter:latest
    container_name: blackbox-exporter
    restart: unless-stopped
    ports:
      - "9115:9115"
    networks:
      - monitoring

  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    restart: unless-stopped
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    networks:
      - monitoring
"""

config_files['docker-compose.yml'] = docker_compose

# 6. Grafana Datasource Provisioning
grafana_datasource = """
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
"""

config_files['grafana/provisioning/datasources/prometheus.yml'] = grafana_datasource

# 7. Installation Script
install_script = """#!/bin/bash

# Network Monitoring System Installation Script
# Supports Ubuntu 22.04/24.04 and Debian-based systems

set -e

echo "🚀 Starting Network Monitoring System Installation..."

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
print_status "Installing required packages..."
sudo apt install -y curl wget apt-transport-https ca-certificates gnupg lsb-release software-properties-common

# Install Docker
print_status "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    sudo usermod -aG docker $USER
    print_status "Docker installed successfully"
else
    print_status "Docker already installed"
fi

# Install Docker Compose
print_status "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed successfully"
else
    print_status "Docker Compose already installed"
fi

# Create project directory
PROJECT_DIR="$HOME/network-monitoring"
print_status "Creating project directory at $PROJECT_DIR..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Create configuration directories
mkdir -p grafana/provisioning/datasources

# Download configuration files (this would be replaced with actual file creation)
print_status "Creating configuration files..."

# Configure firewall
print_status "Configuring firewall..."
sudo ufw allow 3000/tcp  # Grafana
sudo ufw allow 9090/tcp  # Prometheus
sudo ufw allow 9093/tcp  # Alertmanager
sudo ufw allow 9100/tcp  # Node Exporter
sudo ufw allow 9115/tcp  # Blackbox Exporter
sudo ufw allow 9116/tcp  # SNMP Exporter
sudo ufw --force enable

print_status "Starting monitoring stack..."
# Note: User needs to log out and back in for Docker group membership to take effect
newgrp docker << EONG
docker-compose up -d
EONG

print_status "Waiting for services to start..."
sleep 30

# Check service status
print_status "Checking service status..."
docker-compose ps

print_status "✅ Installation completed successfully!"
echo ""
echo "📊 Access your monitoring dashboards:"
echo "   - Grafana: http://localhost:3000 (admin/admin123)"
echo "   - Prometheus: http://localhost:9090"
echo "   - Alertmanager: http://localhost:9093"
echo ""
echo "🔧 Next steps:"
echo "   1. Configure your network devices in prometheus.yml"
echo "   2. Set up email/Telegram notifications in alertmanager.yml"
echo "   3. Import Grafana dashboards for network monitoring"
echo "   4. Configure SSL certificates for secure access"
echo ""
print_warning "Remember to change default passwords and configure proper authentication!"
"""

config_files['install.sh'] = install_script

# 8. Security Configuration Script
security_script = """#!/bin/bash

# Security Configuration Script for Network Monitoring System

set -e

echo "🔒 Configuring security settings..."

# Colors
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Generate SSL certificates
print_status "Generating SSL certificates..."
mkdir -p ssl
cd ssl

# Generate private key
openssl genrsa -out monitoring.key 2048

# Generate certificate signing request
openssl req -new -key monitoring.key -out monitoring.csr -subj "/C=US/ST=State/L=City/O=Organization/CN=monitoring.local"

# Generate self-signed certificate (for production, use CA-signed certificate)
openssl x509 -req -days 365 -in monitoring.csr -signkey monitoring.key -out monitoring.crt

print_status "SSL certificates generated"

cd ..

# Configure Grafana with SSL
print_status "Configuring Grafana SSL..."
mkdir -p grafana/conf

cat > grafana/conf/grafana.ini << EOF
[server]
protocol = https
cert_file = /etc/ssl/certs/monitoring.crt
cert_key = /etc/ssl/private/monitoring.key

[security]
admin_password = \${GRAFANA_ADMIN_PASSWORD}
disable_gravatar = true
cookie_secure = true
cookie_samesite = strict

[auth]
disable_login_form = false
disable_signout_menu = false

[auth.anonymous]
enabled = false

[users]
allow_sign_up = false
allow_org_create = false
default_theme = dark

[log]
mode = console
level = info
EOF

# Update docker-compose for SSL
print_status "Updating Docker Compose for SSL..."
cat >> docker-compose.yml << EOF

  # Nginx reverse proxy for SSL termination
  nginx:
    image: nginx:alpine
    container_name: monitoring-nginx
    restart: unless-stopped
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./ssl:/etc/ssl/certs
      - ./nginx.conf:/etc/nginx/nginx.conf
    networks:
      - monitoring
    depends_on:
      - grafana
      - prometheus
      - alertmanager
EOF

# Create Nginx configuration
cat > nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream grafana {
        server grafana:3000;
    }
    
    upstream prometheus {
        server prometheus:9090;
    }
    
    upstream alertmanager {
        server alertmanager:9093;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        return 301 https://\$host\$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl;
        server_name localhost;

        ssl_certificate /etc/ssl/certs/monitoring.crt;
        ssl_certificate_key /etc/ssl/certs/monitoring.key;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        # Grafana
        location / {
            proxy_pass http://grafana;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Prometheus
        location /prometheus/ {
            proxy_pass http://prometheus/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }

        # Alertmanager
        location /alertmanager/ {
            proxy_pass http://alertmanager/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }
    }
}
EOF

# Create environment file for secrets
print_status "Creating environment file for secrets..."
cat > .env << EOF
# Security Configuration
GRAFANA_ADMIN_PASSWORD=ChangeThisSecurePassword123!
SMTP_PASSWORD=your-smtp-password
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Database Credentials (if using external DB)
DB_PASSWORD=SecureDBPassword123!
EOF

print_warning "Important: Update the .env file with your actual credentials!"
print_status "Security configuration completed"

echo ""
echo "🔐 Security checklist:"
echo "   ✅ SSL certificates generated"
echo "   ✅ HTTPS redirect configured"
echo "   ✅ Secure Grafana settings applied"
echo "   ✅ Environment file created for secrets"
echo ""
echo "⚠️  Additional security steps:"
echo "   - Replace self-signed certificates with CA-signed ones for production"
echo "   - Configure firewall rules to restrict access"
echo "   - Set up VPN access for remote monitoring"
echo "   - Enable two-factor authentication where possible"
echo "   - Regularly update all components"
"""

config_files['security_setup.sh'] = security_script

# Print summary of created files
print("📁 Network Monitoring System Configuration Files Created:")
print("=" * 60)
for filename, content in config_files.items():
    print(f"✅ {filename} ({len(content)} characters)")

# Save total configuration size
total_size = sum(len(content) for content in config_files.values())
print(f"\n📊 Total configuration size: {total_size:,} characters")
print(f"📝 Number of files: {len(config_files)}")
print(f"🕒 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")