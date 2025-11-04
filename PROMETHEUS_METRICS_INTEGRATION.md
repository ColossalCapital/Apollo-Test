# 📊 Prometheus Metrics Integration

## Overview

All AckwardRootsInc connectors expose Prometheus metrics on port **9091**. These metrics power the real-time data flow visualization in the Atlas IntegrationDetailScreen.

---

## 🎯 Metrics Architecture

```
AckwardRootsInc Connector (Rust)
    ↓ Exposes metrics on :9091
Prometheus (Scraper)
    ↓ Scrapes every 15s
Atlas Frontend
    ↓ Queries Prometheus API
Real-Time Visualization
```

---

## 📊 Connector Metrics (Port 9091)

### **AckwardRootsInc Connector Metrics**

Each connector exposes these metrics:

```rust
// Message metrics
connector_messages_sent_total{job="coinbase-connector",instance="connector-personal-coinbase:9091"}
connector_messages_sent_rate // Calculated: rate(connector_messages_sent_total[1m])

// WebSocket metrics
connector_websocket_connections{job="coinbase-connector",instance="connector-personal-coinbase:9091"}
connector_websocket_reconnects_total
connector_last_message_timestamp

// Kafka metrics
connector_kafka_messages_produced_total
connector_kafka_produce_errors_total

// Health metrics
connector_uptime_seconds
connector_health_status // 1 = healthy, 0 = unhealthy
```

### **Kafka Metrics**

```prometheus
# Queue size
kafka_log_log_size{topic="personal_exchange_ticks"}

# Consumer lag
kafka_consumer_lag{topic="personal_exchange_ticks"}

# Message rate
rate(kafka_messages_in_total{topic="personal_exchange_ticks"}[1m])
```

### **Apollo Metrics (Port 9092)**

```prometheus
# Processing metrics
apollo_messages_received_total{entity_id="personal",integration="coinbase"}
apollo_messages_processed_total{entity_id="personal",integration="coinbase"}
apollo_processing_latency_ms{entity_id="personal",integration="coinbase"}
apollo_entities_extracted_total{entity_id="personal",integration="coinbase"}
```

### **Atlas Metrics (Port 9093)**

```prometheus
# Storage metrics
atlas_entities_created_total{entity_id="personal",integration="coinbase"}
atlas_relationships_created_total{entity_id="personal",integration="coinbase"}
atlas_graph_updates_total{entity_id="personal",integration="coinbase"}
```

---

## 🔧 Implementation

### **1. Rust Connector (AckwardRootsInc)**

Add to `src/main.rs`:

```rust
use prometheus::{
    Counter, Gauge, Histogram, Registry, TextEncoder, Encoder
};
use warp::Filter;

// Define metrics
lazy_static! {
    static ref REGISTRY: Registry = Registry::new();
    
    static ref MESSAGES_SENT: Counter = Counter::new(
        "connector_messages_sent_total",
        "Total messages sent to Kafka"
    ).unwrap();
    
    static ref WS_CONNECTIONS: Gauge = Gauge::new(
        "connector_websocket_connections",
        "Current WebSocket connections"
    ).unwrap();
    
    static ref WS_RECONNECTS: Counter = Counter::new(
        "connector_websocket_reconnects_total",
        "Total WebSocket reconnections"
    ).unwrap();
    
    static ref LAST_MESSAGE_TIME: Gauge = Gauge::new(
        "connector_last_message_timestamp",
        "Timestamp of last message sent"
    ).unwrap();
    
    static ref KAFKA_PRODUCED: Counter = Counter::new(
        "connector_kafka_messages_produced_total",
        "Total messages produced to Kafka"
    ).unwrap();
    
    static ref KAFKA_ERRORS: Counter = Counter::new(
        "connector_kafka_produce_errors_total",
        "Total Kafka produce errors"
    ).unwrap();
}

// Register metrics
fn register_metrics() {
    REGISTRY.register(Box::new(MESSAGES_SENT.clone())).unwrap();
    REGISTRY.register(Box::new(WS_CONNECTIONS.clone())).unwrap();
    REGISTRY.register(Box::new(WS_RECONNECTS.clone())).unwrap();
    REGISTRY.register(Box::new(LAST_MESSAGE_TIME.clone())).unwrap();
    REGISTRY.register(Box::new(KAFKA_PRODUCED.clone())).unwrap();
    REGISTRY.register(Box::new(KAFKA_ERRORS.clone())).unwrap();
}

// Metrics endpoint
async fn metrics_handler() -> Result<impl warp::Reply, warp::Rejection> {
    let encoder = TextEncoder::new();
    let metric_families = REGISTRY.gather();
    let mut buffer = vec![];
    encoder.encode(&metric_families, &mut buffer).unwrap();
    Ok(String::from_utf8(buffer).unwrap())
}

// Start metrics server on port 9091
async fn start_metrics_server() {
    let metrics_route = warp::path("metrics")
        .and(warp::get())
        .and_then(metrics_handler);
    
    warp::serve(metrics_route)
        .run(([0, 0, 0, 0], 9091))
        .await;
}

// Update metrics in your code
async fn send_to_kafka(&self, message: &Message) -> Result<()> {
    match self.kafka.send(message).await {
        Ok(_) => {
            MESSAGES_SENT.inc();
            KAFKA_PRODUCED.inc();
            LAST_MESSAGE_TIME.set(chrono::Utc::now().timestamp() as f64);
        }
        Err(e) => {
            KAFKA_ERRORS.inc();
            return Err(e);
        }
    }
    Ok(())
}

async fn handle_websocket_connect(&self) {
    WS_CONNECTIONS.inc();
}

async fn handle_websocket_reconnect(&self) {
    WS_RECONNECTS.inc();
}
```

