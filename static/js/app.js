/* ── YouTube Downloader – Frontend Logic ─────────────────── */

const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search-input");
const searchBtn = document.getElementById("search-btn");
const searchLoading = document.getElementById("search-loading");
const searchError = document.getElementById("search-error");
const resultsGrid = document.getElementById("results");
const downloadsSection = document.getElementById("downloads-section");
const downloadsList = document.getElementById("downloads-list");

// ── Search ──────────────────────────────────────────────────

searchForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = searchInput.value.trim();
  if (!query) return;

  resultsGrid.innerHTML = "";
  searchError.classList.add("hidden");
  searchLoading.classList.remove("hidden");
  searchBtn.disabled = true;

  try {
    const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || "Search failed");
    }

    renderResults(data.results);
  } catch (err) {
    searchError.textContent = err.message;
    searchError.classList.remove("hidden");
  } finally {
    searchLoading.classList.add("hidden");
    searchBtn.disabled = false;
  }
});

// ── Render Results ──────────────────────────────────────────

function renderResults(results) {
  resultsGrid.innerHTML = "";

  if (!results.length) {
    resultsGrid.innerHTML =
      '<p style="text-align:center;color:#888;grid-column:1/-1;">No results found.</p>';
    return;
  }

  results.forEach((video) => {
    const card = document.createElement("div");
    card.className = "video-card";

    const thumbUrl =
      video.thumbnail || `https://i.ytimg.com/vi/${video.id}/hqdefault.jpg`;

    card.innerHTML = `
      <div class="thumb-wrap">
        <img src="${escapeAttr(thumbUrl)}" alt="${escapeAttr(video.title)}" loading="lazy" />
        ${video.duration_fmt ? `<span class="duration-badge">${escapeHtml(video.duration_fmt)}</span>` : ""}
      </div>
      <div class="card-body">
        <div class="card-title">${escapeHtml(video.title)}</div>
        ${video.channel ? `<div class="card-channel">${escapeHtml(video.channel)}</div>` : ""}
        <div class="card-actions">
          <button class="btn btn-video" data-url="${escapeAttr(video.url)}" data-title="${escapeAttr(video.title)}" data-mode="video">
            ▶ Video
          </button>
          <button class="btn btn-audio" data-url="${escapeAttr(video.url)}" data-title="${escapeAttr(video.title)}" data-mode="audio">
            ♫ Audio
          </button>
        </div>
      </div>`;

    // Attach download handlers
    card.querySelectorAll(".btn").forEach((btn) => {
      btn.addEventListener("click", () => startDownload(btn));
    });

    resultsGrid.appendChild(card);
  });
}

// ── Download ────────────────────────────────────────────────

async function startDownload(btn) {
  const url = btn.dataset.url;
  const mode = btn.dataset.mode;
  const title = btn.dataset.title;

  btn.disabled = true;
  btn.textContent = "Starting...";

  try {
    const res = await fetch("/api/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, mode }),
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Download failed");

    addDownloadTracker(data.task_id, title, mode);
  } catch (err) {
    alert("Download error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.textContent = mode === "audio" ? "♫ Audio" : "▶ Video";
  }
}

// ── Download Tracker ────────────────────────────────────────

function addDownloadTracker(taskId, title, mode) {
  downloadsSection.classList.remove("hidden");

  const item = document.createElement("div");
  item.className = "download-item";
  item.id = `dl-${taskId}`;

  item.innerHTML = `
    <div class="dl-info">
      <div class="dl-title">${escapeHtml(title)} (${mode})</div>
      <div class="dl-status">Queued...</div>
      <div class="progress-bar-wrap">
        <div class="progress-bar" style="width: 0%"></div>
      </div>
    </div>
    <div class="dl-action"></div>`;

  downloadsList.prepend(item);
  pollDownload(taskId);
}

async function pollDownload(taskId) {
  const item = document.getElementById(`dl-${taskId}`);
  if (!item) return;

  const statusEl = item.querySelector(".dl-status");
  const barEl = item.querySelector(".progress-bar");
  const actionEl = item.querySelector(".dl-action");

  const poll = async () => {
    try {
      const res = await fetch(`/api/download/${encodeURIComponent(taskId)}/status`);
      const data = await res.json();

      if (data.status === "downloading") {
        statusEl.textContent = `Downloading... ${data.progress}%`;
        barEl.style.width = `${data.progress}%`;
      } else if (data.status === "processing") {
        statusEl.textContent = "Processing...";
        barEl.style.width = "100%";
      } else if (data.status === "done") {
        statusEl.textContent = "Complete!";
        barEl.style.width = "100%";
        barEl.style.background = "#4caf50";
        actionEl.innerHTML = `<a class="btn btn-video" href="/api/download/${encodeURIComponent(taskId)}/file" style="display:inline-block;text-decoration:none;">Save</a>`;
        return; // stop polling
      } else if (data.status === "error") {
        statusEl.textContent = `Error: ${data.error}`;
        barEl.style.background = "#ff6b6b";
        return; // stop polling
      }

      setTimeout(poll, 1000);
    } catch {
      statusEl.textContent = "Connection lost. Retrying...";
      setTimeout(poll, 3000);
    }
  };

  poll();
}

// ── Utilities ───────────────────────────────────────────────

function escapeHtml(str) {
  const div = document.createElement("div");
  div.appendChild(document.createTextNode(str || ""));
  return div.innerHTML;
}

function escapeAttr(str) {
  return (str || "")
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
