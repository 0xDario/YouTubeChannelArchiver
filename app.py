import os
import uuid
import threading
from pathlib import Path

from flask import Flask, render_template, request, jsonify, send_file, abort

import yt_dlp

app = Flask(__name__)

DOWNLOAD_DIR = Path(__file__).resolve().parent / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Track ongoing downloads: task_id -> {status, progress, filepath, error}
downloads: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _search_youtube(query: str, max_results: int = 12) -> list[dict]:
    """Use yt-dlp to search YouTube and return video metadata."""
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "default_search": "ytsearch",
    }

    search_query = f"ytsearch{max_results}:{query}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)

    results = []
    for entry in info.get("entries", []):
        if entry is None:
            continue
        results.append({
            "id": entry.get("id"),
            "title": entry.get("title"),
            "url": entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}",
            "thumbnail": entry.get("thumbnails", [{}])[-1].get("url") if entry.get("thumbnails") else f"https://i.ytimg.com/vi/{entry.get('id')}/hqdefault.jpg",
            "duration": entry.get("duration"),
            "channel": entry.get("channel") or entry.get("uploader"),
            "view_count": entry.get("view_count"),
        })
    return results


def _format_duration(seconds) -> str:
    if seconds is None:
        return ""
    seconds = int(seconds)
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _progress_hook(task_id):
    """Return a yt-dlp progress hook that updates our downloads dict."""
    def hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            pct = (downloaded / total * 100) if total else 0
            downloads[task_id]["progress"] = round(pct, 1)
            downloads[task_id]["status"] = "downloading"
        elif d["status"] == "finished":
            downloads[task_id]["status"] = "processing"
            downloads[task_id]["progress"] = 100
    return hook


def _do_download(task_id: str, video_url: str, mode: str):
    """Run the actual download in a background thread."""
    task_dir = DOWNLOAD_DIR / task_id
    task_dir.mkdir(exist_ok=True)

    base_opts = {
        "outtmpl": str(task_dir / "%(title)s.%(ext)s"),
        "progress_hooks": [_progress_hook(task_id)],
        "noplaylist": True,
        "retries": 3,
        "quiet": True,
        "no_warnings": True,
    }

    if mode == "audio":
        base_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",  # best quality
            }],
        })
    else:
        base_opts.update({
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
        })

    try:
        with yt_dlp.YoutubeDL(base_opts) as ydl:
            ydl.download([video_url])

        # Find the downloaded file
        files = list(task_dir.iterdir())
        if files:
            downloads[task_id]["filepath"] = str(files[0])
            downloads[task_id]["filename"] = files[0].name
            downloads[task_id]["status"] = "done"
        else:
            downloads[task_id]["status"] = "error"
            downloads[task_id]["error"] = "No file was produced"
    except Exception as e:
        downloads[task_id]["status"] = "error"
        downloads[task_id]["error"] = str(e)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "No search query provided"}), 400

    try:
        results = _search_youtube(query)
        for r in results:
            r["duration_fmt"] = _format_duration(r.get("duration"))
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/download", methods=["POST"])
def api_download():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    video_url = data.get("url", "").strip()
    mode = data.get("mode", "video").strip()

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400
    if mode not in ("audio", "video"):
        return jsonify({"error": "Mode must be 'audio' or 'video'"}), 400

    # Basic URL validation
    if not (video_url.startswith("https://www.youtube.com/") or
            video_url.startswith("https://youtu.be/") or
            video_url.startswith("https://youtube.com/")):
        return jsonify({"error": "Invalid YouTube URL"}), 400

    task_id = uuid.uuid4().hex[:12]
    downloads[task_id] = {
        "status": "queued",
        "progress": 0,
        "filepath": None,
        "filename": None,
        "error": None,
    }

    thread = threading.Thread(target=_do_download, args=(task_id, video_url, mode), daemon=True)
    thread.start()

    return jsonify({"task_id": task_id})


@app.route("/api/download/<task_id>/status")
def api_download_status(task_id):
    task = downloads.get(task_id)
    if not task:
        return jsonify({"error": "Unknown task"}), 404
    return jsonify({
        "status": task["status"],
        "progress": task["progress"],
        "filename": task["filename"],
        "error": task["error"],
    })


@app.route("/api/download/<task_id>/file")
def api_download_file(task_id):
    task = downloads.get(task_id)
    if not task or task["status"] != "done":
        abort(404)

    filepath = task["filepath"]
    if not filepath or not os.path.isfile(filepath):
        abort(404)

    # Ensure file is within DOWNLOAD_DIR to prevent path traversal
    real_path = os.path.realpath(filepath)
    if not real_path.startswith(str(DOWNLOAD_DIR.resolve())):
        abort(403)

    return send_file(real_path, as_attachment=True, download_name=task["filename"])


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=8080)