### **2. Prometheus Configuration**

Add to `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # AckwardRootsInc connectors
  - job_name: 'connectors'
    static_configs:
      - targets:
          - 'connector-personal-coinbase:9091'
          - 'connector-personal-binance:9091'
          - 'connector-personal-kraken:9091'
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
  
  # Apollo AI
  - job_name: 'apollo'
    static_configs:
      - targets: ['apollo:9092']
  
  # Atlas backend
  - job_name: 'atlas'
    static_configs:
      - targets: ['atlas:9093']
  
  # Kafka
  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka-exporter:9308']
```

### **3. Docker Compose**

Add Prometheus to your stack:

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    networks:
      - wtf-network

  # Kafka exporter for Kafka metrics
  kafka-exporter:
    image: danielqsj/kafka-exporter:latest
    container_name: kafka-exporter
    ports:
      - "9308:9308"
    command:
      - '--kafka.server=kafka:9092'
    networks:
      - wtf-network

volumes:
  prometheus-data:

networks:
  wtf-network:
    external: true
```

---

## 🎨 Frontend Integration

### **Usage in IntegrationDetailScreen**

```typescript
import { DataFlowVisualization } from '../components/DataFlowVisualization';

export default function IntegrationDetailScreen({ route }: any) {
  const { integrationId, entityId } = route.params;
  
  return (
    <ScrollView>
      {/* Existing content */}
      
      {/* Real-time data flow powered by Prometheus */}
      <DataFlowVisualization
        entityId={entityId}
        integrationType={integrationId}
      />
    </ScrollView>
  );
}
```

### **Prometheus Client**

```typescript
import { prometheusClient } from '../services/prometheusClient';

// Get connector metrics
const metrics = await prometheusClient.getConnectorMetrics('personal', 'coinbase');

// Get Kafka metrics
const kafka = await prometheusClient.getKafkaMetrics('personal');

// Get time-series data for charts
const timeSeries = await prometheusClient.getTimeSeriesData(
  'personal',
  'coinbase',
  'connector_messages_sent_total',
  60 // last 60 minutes
);
```

---

## 📊 Visualization

### **Data Flow Display**

```
┌─────────────────────────────────────────┐
│ 🔌 AckwardRootsInc                      │
│ Coinbase Connector                      │
│ Status: ✅ Streaming                    │
│ Messages/sec: 15.3                      │
│ Total sent: 1,234,567                   │
│ WebSocket: 🟢 Connected                 │
└─────────────────────────────────────────┘
              ↓ → → → (animated)
┌─────────────────────────────────────────┐
│ 📨 Kafka                                │
│ Message Broker                          │
│ Queue size: 1,234                       │
│ Messages/sec: 14.8                      │
│ Consumer lag: 23                        │
│ Topics: personal_exchange_*             │
└─────────────────────────────────────────┘
              ↓ → → → (animated)
┌─────────────────────────────────────────┐
│ 🤖 Apollo                               │
│ AI Processing                           │
│ Status: ✅ Processing                   │
│ Processed: 1,234,544                    │
│ Latency: 45ms                           │
│ Entities: 12,345                        │
└─────────────────────────────────────────┘
              ↓ → → → (animated)
┌─────────────────────────────────────────┐
│ 🌍 Atlas                                │
│ Knowledge Graph                         │
│ Status: ✅ Storing                      │
│ Entities: 12,345                        │
│ Relationships: 45,678                   │
│ Graph updates: 57,023                   │
└─────────────────────────────────────────┘

📈 Pipeline Summary
End-to-end latency: 95ms
Success rate: 100%
Last update: 6:44:23 PM
```

---

## 🚀 Benefits

### **1. Real-Time Visibility**
- See data flowing through the system
- Instant feedback on connector health
- Identify bottlenecks immediately

### **2. No Custom Metrics API**
- Use standard Prometheus
- Industry-standard monitoring
- Works with existing tools (Grafana, etc.)

### **3. Animated Visualization**
- Flowing arrows show active data transfer
- Color-coded status indicators
- Auto-refresh every 5 seconds

### **4. Historical Data**
- Query time-series data for charts
- Track trends over time
- Performance analysis

---

## 📈 Example Queries

### **Messages per second (last minute)**
```promql
rate(connector_messages_sent_total{job="coinbase-connector"}[1m])
```

### **Total messages sent**
```promql
connector_messages_sent_total{job="coinbase-connector"}
```

### **WebSocket connection status**
```promql
connector_websocket_connections{job="coinbase-connector"}
```

### **Kafka queue size**
```promql
kafka_log_log_size{topic=~"personal_exchange_.*"}
```

### **Apollo processing latency**
```promql
apollo_processing_latency_ms{entity_id="personal",integration="coinbase"}
```

### **Atlas entities created**
```promql
atlas_entities_created_total{entity_id="personal",integration="coinbase"}
```

---

## 🎯 Status

**100% COMPLETE!**

✅ Prometheus client (`prometheusClient.ts`)
✅ Data flow visualization component (`DataFlowVisualization.tsx`)
✅ Connector metrics specification
✅ Kafka metrics integration
✅ Apollo metrics integration
✅ Atlas metrics integration
✅ Animated real-time display
✅ Auto-refresh every 5 seconds

**The ultimate real-time data flow visualization powered by Prometheus!** 🚀
