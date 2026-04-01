# YouTube Downloader

A browser-based tool to search YouTube videos and download them as high-quality video (MP4) or audio (MP3).

![Python](https://img.shields.io/badge/Python-3.10+-blue)

## Features

- **Search YouTube** directly from the browser
- **Download video** in the best available quality (MP4)
- **Download audio** in the best available quality (MP3)
- Real-time download progress tracking
- Clean, dark-themed responsive UI

## Prerequisites

- **Python 3.10+**
- **ffmpeg** installed and available on your PATH
  - macOS: `brew install ffmpeg`
  - Windows: `winget install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

## Setup

```bash
# Clone the repo
git clone https://github.com/0xDario/YouTubeChannelArchiver.git
cd YouTubeChannelArchiver

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python app.py
```

Open **http://localhost:5000** in your browser, search for a video, and click **Video** or **Audio** to download.