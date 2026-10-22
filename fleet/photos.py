"""Download three Commons photographs for each demo car.

Only CC0, CC BY, CC BY-SA, and public-domain files are kept. Titles must
name the requested model and the requested view. Nothing is substituted
from another model.
"""

import json
import re
import subprocess
import time
import urllib.parse
from io import BytesIO
from pathlib import Path

from PIL import Image

from fleet.data.vehicles import PHOTO_FILES, VEHICLES

USER_AGENT = "RentCarKomDjango/1.0 (local educational demo; vehicle catalog)"
COMMONS = "https://commons.wikimedia.org/w/api.php"
PHOTO_ROOT = Path(__file__).resolve().parent / "data" / "photos"
CREDITS_PATH = Path(__file__).resolve().parent / "data" / "photo_credits.json"

VIEW_WORDS = {
    "front": ("front", "quarter", "3/4", "three-quarter"),
    "rear": ("rear", "back", "side"),
    "interior": ("interior", "dashboard", "cockpit", "cabin"),
}
INTERIOR_WORDS = ("interior", "dashboard", "cockpit", "cabin", "inside")
NOT_A_CAR = (
    "logo",
    "emblem",
    "badge",
    "engine",
    "diagram",
    "map",
    "icon",
    "illustration",
    "drawing",
    "lego",
    "hot wheels",
    "diecast",
    "die-cast",
    "scale model",
    "toy ",
)


def photo_path(slug, view):
    return PHOTO_ROOT / slug / PHOTO_FILES[view]


def _license_ok(name):
    text = (name or "").lower()
    if any(flag in text for flag in ("nc", "nd", "non-commercial", "no derivatives")):
        return False
    return any(
        token in text
        for token in ("cc0", "cc by", "public domain", "pd")
    )


def _title_text(title):
    text = title.lower().replace("_", " ")
    if text.startswith("file:"):
        text = text[5:]
    return text


def _tokens_ok(title, vehicle):
    text = _title_text(title)
    for phrase in vehicle["reject"]:
        if phrase in text:
            return False
    if any(word in text for word in NOT_A_CAR):
        return False
    must = vehicle["must"]
    if vehicle.get("any_must"):
        return any(token in text for token in must)
    return all(token in text for token in must)


def _view_ok(title, view):
    text = _title_text(title)
    if view == "interior":
        return any(word in text for word in INTERIOR_WORDS)
    if view == "front":
        if any(word in text for word in ("rear", "back", "interior", "dashboard", "cockpit")):
            return False
        return True
    if any(word in text for word in ("interior", "dashboard", "cockpit")):
        return False
    return any(word in text for word in ("rear", "back", "side"))


def _score(title, view, width, year):
    text = _title_text(title)
    score = (width or 0) / 1000
    if any(word in text for word in VIEW_WORDS[view]):
        score += 5
    if any(word in text for word in ("police", "taxi", "ambulance", "carabinieri")):
        score -= 3
    years = [int(item) for item in re.findall(r"\b(?:19|20)\d{2}\b", text)]
    if years:
        gap = min(abs(item - year) for item in years)
        if gap <= 4:
            score += 6
        elif gap <= 8:
            score += 2
        else:
            score -= 6
    return score


def _get(url, drop_query=False):
    # The local Python build does not have a CA bundle. curl uses the system store.
    # Image CDN links can drop tracking parameters. The Commons API query must stay.
    if drop_query:
        url = url.split("?", 1)[0]
    last_error = None
    for _ in range(2):
        try:
            result = subprocess.run(
                [
                    "curl",
                    "-fsSL",
                    "--connect-timeout",
                    "10",
                    "--max-time",
                    "25",
                    "-A",
                    USER_AGENT,
                    url,
                ],
                check=True,
                capture_output=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as exc:
            last_error = exc
            time.sleep(1)
    raise last_error


def _search(query):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrnamespace": "6",
        "gsrlimit": "15",
        "gsrsearch": query,
        "prop": "imageinfo",
        "iiprop": "url|mime|size|extmetadata",
        "iiurlwidth": "1280",
        "iiextmetadatafilter": "LicenseShortName|Artist",
    }
    url = COMMONS + "?" + urllib.parse.urlencode(params)
    payload = json.loads(_get(url).decode("utf-8"))
    pages = (payload.get("query") or {}).get("pages") or {}
    found = []
    for page in pages.values():
        info = (page.get("imageinfo") or [None])[0]
        if not info:
            continue
        mime = info.get("mime") or ""
        if mime not in {"image/jpeg", "image/png", "image/webp"}:
            continue
        if (info.get("width") or 0) < 800:
            continue
        meta = info.get("extmetadata") or {}
        license_name = (meta.get("LicenseShortName") or {}).get("value") or ""
        if not _license_ok(license_name):
            continue
        image_url = info.get("thumburl") or info.get("url")
        if not image_url:
            continue
        artist = (meta.get("Artist") or {}).get("value") or ""
        found.append(
            {
                "title": page.get("title") or "",
                "pageid": page.get("pageid"),
                "url": image_url,
                "license": license_name,
                "artist": artist,
                "width": info.get("thumbwidth") or info.get("width") or 0,
            }
        )
    return found


