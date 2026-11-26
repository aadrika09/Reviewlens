"""Review analysis service (Google Gemini). Run: uvicorn main:app --port 8000"""
import json, os, re
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()  # reads GEMINI_API_KEY from fastapi-service/.env
app = FastAPI(title="ReviewLens Analysis Service")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

class Query(BaseModel):
    brand: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=120)
    requirement: str = Field(min_length=3, max_length=600)
    reason: str = Field(min_length=3, max_length=600)

PROMPT = """You are a product review analyst. Using real user and expert reviews of {brand} {name},
judge it against this buyer's need.
Requirement: {requirement}
Reason to buy: {reason}
Reply with ONLY valid JSON, no markdown:
{{"features":[{{"name":str,"score":0-100,"summary":"one sentence from reviews"}}] (5-7 features that matter for THIS buyer),
"pros":[str],"cons":[str],
"verdict":{{"decision":"buy"|"consider"|"skip","fit_score":0-100,"reason_fit":true|false,"explanation":"2-3 sentences tying reviews to the buyer's requirement and reason"}},
"source_note":"which sources were used"}}"""

def call(key: str, prompt: str, search: bool):
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    if search:
        body["tools"] = [{"google_search": {}}]
    r = httpx.post(URL, params={"key": key}, json=body, timeout=90)
    r.raise_for_status()
    parts = r.json()["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts)

@app.get("/")
def root():
    return health()

@app.get("/health")
def health():
    return {"ok": True, "version": "gemini-live", "gemini_key_loaded": bool(os.getenv("GEMINI_API_KEY"))}

@app.post("/analyze")
def analyze(q: Query):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise HTTPException(500, "GEMINI_API_KEY is not set. Put it in fastapi-service/.env and restart uvicorn.")
    prompt = PROMPT.format(**q.model_dump())
    try:
        try:
            text = call(key, prompt, search=True)      # grounded in live Google results
        except httpx.HTTPStatusError:
            text = call(key, prompt, search=False)     # free-tier fallback: model knowledge only
            note = " (Live search unavailable; based on the model's general knowledge.)"
        else:
            note = ""
        data = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
        data["source_note"] = data.get("source_note", "") + note
        return data
    except Exception as e:
        raise HTTPException(502, f"Analysis failed: {e}")


def wiki_image(q: str):
    r = httpx.get("https://en.wikipedia.org/w/api.php", timeout=10, headers={"User-Agent": "ReviewLens/1.0"},
                  params={"action": "query", "generator": "search", "gsrsearch": q, "gsrlimit": 1,
                          "prop": "pageimages", "piprop": "original", "format": "json"})
    for page in r.json().get("query", {}).get("pages", {}).values():
        if page.get("original"):
            return page["original"]["source"]

@app.get("/image")
def image(brand: str, name: str):
    """Finds a product photo on the web. Never fails: returns {"url": null} if nothing is found."""
    q = f"{brand} {name}".strip()
    try:
        from ddgs import DDGS
        hits = DDGS().images(f"{q} product", max_results=10) or []
        word = name.lower().split()[0] if name.strip() else ""
        ok = [h for h in hits if str(h.get("image", "")).lower().split("?")[0].endswith((".jpg", ".jpeg", ".png", ".webp"))
              and (h.get("width") or 0) >= 300]
        ok.sort(key=lambda h: word not in (str(h.get("title", "")) + str(h.get("image", ""))).lower())
        if ok:
            h = ok[0]
            return {"url": h["image"], "thumb": h.get("thumbnail"), "source": re.sub(r"^www\.", "", httpx.URL(h["image"]).host)}
    except Exception:
        pass
    try:
        u = wiki_image(q)
        if u:
            return {"url": u, "thumb": None, "source": "Wikipedia"}
    except Exception:
        pass
    return {"url": None, "thumb": None, "source": None}
