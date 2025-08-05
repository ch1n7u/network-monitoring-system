# Complete Network Monitoring System - Configuration Files

This directory contains all configuration files needed to deploy a professional network monitoring system using open-source tools.

## File Structure

```
network-monitoring/
├── docker-compose.yml              # Main orchestration file
├── prometheus.yml                  # Prometheus configuration
├── alertmanager.yml               # Alert routing configuration
├── alert_rules.yml               # Prometheus alert definitions
├── install.sh                    # Automated installation script
├── security_setup.sh             # Security configuration script
├── .env.example                  # Environment variables template
├── grafana/
│   └── provisioning/
│       └── datasources/
│           └── prometheus.yml    # Grafana datasource config
├── ssl/                          # SSL certificates directory
├── backups/                      # Configuration backups
└── scripts/                      # Utility scripts
    ├── backup.sh
    ├── maintenance.sh
    └── report_generator.sh
```

## Configuration Files

### 1. docker-compose.yml
Main orchestration file that defines all services including Prometheus, Grafana, Node Exporter, SNMP Exporter, Alertmanager, and supporting services.

### 2. prometheus.yml
Prometheus server configuration defining:
- Scrape targets (Node Exporter, SNMP devices, Blackbox probes)
- Alert rule files
- Alertmanager endpoints
- Global settings

### 3. alertmanager.yml
Alert routing and notification configuration:
- Email SMTP settings
- Telegram bot configuration
- Alert routing rules
- Notification templates

### 4. alert_rules.yml
Prometheus alert definitions:
- System alerts (CPU, Memory, Disk)
- Network alerts (Interface down, High latency)
- Service alerts (HTTP endpoints, SSL certificates)
- Custom business logic alerts

### 5. install.sh
Automated installation script that:
- Installs Docker and Docker Compose
- Configures system dependencies
- Sets up firewall rules
- Starts monitoring services
- Performs initial configuration

### 6. security_setup.sh
Security hardening script:
- Generates SSL certificates
- Configures HTTPS reverse proxy
- Sets up authentication
- Implements security best practices

## Quick Start

1. **Download the files:**
```bash
git clone https://github.com/your-repo/network-monitoring.git
cd network-monitoring
```

2. **Run the installer:**
```bash
chmod +x install.sh
./install.sh
```

3. **Configure security:**
```bash
chmod +x security_setup.sh
./security_setup.sh
```

4. **Access the interfaces:**
- Grafana: https://localhost:3000 (admin/admin123)
- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093

## Configuration Details

### Environment Variables (.env)
```bash
# Security
GRAFANA_ADMIN_PASSWORD=ChangeThisSecurePassword123!
SMTP_PASSWORD=your-smtp-app-password
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Database (if using external DB)
DB_PASSWORD=SecureDBPassword123!
MYSQL_ROOT_PASSWORD=SecureRootPassword123!
ZABBIX_DB_PASSWORD=SecureZabbixPassword123!

# SSL Configuration
SSL_CERT_PATH=/etc/ssl/certs/monitoring.crt
SSL_KEY_PATH=/etc/ssl/private/monitoring.key
```

### Prometheus Targets
Update `prometheus.yml` with your network devices:
```yaml
scrape_configs:
  - job_name: 'snmp'
    static_configs:
      - targets:
        - 192.168.1.1    # Your router
        - 192.168.1.2    # Your switch
        - 192.168.1.3    # Your firewall
```

### SNMP Configuration
For network device monitoring, ensure SNMP is enabled:
```bash
# Cisco IOS
snmp-server community public RO
snmp-server enable traps

# Linux
sudo apt install snmpd
sudo systemctl enable snmpd
```

### Grafana Dashboards
Import these popular dashboards by ID:
- **1860**: Node Exporter Full
- **11953**: Network Interface Dashboard  
- **20265**: SNMP Network Monitoring
- **19665**: Zabbix Dashboard

### Alert Channels
Configure multiple notification channels:

**Email Setup:**
1. Use Gmail with App Password
2. Enable 2FA on Gmail account
3. Generate App Password for monitoring
4. Update `alertmanager.yml` with credentials

**Telegram Setup:**
1. Create bot with @BotFather
2. Get bot token
3. Add bot to group chat
4. Get chat ID from API
5. Update configuration

### Network Discovery
For automatic device discovery:

**Zabbix Discovery:**
- IP Range: Configure your network subnet
- Check Types: SNMP, SSH, HTTP, ICMP
- Actions: Auto-add hosts with templates

**Prometheus Discovery:**
- File-based service discovery
- DNS-based discovery for cloud environments
- Kubernetes service discovery

## Security Considerations

### SSL/TLS Configuration
- Generate proper SSL certificates
- Use strong cipher suites
- Enable HSTS headers
- Implement certificate rotation

### Authentication
- Change all default passwords
- Use strong, unique passwords
- Enable 2FA where possible
- Implement role-based access control

### Network Security
- Configure firewall rules
- Use VPN for remote access
- Segment monitoring network
- Monitor access logs

### Data Protection
- Encrypt data at rest
- Secure backup storage
- Implement access controls
- Regular security audits

## Maintenance

### Regular Tasks
- **Daily**: Check service health, review alerts
- **Weekly**: Update Docker images, backup configs
- **Monthly**: System updates, certificate renewal
- **Quarterly**: Security audit, performance review

### Backup Strategy
```bash
# Configuration backup
./scripts/backup.sh

# Data backup
docker run --rm -v prometheus_data:/data -v /backup:/backup \
  alpine tar czf /backup/prometheus_$(date +%Y%m%d).tar.gz -C /data .
```

### Monitoring the Monitors
Set up monitoring for the monitoring system itself:
- Monitor service availability
- Track resource usage
- Alert on monitoring system issues
- Implement health checks

## Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check logs
docker-compose logs service-name

# Check port conflicts
sudo netstat -tulpn | grep :9090

# Restart services
docker-compose restart
```

**High resource usage:**
```bash
# Monitor resources
docker stats

# Adjust limits in docker-compose.yml
services:
  prometheus:
    mem_limit: 2g
```

**Network discovery not working:**
- Verify SNMP community strings
- Check firewall rules
- Ensure network connectivity
- Review discovery logs

### Performance Tuning

**Prometheus:**
- Adjust scrape intervals
- Use recording rules
- Configure retention
- Optimize queries

**Grafana:**
- Use dashboard variables
- Optimize panel queries
- Enable caching
- Use appropriate time ranges

## Support and Documentation

### Resources
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Zabbix Documentation](https://www.zabbix.com/documentation)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

### Community
- Stack Overflow tags: prometheus, grafana, zabbix
- Reddit communities: r/sysadmin, r/homelab
- Discord servers for each project

### Professional Support
For enterprise deployments:
- Grafana Labs Enterprise
- Zabbix Professional Services
- Third-party consultants

---

**Note:** This is a complete, production-ready monitoring solution. Customize the configurations according to your specific network requirements and security policies.