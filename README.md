# Complete Network Monitoring System Setup Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Overview](#architecture-overview)
3. [Prerequisites](#prerequisites)
4. [Quick Start Installation](#quick-start-installation)
5. [Detailed Component Setup](#detailed-component-setup)
6. [Security Configuration](#security-configuration)
7. [Dashboard Setup](#dashboard-setup)
8. [Alert Configuration](#alert-configuration)
9. [Network Discovery](#network-discovery)
10. [Maintenance and Troubleshooting](#maintenance-and-troubleshooting)
11. [Best Practices](#best-practices)

## Project Overview

This comprehensive network monitoring system combines the power of **Zabbix**, **Prometheus**, **Grafana**, and other open-source tools to provide:

- ✅ **Auto-discovery** of network devices and hosts
- ✅ **Real-time monitoring** of CPU, RAM, Disk, Network metrics
- ✅ **Professional dashboards** with network topology overview
- ✅ **Multi-channel alerting** (Email, Telegram, Slack)
- ✅ **SSL/TLS security** with strong authentication
- ✅ **Exportable reports** (daily, weekly, monthly)
- ✅ **Easy deployment** on local servers or cloud VMs

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Grafana     │    │   Prometheus    │    │     Zabbix      │
│  (Dashboards)   │◄──►│  (Metrics DB)   │◄──►│  (Monitoring)   │
│     :3000       │    │     :9090       │    │     :80         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Alertmanager   │    │ Node Exporters  │    │ Network Devices │
│   (Alerts)      │    │ (System Stats)  │    │ (SNMP/Agents)   │
│     :9093       │    │     :9100       │    │   Various       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

### System Requirements
- **OS**: Ubuntu 22.04/24.04, Debian 11/12, or CentOS/RHEL 8+
- **RAM**: Minimum 4GB (8GB+ recommended for production)
- **Storage**: 20GB free space (SSD recommended)
- **Network**: Static IP address recommended
- **Ports**: 80, 443, 3000, 9090, 9093, 9100, 9115, 9116, 10050, 10051

### Software Dependencies
- Docker & Docker Compose
- Git (for configuration management)
- UFW or iptables (firewall)
- OpenSSL (for SSL certificates)

## Quick Start Installation

### Option 1: Automatic Installation (Recommended)

```bash
# Download and run the automated installer
curl -fsSL https://raw.githubusercontent.com/ch1n7u/network-monitoring-system/main/install.sh | bash

# Or download first and review
wget https://raw.githubusercontent.com/ch1n7u/network-monitoring-system/main/install.sh
chmod +x install.sh
./install.sh
```

### Option 2: Manual Installation

#### Step 1: System Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y curl wget apt-transport-https ca-certificates gnupg lsb-release

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Step 2: Download Project Files
```bash
# Create project directory
mkdir ~/network-monitoring && cd ~/network-monitoring

# Download configuration files (create these based on the guide)
# Files: docker-compose.yml, prometheus.yml, alertmanager.yml, etc.
```

#### Step 3: Configure Services
```bash
# Set up environment variables
cp .env.example .env
nano .env  # Edit with your settings

# Create necessary directories
mkdir -p grafana/provisioning/datasources
mkdir -p ssl
```

#### Step 4: Start Services
```bash
# Start the monitoring stack
docker-compose up -d

# Check status
docker-compose ps
```

## Detailed Component Setup

### Zabbix Server Installation

#### Ubuntu/Debian Installation
```bash
# Add Zabbix repository
wget https://repo.zabbix.com/zabbix/7.0/ubuntu/pool/main/z/zabbix-release/zabbix-release_7.0-2+ubuntu$(lsb_release -rs)_all.deb
sudo dpkg -i zabbix-release_7.0-2+ubuntu$(lsb_release -rs)_all.deb
sudo apt update

# Install Zabbix server, frontend, and agent
sudo apt install -y zabbix-server-mysql zabbix-frontend-php zabbix-apache-conf zabbix-sql-scripts zabbix-agent

# Install and configure MariaDB
sudo apt install -y mariadb-server
sudo mysql_secure_installation

# Create Zabbix database
sudo mysql -uroot -p
CREATE DATABASE zabbix CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
CREATE USER 'zabbix'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON zabbix.* TO 'zabbix'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Import initial schema
sudo zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | mysql --default-character-set=utf8mb4 -uzabbix -p zabbix

# Configure Zabbix server
sudo nano /etc/zabbix/zabbix_server.conf
# Add: DBPassword=your_secure_password

# Start and enable services
sudo systemctl restart zabbix-server zabbix-agent apache2
sudo systemctl enable zabbix-server zabbix-agent apache2
```

#### Optimization for Production
```bash
# Edit Zabbix server configuration
sudo nano /etc/zabbix/zabbix_server.conf

# Add performance tuning parameters:
StartPollers=100
StartPollersUnreachable=50
StartPingers=50
StartTrappers=10
StartDiscoverers=10
StartHTTPPollers=10
CacheSize=128M
HistoryCacheSize=64M
HistoryIndexCacheSize=32M
TrendCacheSize=32M
ValueCacheSize=256M
```

### Prometheus Configuration

#### Basic prometheus.yml
```yaml
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
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: 
        - 'localhost:9100'
        - '192.168.1.10:9100'

  - job_name: 'snmp'
    static_configs:
      - targets:
        - 192.168.1.1  # Router
        - 192.168.1.2  # Switch
    metrics_path: /snmp
    params:
      module: [if_mib]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: localhost:9116
```

### Node Exporter Setup

#### Docker Deployment
```bash
docker run -d \
  --name=node-exporter \
  --restart=unless-stopped \
  -p 9100:9100 \
  -v "/proc:/host/proc:ro" \
  -v "/sys:/host/sys:ro" \
  -v "/:/rootfs:ro" \
  prom/node-exporter:latest \
  --path.procfs=/host/proc \
  --path.rootfs=/rootfs \
  --path.sysfs=/host/sys \
  --collector.filesystem.mount-points-exclude='^/(sys|proc|dev|host|etc)($$|/)'
```

#### System Service Installation
```bash
# Download Node Exporter
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-*-linux-amd64.tar.gz
tar xvf node_exporter-*-linux-amd64.tar.gz
sudo mv node_exporter-*-linux-amd64/node_exporter /usr/local/bin/

# Create system user
sudo useradd --no-create-home --shell /bin/false node_exporter

# Create systemd service
sudo tee /etc/systemd/system/node_exporter.service > /dev/null <<EOF
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

# Start and enable service
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl enable node_exporter
```

## Security Configuration

### SSL Certificate Setup

#### Self-Signed Certificates (Development)
```bash
# Create SSL directory
mkdir -p ssl && cd ssl

# Generate private key
openssl genrsa -out monitoring.key 2048

# Generate certificate
openssl req -new -x509 -key monitoring.key -out monitoring.crt -days 365 \
  -subj "/C=US/ST=State/L=City/O=YourOrg/CN=monitoring.local"
```

#### Let's Encrypt (Production)
```bash
# Install Certbot
sudo apt install -y certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/monitoring.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/monitoring.key
```

### Firewall Configuration
```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow monitoring services
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 3000/tcp  # Grafana
sudo ufw allow 9090/tcp  # Prometheus
sudo ufw allow 9093/tcp  # Alertmanager
sudo ufw allow 9100/tcp  # Node Exporter
sudo ufw allow 10050/tcp # Zabbix Agent
sudo ufw allow 10051/tcp # Zabbix Server

# Enable firewall
sudo ufw --force enable
```

### Strong Authentication

#### Grafana Security
```ini
# /etc/grafana/grafana.ini
[server]
protocol = https
cert_file = /etc/ssl/certs/monitoring.crt
cert_key = /etc/ssl/private/monitoring.key

[security]
admin_password = ${GRAFANA_ADMIN_PASSWORD}
disable_gravatar = true
cookie_secure = true
cookie_samesite = strict

[auth]
disable_login_form = false

[users]
allow_sign_up = false
allow_org_create = false
```

#### Environment Variables
```bash
# Create .env file
cat > .env << EOF
GRAFANA_ADMIN_PASSWORD=YourSecurePassword123!
SMTP_PASSWORD=your-smtp-app-password
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-chat-id
MYSQL_ROOT_PASSWORD=SecureRootPassword123!
ZABBIX_DB_PASSWORD=SecureZabbixPassword123!
EOF

# Secure the file
chmod 600 .env
```

## Dashboard Setup

### Grafana Dashboard Import

#### Popular Network Monitoring Dashboards
1. **Node Exporter Full** (ID: 1860)
2. **Network Interface Dashboard** (ID: 11953)
3. **SNMP Network Monitoring** (ID: 20265)
4. **Zabbix Dashboard** (ID: 19665)

#### Import Process
```bash
# Via Grafana UI:
# 1. Login to Grafana (http://your-server:3000)
# 2. Go to "+" → Import
# 3. Enter dashboard ID or upload JSON
# 4. Configure data source (Prometheus/Zabbix)

# Via API:
curl -X POST \
  http://admin:password@localhost:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @dashboard.json
```

### Custom Dashboard Creation

#### Network Topology Panel
```json
{
  "title": "Network Topology",
  "type": "graph",
  "targets": [
    {
      "expr": "up{job=\"node-exporter\"}",
      "legendFormat": "{{instance}}"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "custom": {
        "displayMode": "list",
        "placement": "bottom"
      }
    }
  }
}
```

## Alert Configuration

### Email Notifications

#### SMTP Configuration
```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'monitoring@yourcompany.com'
  smtp_auth_username: 'monitoring@yourcompany.com'
  smtp_auth_password: 'your-app-password'

receivers:
- name: 'email-alerts'
  email_configs:
  - to: 'admin@yourcompany.com'
    subject: 'Alert: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      Instance: {{ .Labels.instance }}
      Severity: {{ .Labels.severity }}
      Time: {{ .StartsAt }}
      {{ end }}
```

### Telegram Notifications

#### Bot Setup
```bash
# 1. Create bot with @BotFather on Telegram
# 2. Get bot token
# 3. Add bot to group and get chat ID

# Test bot
curl -X GET "https://api.telegram.org/bot<BOT_TOKEN>/getUpdates"
```

#### Alertmanager Configuration
```yaml
receivers:
- name: 'telegram-alerts'
  telegram_configs:
  - bot_token: 'YOUR_BOT_TOKEN'
    chat_id: YOUR_CHAT_ID
    message: |
      🚨 {{ .Status | toUpper }} Alert 🚨
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Instance: {{ .Labels.instance }}
      Severity: {{ .Labels.severity }}
      {{ end }}
```

### Alert Rules Examples

#### Critical System Alerts
```yaml
groups:
- name: system_alerts
  rules:
  - alert: InstanceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Instance {{ $labels.instance }} is down"

  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage on {{ $labels.instance }}"

  - alert: LowDiskSpace
    expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 10
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Low disk space on {{ $labels.instance }}"
```

## Network Discovery

### Zabbix Auto-Discovery

#### Discovery Rules Configuration
```json
{
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
      "type": "Zabbix_agent",
      "port": "10050"
    },
    {
      "type": "ICMP_ping"
    }
  ]
}
```

#### Discovery Actions
```bash
# Via Zabbix Web UI:
# 1. Configuration → Actions → Discovery actions
# 2. Create action with conditions:
#    - Discovery rule equals "Network Auto Discovery"
#    - Received value contains "Linux"
# 3. Operations:
#    - Add host
#    - Add to group: "Linux servers"
#    - Link template: "Linux by Zabbix agent"
```

### Prometheus Service Discovery

#### File-based Discovery
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'file_sd'
    file_sd_configs:
      - files:
        - 'targets/*.yml'
        refresh_interval: 5m
```

```yaml
# targets/network.yml
- targets:
  - '192.168.1.10:9100'
  - '192.168.1.11:9100'
  labels:
    environment: 'production'
    team: 'infrastructure'
```

## Exportable Reports

### Grafana Report Generation

#### PDF Reports
```bash
# Install Grafana Image Renderer
docker run -d \
  --name=grafana-image-renderer \
  --restart=unless-stopped \
  -p 8081:8081 \
  grafana/grafana-image-renderer:latest

# Configure Grafana
# Add to grafana.ini:
[rendering]
server_url = http://grafana-image-renderer:8081/render
callback_url = http://grafana:3000/
```

#### Automated Reports
```bash
#!/bin/bash
# weekly_report.sh

GRAFANA_URL="https://your-grafana-instance.com"
API_KEY="your-api-key"
DASHBOARD_UID="dashboard-uid"

# Generate PDF report
curl -H "Authorization: Bearer $API_KEY" \
  "$GRAFANA_URL/render/d-solo/$DASHBOARD_UID?orgId=1&from=now-7d&to=now&panelId=1&width=1000&height=500&tz=UTC" \
  -o "weekly_report_$(date +%Y%m%d).pdf"

# Email report
echo "Weekly monitoring report attached" | \
  mail -s "Weekly Network Report" -a "weekly_report_$(date +%Y%m%d).pdf" admin@company.com
```

### Zabbix Reports

#### Custom Report Scripts
```bash
#!/bin/bash
# zabbix_report.sh

ZABBIX_URL="http://your-zabbix-server/zabbix"
USERNAME="admin"
PASSWORD="password"

# Login and get auth token
AUTH_TOKEN=$(curl -s -X POST "$ZABBIX_URL/api_jsonrpc.php" \
  -H "Content-Type: application/json-rpc" \
  -d '{
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {
      "user": "'$USERNAME'",
      "password": "'$PASSWORD'"
    },
    "id": 1
  }' | jq -r .result)

# Get host availability data
curl -s -X POST "$ZABBIX_URL/api_jsonrpc.php" \
  -H "Content-Type: application/json-rpc" \
  -d '{
    "jsonrpc": "2.0",
    "method": "host.get",
    "params": {
      "output": ["hostid", "host", "status", "available"],
      "selectInterfaces": ["ip"]
    },
    "auth": "'$AUTH_TOKEN'",
    "id": 1
  }' | jq . > daily_host_status.json
```

## Maintenance and Troubleshooting

### Regular Maintenance Tasks

#### Weekly Tasks
```bash
#!/bin/bash
# weekly_maintenance.sh

# Update Docker images
docker-compose pull
docker-compose up -d

# Clean up old data
docker system prune -f

# Backup configurations
tar -czf backup_$(date +%Y%m%d).tar.gz \
  prometheus.yml alertmanager.yml docker-compose.yml .env

# Check disk space
df -h | grep -E "/(|var|tmp)" | awk '$5 > 80 {print "Warning: " $0}'

# Restart services if needed
if [ $(docker ps --filter "status=exited" -q | wc -l) -gt 0 ]; then
  echo "Restarting failed containers..."
  docker-compose restart
fi
```

#### Monthly Tasks
```bash
#!/bin/bash
# monthly_maintenance.sh

# Update system packages
sudo apt update && sudo apt upgrade -y

# Rotate logs
sudo logrotate -f /etc/logrotate.conf

# Update SSL certificates (if using Let's Encrypt)
sudo certbot renew --quiet

# Database optimization (Zabbix)
mysql -uzabbix -p zabbix -e "OPTIMIZE TABLE history, trends, events;"

# Generate monthly report
./generate_monthly_report.sh
```

### Common Issues and Solutions

#### Service Not Starting
```bash
# Check logs
docker-compose logs service-name

# Check port conflicts
sudo netstat -tulpn | grep :9090

# Check firewall
sudo ufw status
```

#### High Memory Usage
```bash
# Monitor resource usage
docker stats

# Adjust memory limits in docker-compose.yml
services:
  prometheus:
    mem_limit: 2g
    mem_reservation: 1g
```

#### Database Connection Issues
```bash
# Check Zabbix database connection
sudo mysql -uzabbix -p -e "SELECT VERSION();"

# Check database size
sudo mysql -uzabbix -p -e "
SELECT 
  table_schema AS 'Database',
  ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'zabbix'
GROUP BY table_schema;"
```

## Best Practices

### Performance Optimization

#### Prometheus
- Use recording rules for frequently queried metrics
- Configure appropriate retention periods
- Use remote storage for long-term data
- Optimize scrape intervals based on requirements

#### Zabbix
- Use active agents instead of passive where possible
- Configure housekeeping to remove old data
- Use database partitioning for large installations
- Optimize trigger expressions

#### Grafana
- Use dashboard variables for dynamic filtering
- Cache dashboard results
- Optimize panel queries
- Use appropriate time ranges

### Security Best Practices

1. **Change Default Passwords**: Always change default credentials
2. **Use HTTPS**: Encrypt all web traffic
3. **Network Segmentation**: Isolate monitoring network
4. **Regular Updates**: Keep all components updated
5. **Access Control**: Implement role-based access
6. **Backup Strategy**: Regular backups of configurations and data
7. **Monitoring Logs**: Monitor access and error logs
8. **Certificate Management**: Automate SSL certificate renewal

### Scalability Considerations

#### Horizontal Scaling
- Use Prometheus federation for multi-site monitoring
- Deploy Zabbix proxies for remote locations
- Implement load balancing for Grafana
- Use external databases for better performance

#### Vertical Scaling
- Add more CPU/RAM as monitoring scope increases
- Use SSD storage for better I/O performance
- Optimize database configuration
- Monitor resource usage and plan capacity

### Backup and Recovery

#### Configuration Backup
```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR="/backup/monitoring/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup configuration files
cp -r prometheus.yml alertmanager.yml docker-compose.yml .env $BACKUP_DIR/

# Backup Grafana dashboards
curl -H "Authorization: Bearer $GRAFANA_API_KEY" \
  "$GRAFANA_URL/api/search?type=dash-db" | \
  jq -r '.[].uri' | \
  while read uri; do
    curl -H "Authorization: Bearer $GRAFANA_API_KEY" \
      "$GRAFANA_URL/api/dashboards/$uri" > "$BACKUP_DIR/dashboard_$(basename $uri).json"
  done

# Backup Zabbix configuration
mysqldump -uzabbix -p$ZABBIX_DB_PASSWORD --single-transaction \
  zabbix hosts groups templates items triggers > $BACKUP_DIR/zabbix_config.sql
```

#### Data Backup
```bash
#!/bin/bash
# backup_data.sh

# Backup Prometheus data
docker run --rm -v prometheus_data:/data -v /backup:/backup \
  alpine tar czf /backup/prometheus_$(date +%Y%m%d).tar.gz -C /data .

# Backup Grafana data
docker run --rm -v grafana_data:/data -v /backup:/backup \
  alpine tar czf /backup/grafana_$(date +%Y%m%d).tar.gz -C /data .
```

### Documentation and Change Management

1. **Document Changes**: Keep a changelog of all modifications
2. **Version Control**: Use Git for configuration management
3. **Testing**: Test changes in a staging environment
4. **Rollback Plan**: Always have a rollback strategy
5. **Team Training**: Ensure team knows how to use the system

## Conclusion

This comprehensive network monitoring system provides:

- **Complete visibility** into your network infrastructure
- **Professional-grade monitoring** using industry-standard tools
- **Robust alerting** to prevent downtime
- **Security-first approach** with SSL and strong authentication
- **Scalable architecture** that grows with your needs
- **Automation capabilities** for reduced maintenance overhead

The combination of Zabbix's powerful discovery features, Prometheus's flexible metrics collection, and Grafana's beautiful visualizations creates a monitoring solution that rivals expensive commercial alternatives while remaining completely free and open-source.

Remember to:
- Regularly update all components
- Monitor the monitoring system itself
- Backup configurations and data
- Train your team on system usage
- Document any customizations

With proper setup and maintenance, this system will provide reliable network monitoring for years to come.

---

*For additional support and updates, visit the project repository or contact the development team.*
