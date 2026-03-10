#!/usr/bin/env python3
"""Create dashboard with workaround for strict mapping"""
import urllib.request
import urllib.error
import json

KIBANA_API = "http://localhost:5601/api/saved_objects"

def make_request(method, path, data=None):
    url = f"{KIBANA_API}{path}"
    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json"
    }
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            return json.loads(error_body)
        except:
            return {"error": error_body}
    except Exception as e:
        return {"error": str(e)}

print("\n📊 Creating Dashboard with panels...\n")

# Create dashboard with minimal structure first
dashboard = {
    "attributes": {
        "title": "WMDP Run Overview",
        "description": "Dashboard for WMDP analysis"
    }
}

print("Creating empty dashboard...")
result = make_request("POST", "/dashboard/wmdp-overview-dashboard", dashboard)
if "error" not in result or "already exists" in str(result.get("error", "")):
    print("✅ Dashboard created (or already exists)")
    
    # Now try to add panels via update
    print("\nAdding panels to dashboard...")
    
    dashboard_with_panels = {
        "attributes": {
            "title": "WMDP Run Overview",
            "description": "Dashboard for WMDP analysis",
            "panels": [
                {
                    "version": "8.5.0",
                    "gridData": {"x": 0, "y": 0, "w": 24, "h": 15},
                    "type": "visualization",
                    "id": "wmdp-viz-latency-trend"
                },
                {
                    "version": "8.5.0",
                    "gridData": {"x": 24, "y": 0, "w": 12, "h": 15},
                    "type": "visualization",
                    "id": "wmdp-viz-responses-by-model"
                },
                {
                    "version": "8.5.0",
                    "gridData": {"x": 36, "y": 0, "w": 12, "h": 15},
                    "type": "visualization",
                    "id": "wmdp-viz-behavior-distribution"
                }
            ]
        }
    }
    
    result = make_request("PUT", "/dashboard/wmdp-overview-dashboard", dashboard_with_panels)
    
    if "error" not in result or "conflict" not in str(result.get("error", "")).lower():
        print("✅ Dashboard updated with panels")
    else:
        print(f"⚠️ Could not add panels: {result.get('error', 'Unknown')}")
        print("\n📝 Manual workaround: In Kibana, go to Dashboard and add visualizations manually")
        print("   Visualizations are created and ready to be added:")
        print("   - Latency Trend")
        print("   - Model Distribution")
        print("   - Behavior Analysis")
else:
    print(f"❌ Error: {result.get('error', 'Unknown')}")

print("\n🎉 Dashboard is available at:")
print("http://localhost:5601/app/dashboards/wmdp-overview-dashboard")
print("\n")
