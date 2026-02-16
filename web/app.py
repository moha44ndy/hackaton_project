from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime

ES_HOST = "http://localhost:9200"

app = Flask(__name__)


def get_collection_events(limit=20):
    try:
        url = f"{ES_HOST}/wmdp-collection-*/_search"
        body = {
            "query": {"match_all": {}},
            "size": limit,
            "sort": [{"timestamp": {"order": "desc"}}]
        }
        r = requests.post(url, json=body, timeout=10)
        r.raise_for_status()
        data = r.json()
        hits = data.get("hits", {}).get("hits", [])
        events = [h.get("_source", {}) for h in hits]
        return events
    except Exception as e:
        return {"error": str(e)}


@app.route("/", methods=["GET"])
def index():
    events = get_collection_events(limit=50)
    return render_template("index.html", events=events)


@app.route("/run-test", methods=["POST"]) 
def run_test():
    # Post a simple test document to today's collection index
    d = datetime.now().strftime("%Y.%m.%d")
    url = f"{ES_HOST}/wmdp-collection-{d}/_doc"
    doc = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "collection",
        "model_name": request.json.get("model_name", "web-test-model"),
        "prompt_id": request.json.get("prompt_id", "web-run"),
        "latency_ms": request.json.get("latency_ms", 0),
        "token_count": request.json.get("token_count", 0),
        "status": "success",
    }
    try:
        r = requests.post(url, json=doc, timeout=10)
        r.raise_for_status()
        return jsonify({"ok": True, "result": r.json()}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
