#!/usr/bin/env python3
"""
Create Kibana visualizations and dashboard using only stdlib
"""
import urllib.request
import urllib.error
import json
import sys

KIBANA_API = "http://localhost:5601/api/saved_objects"

def make_request(method, path, data=None):
    """Make HTTP request to Kibana"""
    url = f"{KIBANA_API}{path}"
    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }
    
    body = None
    if data:
        body = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            if content:
                return json.loads(content)
            return {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_json = json.loads(error_body)
            return {"error": error_json.get("message", str(e))}
        except:
            return {"error": error_body}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("\n🚀 Creating Kibana Visualizations and Dashboard...\n")
    
    # Visualization 1: Latency Trend
    print("1️⃣ Creating 'Latency Trend'...")
    viz1 = {
        "attributes": {
            "title": "Latency Trend",
            "visState": json.dumps({
                "title": "Latency Trend",
                "type": "line",
                "params": {
                    "addTooltip": True,
                    "addLegend": True,
                    "legendPosition": "bottom"
                },
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "avg",
                        "schema": "metric",
                        "params": {"field": "latency_ms"}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "date_histogram",
                        "schema": "segment",
                        "params": {"field": "timestamp", "interval": "auto"}
                    }
                ]
            }),
            "uiStateJSON": "{}",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": "wmdp-*",
                    "query": {"match_all": {}}
                })
            }
        }
    }
    
    result = make_request("POST", "/visualization/wmdp-viz-latency-trend", viz1)
    if "error" not in result:
        print("   ✅ Created")
    else:
        print(f"   ⚠️ {result.get('error', 'Unknown error')}")
    
    # Visualization 2: Model Distribution
    print("2️⃣ Creating 'Model Distribution'...")
    viz2 = {
        "attributes": {
            "title": "Model Distribution",
            "visState": json.dumps({
                "title": "Model Distribution",
                "type": "pie",
                "params": {
                    "addTooltip": True,
                    "addLegend": True,
                    "legendPosition": "right",
                    "isDonut": False
                },
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "terms",
                        "schema": "segment",
                        "params": {"field": "model_name", "size": 10}
                    }
                ]
            }),
            "uiStateJSON": "{}",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": "wmdp-*",
                    "query": {"match_all": {}}
                })
            }
        }
    }
    
    result = make_request("POST", "/visualization/wmdp-viz-responses-by-model", viz2)
    if "error" not in result:
        print("   ✅ Created")
    else:
        print(f"   ⚠️ {result.get('error', 'Unknown error')}")
    
    # Visualization 3: Behavior Analysis
    print("3️⃣ Creating 'Behavior Analysis'...")
    viz3 = {
        "attributes": {
            "title": "Behavior Analysis",
            "visState": json.dumps({
                "title": "Behavior Analysis",
                "type": "bar",
                "params": {
                    "addTooltip": True,
                    "addLegend": True,
                    "legendPosition": "bottom"
                },
                "aggs": [
                    {
                        "id": "1",
                        "enabled": True,
                        "type": "count",
                        "schema": "metric",
                        "params": {}
                    },
                    {
                        "id": "2",
                        "enabled": True,
                        "type": "terms",
                        "schema": "segment",
                        "params": {"field": "response_behavior", "size": 10}
                    }
                ]
            }),
            "uiStateJSON": "{}",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": "wmdp-*",
                    "query": {"match_all": {}}
                })
            }
        }
    }
    
    result = make_request("POST", "/visualization/wmdp-viz-behavior-distribution", viz3)
    if "error" not in result:
        print("   ✅ Created")
    else:
        print(f"   ⚠️ {result.get('error', 'Unknown error')}")
    
    # Create Dashboard
    print("4️⃣ Creating 'WMDP Run Overview' Dashboard...")
    dashboard = {
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
            "timeRestore": False,
            "refreshInterval": {"pause": True, "value": 0}
        }
    }
    
    result = make_request("POST", "/dashboard/wmdp-overview-dashboard", dashboard)
    if "error" not in result:
        print("   ✅ Created")
    else:
        print(f"   ⚠️ {result.get('error', 'Unknown error')}")
    
    print("\n🎉 Done!\n")
    print("Dashboard available at:")
    print("http://localhost:5601/app/dashboards/wmdp-overview-dashboard\n")

if __name__ == "__main__":
    main()
