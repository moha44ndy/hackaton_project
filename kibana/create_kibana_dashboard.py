#!/usr/bin/env python3
"""
Create Kibana visualizations and dashboard directly
"""
import requests
import json
import sys

KIBANA_API = "http://localhost:5601/api/saved_objects"

def create_visualization(vis_id, title, vis_state):
    """Create a visualization in Kibana"""
    url = f"{KIBANA_API}/visualization/{vis_id}"
    headers = {"kbn-xsrf": "true"}
    
    payload = {
        "attributes": {
            "title": title,
            "visState": json.dumps(vis_state),
            "uiStateJSON": "{}",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": "wmdp-*",
                    "query": {"match_all": {}}
                })
            }
        }
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        if r.status_code in [200, 201]:
            print(f"✅ Created visualization: {title}")
            return True
        else:
            print(f"❌ Failed to create {title}: {r.status_code} - {r.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error creating {title}: {e}")
        return False

def create_dashboard(panels):
    """Create dashboard with panels"""
    url = f"{KIBANA_API}/dashboard/wmdp-overview-dashboard"
    headers = {"kbn-xsrf": "true"}
    
    payload = {
        "attributes": {
            "title": "WMDP Run Overview",
            "description": "Dashboard for WMDP latency, model distribution, and behavior analysis",
            "panels": panels,
            "timeRestore": False,
            "timeFrom": "now-7d",
            "timeTo": "now",
            "refreshInterval": {"pause": True, "value": 0},
            "uiStateJSON": "{}",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({"query": {"match_all": {}}})
            }
        }
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        if r.status_code in [200, 201]:
            print(f"✅ Created dashboard: WMDP Run Overview")
            return True
        else:
            print(f"❌ Failed to create dashboard: {r.status_code}")
            print(f"   Response: {r.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")
        return False

def main():
    print("🚀 Creating Kibana visualizations and dashboard...\n")
    
    # Visualization 1: Avg Latency by Time
    viz1 = {
        "title": "Avg Latency (ms) by Time",
        "type": "line",
        "params": {
            "addTooltip": True,
            "addLegend": True,
            "legendPosition": "bottom"
        },
        "aggs": [
            {"id": "1", "enabled": True, "type": "avg", "schema": "metric", "params": {"field": "latency_ms"}},
            {"id": "2", "enabled": True, "type": "date_histogram", "schema": "segment", "params": {"field": "timestamp", "interval": "auto"}}
        ]
    }
    
    # Visualization 2: Responses by Model (Pie)
    viz2 = {
        "title": "Responses by Model",
        "type": "pie",
        "params": {
            "addTooltip": True,
            "addLegend": True,
            "legendPosition": "right",
            "isDonut": False
        },
        "aggs": [
            {"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}},
            {"id": "2", "enabled": True, "type": "terms", "schema": "segment", "params": {"field": "model_name", "size": 10}}
        ]
    }
    
    # Visualization 3: Behavior Distribution (Bar)
    viz3 = {
        "title": "Behavior Distribution",
        "type": "histogram",
        "params": {
            "addTooltip": True,
            "addLegend": True,
            "legendPosition": "bottom"
        },
        "aggs": [
            {"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}},
            {"id": "2", "enabled": True, "type": "terms", "schema": "segment", "params": {"field": "response_behavior", "size": 10}}
        ]
    }
    
    # Create visualizations
    success = True
    success &= create_visualization("wmdp-viz-latency-trend", "Avg Latency (ms) by Time", viz1)
    success &= create_visualization("wmdp-viz-responses-by-model", "Responses by Model", viz2)
    success &= create_visualization("wmdp-viz-behavior-distribution", "Behavior Distribution", viz3)
    
    if not success:
        print("\n⚠️  Some visualizations failed to create")
    
    # Create dashboard with panels
    print("\n📊 Creating dashboard...")
    panels = [
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
    ]
    
    if create_dashboard(panels):
        print(f"\n🎉 SUCCESS! Dashboard available at: http://localhost:5601/app/dashboards/wmdp-overview-dashboard")
    else:
        print("\n❌ Dashboard creation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
