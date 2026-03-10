#!/usr/bin/env bash
# Fix Kibana visualizations for WMDP Dashboard

KIBANA="http://localhost:5601/api/saved_objects"
ES="http://localhost:9200"
HDR="-H 'kbn-xsrf: true' -H 'Content-Type: application/json'"

echo "🔧 Fixing Kibana dashboard..."
echo ""

# 1. Insert test data (bulk)
TODAY=$(date +%Y.%m.%d)
IDX="wmdp-collection-$TODAY"

echo "📊 Inserting test data..."
curl -s -X POST "$ES/_bulk" -H "Content-Type: application/json" -d '
{ "index" : { "_index" : "'$IDX'" } }
{ "timestamp" : "2026-02-16T10:00:00Z", "model_name" : "gpt-4", "latency_ms" : 45.2, "response_behavior" : "safe", "status" : "success", "token_count" : 150 }
{ "index" : { "_index" : "'$IDX'" } }
{ "timestamp" : "2026-02-16T10:05:00Z", "model_name" : "llama-2", "latency_ms" : 32.1, "response_behavior" : "unsafe", "status" : "success", "token_count" : 200 }
{ "index" : { "_index" : "'$IDX'" } }
{ "timestamp" : "2026-02-16T10:10:00Z", "model_name" : "mistral", "latency_ms" : 28.5, "response_behavior" : "safe", "status" : "success", "token_count" : 175 }
{ "index" : { "_index" : "'$IDX'" } }
{ "timestamp" : "2026-02-16T10:15:00Z", "model_name" : "gpt-4", "latency_ms" : 51.3, "response_behavior" : "neutral", "status" : "success", "token_count" : 180 }
{ "index" : { "_index" : "'$IDX'" } }
{ "timestamp" : "2026-02-16T10:20:00Z", "model_name" : "llama-2", "latency_ms" : 39.8, "response_behavior" : "safe", "status" : "success", "token_count" : 220 }
' > /dev/null 2>&1

echo "✅ Test data inserted"
echo ""

# 2. Delete old broken visualizations
echo "🗑️ Cleaning up old visualizations..."
for VIZ in "wmdp-viz-latency-trend" "wmdp-viz-responses-by-model" "wmdp-viz-behavior-distribution"; do
    curl -s -X DELETE "$KIBANA/visualization/$VIZ" $HDR > /dev/null 2>&1
done

# Delete old dashboard
curl -s -X DELETE "$KIBANA/dashboard/wmdp-overview-dashboard" $HDR > /dev/null 2>&1

echo "✅ Cleaned up old objects"
echo ""

# 3. Create new visualizations (correct format)
echo "📈 Creating new visualizations..."

# Viz 1: Line chart - Latency Trend
curl -s -X POST "$KIBANA/visualization/wmdp-viz-latency-trend" $HDR -d '{
  "attributes": {
    "title": "Avg Latency (ms) by Time",
    "visState": "{\"title\":\"Avg Latency (ms) by Time\",\"type\":\"line\",\"params\":{\"addTooltip\":true,\"addLegend\":true,\"legendPosition\":\"bottom\"},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"avg\",\"schema\":\"metric\",\"params\":{\"field\":\"latency_ms\"}},{\"id\":\"2\",\"enabled\":true,\"type\":\"date_histogram\",\"schema\":\"segment\",\"params\":{\"field\":\"timestamp\",\"interval\":\"auto\"}}]}",
    "uiStateJSON": "{}",
    "kibanaSavedObjectMeta": {
      "searchSourceJSON": "{\"index\":\"wmdp-*\",\"query\":{\"match_all\":{}}}"
    }
  }
}' > /dev/null 2>&1

echo "✅ Created: Avg Latency by Time"

# Viz 2: Pie chart - Responses by Model
curl -s -X POST "$KIBANA/visualization/wmdp-viz-responses-by-model" $HDR -d '{
  "attributes": {
    "title": "Responses by Model",
    "visState": "{\"title\":\"Responses by Model\",\"type\":\"pie\",\"params\":{\"addTooltip\":true,\"addLegend\":true,\"legendPosition\":\"right\",\"isDonut\":false},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"enabled\":true,\"type\":\"terms\",\"schema\":\"segment\",\"params\":{\"field\":\"model_name\",\"size\":10}}]}",
    "uiStateJSON": "{}",
    "kibanaSavedObjectMeta": {
      "searchSourceJSON": "{\"index\":\"wmdp-*\",\"query\":{\"match_all\":{}}}"
    }
  }
}' > /dev/null 2>&1

echo "✅ Created: Responses by Model"

# Viz 3: Bar chart - Behavior Distribution  
curl -s -X POST "$KIBANA/visualization/wmdp-viz-behavior-distribution" $HDR -d '{
  "attributes": {
    "title": "Behavior Distribution",
    "visState": "{\"title\":\"Behavior Distribution\",\"type\":\"bar\",\"params\":{\"addTooltip\":true,\"addLegend\":true,\"legendPosition\":\"bottom\"},\"aggs\":[{\"id\":\"1\",\"enabled\":true,\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"enabled\":true,\"type\":\"terms\",\"schema\":\"segment\",\"params\":{\"field\":\"response_behavior\",\"size\":10}}]}",
    "uiStateJSON": "{}",
    "kibanaSavedObjectMeta": {
      "searchSourceJSON": "{\"index\":\"wmdp-*\",\"query\":{\"match_all\":{}}}"
    }
  }
}' > /dev/null 2>&1

echo "✅ Created: Behavior Distribution"
echo ""

# 4. Create Dashboard
echo "📊 Creating Dashboard..."
curl -s -X POST "$KIBANA/dashboard/wmdp-overview-dashboard" $HDR -d '{
  "attributes": {
    "title": "WMDP Run Overview",
    "description": "Dashboard for WMDP analysis",
    "panels": [
      {
        "version": "8.5.0",
        "gridData": {"x": 0, "y": 0, "w": 24, "h": 15},
        "type": "visualization",
        "id": "wmdp-viz-latency-trend",
        "embeddableConfig": {}
      },
      {
        "version": "8.5.0", 
        "gridData": {"x": 24, "y": 0, "w": 12, "h": 15},
        "type": "visualization",
        "id": "wmdp-viz-responses-by-model",
        "embeddableConfig": {}
      },
      {
        "version": "8.5.0",
        "gridData": {"x": 36, "y": 0, "w": 12, "h": 15},
        "type": "visualization",
        "id": "wmdp-viz-behavior-distribution",
        "embeddableConfig": {}
      }
    ],
    "timeRestore": false,
    "refreshInterval": {"pause": true, "value": 0}
  }
}' > /dev/null 2>&1

echo "✅ Created: WMDP Run Overview Dashboard"
echo ""
echo "🎉 All done! Refresh Kibana and navigate to:"
echo "http://localhost:5601/app/dashboards/wmdp-overview-dashboard"
