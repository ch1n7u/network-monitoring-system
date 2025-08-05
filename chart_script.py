import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Data from the provided JSON
data = [
    {"Component": "Zabbix Server", "Port": 80, "Protocol": "HTTP", "Purpose": "Web Interface", "Security": "Basic Auth + SSL"},
    {"Component": "Zabbix Server", "Port": 10051, "Protocol": "TCP", "Purpose": "Server Communication", "Security": "TLS Encryption"},
    {"Component": "Zabbix Agent", "Port": 10050, "Protocol": "TCP", "Purpose": "Agent Communication", "Security": "PSK/TLS"},
    {"Component": "Prometheus", "Port": 9090, "Protocol": "HTTP", "Purpose": "Metrics Collection", "Security": "Basic Auth + SSL"},
    {"Component": "Grafana", "Port": 3000, "Protocol": "HTTP", "Purpose": "Dashboard Interface", "Security": "User Auth + SSL"},
    {"Component": "Alertmanager", "Port": 9093, "Protocol": "HTTP", "Purpose": "Alert Management", "Security": "Basic Auth + SSL"},
    {"Component": "Node Exporter", "Port": 9100, "Protocol": "HTTP", "Purpose": "System Metrics", "Security": "Firewall Restricted"},
    {"Component": "SNMP Exporter", "Port": 9116, "Protocol": "HTTP", "Purpose": "Network Device Metrics", "Security": "Internal Only"},
    {"Component": "Blackbox Exporter", "Port": 9115, "Protocol": "HTTP", "Purpose": "HTTP/HTTPS Probes", "Security": "Internal Only"},
    {"Component": "MySQL/MariaDB", "Port": 3306, "Protocol": "TCP", "Purpose": "Database", "Security": "User Auth + SSL"}
]

df = pd.DataFrame(data)

# Define positions for components in a logical network flow
positions = {
    "Node Exporter": (1, 3),
    "SNMP Exporter": (1, 2),
    "Blackbox Exporter": (1, 1),
    "Zabbix Agent": (1, 4),
    "Prometheus": (3, 2.5),
    "Zabbix Server": (3, 4),
    "MySQL/MariaDB": (4, 4),
    "Grafana": (5, 3),
    "Alertmanager": (5, 2)
}

# Create unique components (handle Zabbix Server duplicates)
unique_components = df.groupby('Component').first().reset_index()

# Define component types for color coding
component_types = {
    "Node Exporter": "Exporter",
    "SNMP Exporter": "Exporter", 
    "Blackbox Exporter": "Exporter",
    "Zabbix Agent": "Agent",
    "Prometheus": "Collection",
    "Zabbix Server": "Server",
    "MySQL/MariaDB": "Database",
    "Grafana": "Visualization",
    "Alertmanager": "Alerting"
}

# Color mapping
colors = {
    "Exporter": "#1FB8CD",
    "Agent": "#DB4545", 
    "Collection": "#2E8B57",
    "Server": "#5D878F",
    "Database": "#D2BA4C",
    "Visualization": "#B4413C",
    "Alerting": "#964325"
}

# Create the figure
fig = go.Figure()

# Add connection lines
connections = [
    ("Node Exporter", "Prometheus"),
    ("SNMP Exporter", "Prometheus"),
    ("Blackbox Exporter", "Prometheus"),
    ("Zabbix Agent", "Zabbix Server"),
    ("Zabbix Server", "MySQL/MariaDB"),
    ("Prometheus", "Grafana"),
    ("Prometheus", "Alertmanager"),
    ("Zabbix Server", "Grafana")
]

for start, end in connections:
    x_start, y_start = positions[start]
    x_end, y_end = positions[end]
    
    fig.add_trace(go.Scatter(
        x=[x_start, x_end],
        y=[y_start, y_end],
        mode='lines',
        line=dict(color='gray', width=2, dash='solid'),
        showlegend=False,
        hoverinfo='skip',
        cliponaxis=False
    ))

# Add component nodes
for _, row in unique_components.iterrows():
    component = row['Component']
    x, y = positions[component]
    comp_type = component_types[component]
    
    # Get all ports for this component
    component_data = df[df['Component'] == component]
    ports_info = []
    for _, comp_row in component_data.iterrows():
        ports_info.append(f"Port {comp_row['Port']} ({comp_row['Protocol']})")
    
    hover_text = f"<b>{component}</b><br>" + \
                f"Type: {comp_type}<br>" + \
                f"Ports: {', '.join(ports_info)}<br>" + \
                f"Security: {row['Security']}"
    
    fig.add_trace(go.Scatter(
        x=[x],
        y=[y],
        mode='markers+text',
        marker=dict(
            size=40,
            color=colors[comp_type],
            line=dict(width=2, color='white')
        ),
        text=component.replace(' ', '<br>'),
        textposition='middle center',
        textfont=dict(size=10, color='white'),
        name=comp_type,
        hovertext=hover_text,
        hoverinfo='text',
        showlegend=True if component == list(component_types.keys())[list(component_types.values()).index(comp_type)] else False,
        cliponaxis=False
    ))

# Update layout
fig.update_layout(
    title="Network Monitor Architecture",
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        range=[0.5, 5.5]
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        range=[0.5, 4.5]
    ),
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.05,
        xanchor='center',
        x=0.5
    ),
    plot_bgcolor='white'
)

# Save the chart
fig.write_image("network_architecture.png")