def _queries(vehicle, view):
    name = f"{vehicle['brand']} {vehicle['model']}"
    if view == "front":
        return [f"{name} front", name]
    if view == "rear":
        return [f"{name} rear", f"{name} side"]
    return [f"{name} interior", f"{name} dashboard", f"{name} cockpit"]


def choose_photo(vehicle, view, used_ids):
    best = None
    best_score = None
    for query in _queries(vehicle, view):
        try:
            hits = _search(query)
        except Exception:
            time.sleep(1)
            continue
        time.sleep(0.35)
        for hit in hits:
            if hit["pageid"] in used_ids:
                continue
            if not _tokens_ok(hit["title"], vehicle):
                continue
            if not _view_ok(hit["title"], view):
                continue
            years = [int(item) for item in re.findall(r"\b(?:19|20)\d{2}\b", _title_text(hit["title"]))]
            # The first year in the title is the model year. Later years are usually the photo date.
            if years and abs(years[0] - vehicle["year"]) > 8:
                continue
            score = _score(hit["title"], view, hit["width"], vehicle["year"])
            if best_score is None or score > best_score:
                best = hit
                best_score = score
    return best


def _save_webp(raw, path):
    image = Image.open(BytesIO(raw))
    image = image.convert("RGB")
    image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "WEBP", quality=78, method=6)


def fetch_vehicle_photos(vehicle, used_ids, stdout=None):
    credits = []
    missing = []
    for view in ("front", "rear", "interior"):
        path = photo_path(vehicle["slug"], view)
        if path.exists() and path.stat().st_size > 1000:
            credits.append({"slug": vehicle["slug"], "view": view, "file": path.name, "cached": True})
            continue
        chosen = choose_photo(vehicle, view, used_ids)
        if chosen is None:
            missing.append(f"{vehicle['brand']} {vehicle['model']} ({view})")
            if stdout:
                stdout.write(f"  missing {vehicle['brand']} {vehicle['model']} {view}")
            continue
        try:
            raw = _get(chosen["url"], drop_query=True)
            _save_webp(raw, path)
        except Exception as exc:
            missing.append(f"{vehicle['brand']} {vehicle['model']} ({view}): {exc}")
            if stdout:
                stdout.write(f"  failed {vehicle['brand']} {vehicle['model']} {view}: {exc}")
            continue
        used_ids.add(chosen["pageid"])
        credits.append(
            {
                "slug": vehicle["slug"],
                "view": view,
                "file": str(path.relative_to(PHOTO_ROOT.parent.parent)),
                "title": chosen["title"],
                "license": chosen["license"],
                "artist": chosen["artist"],
                "source": chosen["url"],
            }
        )
        if stdout:
            stdout.write(f"  {view}: {chosen['title']} [{chosen['license']}]")
        time.sleep(0.2)
    return credits, missing


def fetch_all(stdout=None):
    used_ids = set()
    credits = []
    missing = []
    existing = []
    if CREDITS_PATH.exists():
        existing = json.loads(CREDITS_PATH.read_text(encoding="utf-8"))
    for vehicle in VEHICLES:
        if stdout:
            stdout.write(f"{vehicle['brand']} {vehicle['model']}")
        found, missed = fetch_vehicle_photos(vehicle, used_ids, stdout=stdout)
        credits.extend(found)
        missing.extend(missed)
    # Keep previously recorded attribution for cached files.
    by_key = {(item.get("slug"), item.get("view")): item for item in existing if not item.get("cached")}
    for item in credits:
        if item.get("cached"):
            previous = by_key.get((item["slug"], item["view"]))
            if previous:
                item.update(previous)
                item["cached"] = True
    CREDITS_PATH.write_text(json.dumps(credits, indent=2, ensure_ascii=False), encoding="utf-8")
    return credits, missing
