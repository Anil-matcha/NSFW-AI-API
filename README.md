# NSFW AI API

Check text, an image, or both for NSFW content and get a `pass` or `block` verdict at the `adult`, `social` or `strict` level. One endpoint, a flat per-request price, and runnable `curl`, Python and JavaScript examples, including a script that gates an image-generation call behind a moderation check.

[Muapi NSFW AI API landing page](https://muapi.ai/nsfw-ai-api) · [Playground](https://muapi.ai/playground/nsfw-moderation) · [API reference](https://muapi.ai/docs/api-reference) · [Create an API key](https://muapi.ai/access-keys)

## Related Projects

- [Open-Generative-AI](https://github.com/Anil-matcha/Open-Generative-AI)
- [awesome-ai-image-models](https://github.com/Anil-matcha/awesome-ai-image-models)
- [muapi-cli](https://github.com/SamurAIGPT/muapi-cli)
- [Spicy-AI-Video-Generator-API](https://github.com/Anil-matcha/Spicy-AI-Video-Generator-API)
- [Spicy-AI-Image-Generator-API](https://github.com/Anil-matcha/Spicy-AI-Image-Generator-API)
- [awesome-uncensored-ai-models](https://github.com/Anil-matcha/awesome-uncensored-ai-models)

## Using it with spicy and uncensored models

Relaxed-moderation ("spicy") models are the main reason to put a moderation step in front of generation: you decide the policy, then enforce it with a `scene`. Use `adult` when your platform allows adult content (it still blocks sexual content involving minors), and `social` or `strict` for everything else. The same `suggestion` check works in front of any of these endpoints:

| Repository | What it covers |
|---|---|
| [Seedance-2.5-Spicy-API](https://github.com/Anil-matcha/Seedance-2.5-Spicy-API) | Seedance 2.5 relaxed-moderation video API |
| [Seedance-2-Spicy-API](https://github.com/Anil-matcha/Seedance-2-Spicy-API) | Seedance 2 text, image and reference-to-video |
| [Wan-3.0-Spicy-API](https://github.com/Anil-matcha/Wan-3.0-Spicy-API) | Wan 3.0 relaxed-moderation video API |
| [MiniMax-H3-Spicy-API](https://github.com/Anil-matcha/MiniMax-H3-Spicy-API) | MiniMax H3, H3 Max and H3 Max Turbo spicy endpoints |
| [Uncensored-AI-API](https://github.com/Anil-matcha/Uncensored-AI-API) | Abliterated LLM endpoints (check generated text with `text`) |
| [uncensored-ai-video-generator-comfyui](https://github.com/Anil-matcha/uncensored-ai-video-generator-comfyui) | Spicy video models in ComfyUI |
| [uncensored-ai-image-generator-comfyui](https://github.com/Anil-matcha/uncensored-ai-image-generator-comfyui) | Low-filter image models in ComfyUI |
| [awesome-uncensored-ai-video-models](https://github.com/Anil-matcha/awesome-uncensored-ai-video-models) | Catalog of uncensored video models |
| [awesome-uncensored-ai-image-models](https://github.com/Anil-matcha/awesome-uncensored-ai-image-models) | Catalog of low-filter image models |

Moderation does not make a model "safe" by itself; it is a policy check on what goes in and what comes out. Keep your own review process for anything your platform cannot allow.

## What it does

| | |
|---|---|
| Endpoint | `POST https://api.muapi.ai/api/v1/nsfw-moderation` |
| Input | `text`, `image_url`, or both (at least one) |
| Output | `suggestion` (`pass` / `block`), `nsfw_level`, `minor_risk`, per-text and per-image details |
| Price | $0.005 per request on Muapi, the same for text, image, both, and every scene |
| Contract | Asynchronous: submit, then poll or use a webhook |

### Request fields

| Field | Type | Notes |
|---|---|---|
| `text` | string | Up to 12,000 characters, any language. |
| `image_url` | string | One public image URL: JPG, PNG, WEBP or GIF, up to 20 MB and 50 megapixels. For animated images the first frame is reviewed. |
| `scene` | `adult` \| `social` \| `strict` | Default `social`. |
| `webhook_url` | string | Optional. Notified when the check completes. |

At least one of `text` or `image_url` is required. When both are sent they are reviewed together and billed once.

## Choosing a scene

| | `adult` | `social` (default) | `strict` |
|---|---|---|---|
| Best for | Platforms that allow adult content | General communities and apps | Workplace and family-safe products |
| Explicit / nude content | Allowed | Blocked | Blocked |
| Suggestive content | Allowed | Usually allowed | Blocked |
| Sexual content involving minors | Blocked | Blocked | Blocked |

Detected sexual content involving minors is blocked in every scene.

## Quick start

```bash
curl -X POST https://api.muapi.ai/api/v1/nsfw-moderation \
  -H "Content-Type: application/json" \
  -H "x-api-key: $MUAPI_API_KEY" \
  -d '{
    "text": "A golden retriever leaping to catch a red frisbee in a sunny city park",
    "image_url": "https://example.com/replace-with-your-image.jpg",
    "scene": "social"
  }'
# {"request_id": "REQUEST_ID", "status": "processing"}

curl "https://api.muapi.ai/api/v1/predictions/$REQUEST_ID/result" \
  -H "x-api-key: $MUAPI_API_KEY"
```

When the task is `completed`, `outputs[0]` is a JSON string with the verdict:

```json
{
  "suggestion": "pass",
  "nsfw_level": "none",
  "minor_risk": 0.0,
  "image_type": "realistic",
  "reasons": [],
  "other_categories": [],
  "details": {
    "text": {"nsfw_level": "none", "unsafe_score": 0.0005, "categories": [], "age_signals": []},
    "image": {"nsfw_level": "none", "unsafe_score": 0.0005, "categories": [], "faces": []}
  }
}
```

This is the upstream result shape; fields beyond `suggestion` may evolve. **Act on `suggestion` only**: `pass` to allow, `block` to reject. Levels, scores and reasons are for logging and display, not for fine-grained thresholds. `other_categories` (violence, weapons) are listed for reference and do not affect the verdict.

## Examples

| File | What it shows |
|---|---|
| [`examples/moderate.sh`](examples/moderate.sh) | Submit and poll with `curl`. |
| [`examples/moderate.py`](examples/moderate.py) | Python client (`requests`): `moderate(text=..., image_url=..., scene=...)`. |
| [`examples/moderate.mjs`](examples/moderate.mjs) | Node 18+ client using `fetch`. |
| [`examples/gate_generation.py`](examples/gate_generation.py) | Screen a prompt, run an image model only if it passes, then screen the output. |

```bash
export MUAPI_API_KEY=your_key
pip install requests
python examples/moderate.py "a cat on a sofa"
python examples/gate_generation.py "a cat on a sofa"
```

## Moderating video

Extract frames (for example one per second with `ffmpeg -i in.mp4 -vf fps=1 frame_%04d.jpg`), upload each frame somewhere publicly reachable, submit each as `image_url`, and treat the whole video as `block` if any frame is blocked. Each frame is one request.

## Errors and production notes

- Keep the API key in an environment variable; never commit it.
- The image must be downloadable without login. If it is not, the task fails with a message asking for a public URL, and the charge is refunded.
- When submitting in bulk, limit concurrency and retry failed tasks; a busy service fails the task rather than charging.
- Do not resubmit after a timeout without checking the original `request_id`; each submission is billable.
- Pricing and availability can change; confirm on the [landing page](https://muapi.ai/nsfw-ai-api).

## Status

These examples follow the endpoint schema on Muapi and have not been run against the production endpoint at the time of writing; check the landing page for current availability.

## License

MIT
