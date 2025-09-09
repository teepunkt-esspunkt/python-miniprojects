import requests

A1111 = "http://127.0.0.1:7860"

def api_get(path):
    r = requests.get(f"{A1111}{path}", timeout=60)
    r.raise_for_status()
    return r.json()

def list_samplers():
    try:
        return [s["name"] for s in api_get("/sdapi/v1/samplers")]
    except Exception as e:
        print("Could not fetch samplers:", e)
        return []

def list_schedulers():
    try:
        data = api_get("/sdapi/v1/schedulers")
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return [d.get("label") or d.get("name") for d in data if (d.get("label") or d.get("name"))]
        return data if isinstance(data, list) else []
    except Exception as e:
        print("Could not fetch schedulers:", e)
        return []

samplers = list_samplers()
schedulers = list_schedulers()

print("\n--- Available samplers ---")
print(", ".join(samplers) if samplers else "(none)")

print("\n--- Available schedulers ---")
print(", ".join(schedulers) if schedulers else "(none)")
