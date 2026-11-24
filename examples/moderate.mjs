// Node 18+. Usage: MUAPI_API_KEY=... node moderate.mjs "text" [imageUrl] [scene]
const BASE = "https://api.muapi.ai/api/v1";
const headers = { "x-api-key": process.env.MUAPI_API_KEY, "Content-Type": "application/json" };

export async function moderate({ text, imageUrl, scene = "social", timeoutMs = 60000 }) {
  if (!text && !imageUrl) throw new Error("Provide text, imageUrl, or both.");
  const body = { scene, ...(text && { text }), ...(imageUrl && { image_url: imageUrl }) };
  const submit = await fetch(`${BASE}/nsfw-moderation`, { method: "POST", headers, body: JSON.stringify(body) });
  if (!submit.ok) throw new Error(`submit failed: ${submit.status}`);
  const { request_id } = await submit.json();
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const res = await (await fetch(`${BASE}/predictions/${request_id}/result`, { headers })).json();
    if (res.status === "completed") return JSON.parse(res.outputs[0]);
    if (res.status === "failed") throw new Error(res.error || "moderation failed");
    await new Promise((r) => setTimeout(r, 1000));
  }
  throw new Error(`timed out waiting for ${request_id}`);
}

if (process.argv[1].endsWith("moderate.mjs")) {
  const [, , text, imageUrl, scene] = process.argv;
  const verdict = await moderate({ text, imageUrl, scene });
  console.log(JSON.stringify(verdict, null, 2));
  console.log(verdict.suggestion === "pass" ? "ALLOWED" : "BLOCKED");
}
