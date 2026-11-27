"""Lightweight Cloudinary signed upload helper using only the Python standard library."""
import base64
import hashlib
import json
import os
import time
import urllib.parse
import urllib.request
import uuid


def _cloudinary_config():
    url = (os.environ.get("CLOUDINARY_URL") or "").strip()
    if url.startswith("cloudinary://"):
        parsed = urllib.parse.urlparse(url)
        return {
            "cloud_name": parsed.hostname or "",
            "api_key": urllib.parse.unquote(parsed.username or ""),
            "api_secret": urllib.parse.unquote(parsed.password or ""),
        }
    return {
        "cloud_name": (os.environ.get("CLOUDINARY_CLOUD_NAME") or "").strip(),
        "api_key": (os.environ.get("CLOUDINARY_API_KEY") or "").strip(),
        "api_secret": (os.environ.get("CLOUDINARY_API_SECRET") or "").strip(),
    }


def is_configured() -> bool:
    cfg = _cloudinary_config()
    return bool(cfg["cloud_name"] and cfg["api_key"] and cfg["api_secret"])


def upload_image(file_bytes: bytes, filename: str = "upload.jpg", folder: str = "logistic-waves") -> dict:
    """Upload image bytes to Cloudinary and return {'ok': True, 'url': ...} or {'ok': False, 'error': ...}."""
    cfg = _cloudinary_config()
    if not (cfg["cloud_name"] and cfg["api_key"] and cfg["api_secret"]):
        return {
            "ok": False,
            "error": "Cloudinary is not fully configured (missing CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, or CLOUDINARY_API_SECRET).",
        }
    if not file_bytes:
        return {"ok": False, "error": "Empty file payload."}

    ts = str(int(time.time()))
    params_to_sign = f"folder={folder}&timestamp={ts}{cfg['api_secret']}"
    signature = hashlib.sha1(params_to_sign.encode("utf-8")).hexdigest()

    boundary = f"----LWBoundary{uuid.uuid4().hex}"
    parts = []
    for name, val in (
        ("api_key", cfg["api_key"]),
        ("timestamp", ts),
        ("folder", folder),
        ("signature", signature),
    ):
        parts.append(
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{val}\r\n".encode("utf-8")
        )

    safe_name = os.path.basename(filename or "upload.jpg").replace('"', "")
    parts.append(
        (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"file\"; filename=\"{safe_name}\"\r\n"
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode("utf-8")
        + file_bytes
        + f"\r\n--{boundary}--\r\n".encode("utf-8")
    )
    body = b"".join(parts)

    endpoint = f"https://api.cloudinary.com/v1_1/{cfg['cloud_name']}/image/upload"
    req = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {"ok": True, "url": data.get("secure_url") or data.get("url") or "", "public_id": data.get("public_id", "")}
    except Exception as ex:
        return {"ok": False, "error": str(ex)}


def upload_data_uri(data_uri: str, folder: str = "logistic-waves") -> dict:
    """Decode a base64 data:image/... URI and upload it to Cloudinary."""
    if not data_uri or ";base64," not in data_uri:
        return {"ok": False, "error": "Invalid image data URI."}
    header, b64 = data_uri.split(";base64,", 1)
    ext = "png" if "png" in header.lower() else ("webp" if "webp" in header.lower() else "jpg")
    try:
        raw = base64.b64decode(b64)
    except Exception as ex:
        return {"ok": False, "error": f"Base64 decode failed: {ex}"}
    return upload_image(raw, filename=f"receipt.{ext}", folder=folder)
