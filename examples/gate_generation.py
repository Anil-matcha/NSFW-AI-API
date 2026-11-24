"""Screen a prompt, generate an image only if it passes, then screen the output.

Usage: python gate_generation.py "a cat on a sofa"
The image model slug below is an example; any Muapi text-to-image endpoint works.
"""
import os
import sys
import time

import requests
from moderate import BASE, HEADERS, moderate

IMAGE_MODEL = "flux-schnell"


def generate(prompt, timeout=120):
    r = requests.post(f"{BASE}/{IMAGE_MODEL}", headers=HEADERS, json={"prompt": prompt}, timeout=30)
    r.raise_for_status()
    request_id = r.json()["request_id"]
    deadline = time.time() + timeout
    while time.time() < deadline:
        res = requests.get(f"{BASE}/predictions/{request_id}/result", headers=HEADERS, timeout=30).json()
        if res.get("status") == "completed":
            return res["outputs"][0]
        if res.get("status") == "failed":
            raise RuntimeError(res.get("error") or "generation failed")
        time.sleep(2)
    raise RuntimeError("generation timed out")


def main(prompt):
    if moderate(text=prompt, scene="social")["suggestion"] != "pass":
        print("Prompt blocked; nothing generated.")
        return 1
    image_url = generate(prompt)
    if moderate(image_url=image_url, scene="social")["suggestion"] != "pass":
        print("Generated image blocked; not shown.")
        return 1
    print("OK:", image_url)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
