"""Minimal Muapi NSFW Moderation client. Usage: python moderate.py "text" [image_url] [scene]"""
import json
import os
import sys
import time

import requests

BASE = "https://api.muapi.ai/api/v1"
HEADERS = {"x-api-key": os.environ["MUAPI_API_KEY"], "Content-Type": "application/json"}


def moderate(text=None, image_url=None, scene="social", timeout=60):
    """Return the verdict dict. Raises RuntimeError if the check fails or times out."""
    if not text and not image_url:
        raise ValueError("Provide text, image_url, or both.")
    body = {"scene": scene}
    if text:
        body["text"] = text
    if image_url:
        body["image_url"] = image_url
    r = requests.post(f"{BASE}/nsfw-moderation", headers=HEADERS, json=body, timeout=30)
    r.raise_for_status()
    request_id = r.json()["request_id"]
    deadline = time.time() + timeout
    while time.time() < deadline:
        res = requests.get(f"{BASE}/predictions/{request_id}/result", headers=HEADERS, timeout=30).json()
        if res.get("status") == "completed":
            return json.loads(res["outputs"][0])
        if res.get("status") == "failed":
            raise RuntimeError(res.get("error") or "moderation failed")
        time.sleep(1)
    raise RuntimeError(f"timed out waiting for {request_id}")


if __name__ == "__main__":
    verdict = moderate(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None, sys.argv[3] if len(sys.argv) > 3 else "social")
    print(json.dumps(verdict, indent=2))
    print("ALLOWED" if verdict["suggestion"] == "pass" else "BLOCKED")
