// ResumeMatch AI — frontend/script.js
// Day 5: mode toggle, drag-and-drop, validation, AND a real fetch()
// call to POST /analyze (backend still returns hardcoded placeholder
// JSON today — Day 6 wires up the real Gemini-powered response).

const BACKEND_URL = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"
  ? "http://127.0.0.1:5000"
  : "https://resumematch-ai-tai8.onrender.com";
const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024; // 5MB
const ALLOWED_EXTENSIONS = ["pdf", "docx"];
const MIN_RESUME_TEXT_LENGTH = 50;
const MIN_JD_LENGTH = 50;

// ---- State ----
let resumeMode = "upload"; // "upload" | "paste"
let resumeValid = false;
let jdValid = false;
let selectedFile = null;

// ---- Elements ----
const modeUploadBtn = document.getElementById("modeUploadBtn");
const modePasteBtn = document.getElementById("modePasteBtn");
const uploadMode = document.getElementById("uploadMode");
const pasteMode = document.getElementById("pasteMode");

const dropzone = document.getElementById("dropzone");
const resumeFileInput = document.getElementById("resumeFileInput");
const fileChip = document.getElementById("fileChip");
const fileChipName = document.getElementById("fileChipName");
const fileChipSize = document.getElementById("fileChipSize");
const fileChipRemove = document.getElementById("fileChipRemove");
const fileError = document.getElementById("fileError");

const resumeTextInput = document.getElementById("resumeTextInput");
const resumeCharCount = document.getElementById("resumeCharCount");
const resumeTextError = document.getElementById("resumeTextError");

const jdTextInput = document.getElementById("jdTextInput");
const jdCharCount = document.getElementById("jdCharCount");
const jdError = document.getElementById("jdError");

const analyzeBtn = document.getElementById("analyzeBtn");
const analyzeHint = document.getElementById("analyzeHint");
const analyzeResult = document.getElementById("analyzeResult");
const loadingState = document.getElementById("loadingState");
const loadingStateText = document.getElementById("loadingStateText");

const resultsBay = document.getElementById("resultsBay");
const scoreRingFill = document.getElementById("scoreRingFill");
const scoreNumber = document.getElementById("scoreNumber");
const scoreTier = document.getElementById("scoreTier");
const analyzeAnotherBtn = document.getElementById("analyzeAnotherBtn");

const SCORE_RING_CIRCUMFERENCE = 326.7;

// ---- Backend health check (Day 3/Milestone 1) ----
async function checkBackendHealth() {
  const dot = document.getElementById("statusDot");
  const text = document.getElementById("statusText");

  try {
    const response = await fetch(`${BACKEND_URL}/health`);
    const data = await response.json();

    if (response.ok && data.status === "ok") {
      dot.classList.remove("is-offline");
      dot.classList.add("is-online");
      text.textContent = "backend connected";
    } else {
      throw new Error("Unexpected health response");
    }
  } catch (err) {
    dot.classList.remove("is-online");
    dot.classList.add("is-offline");
    text.textContent = "backend offline";
  }
}

// ---- Mode toggle: Upload file <-> Paste text ----
function setResumeMode(mode) {
  resumeMode = mode;

  const isUpload = mode === "upload";
  modeUploadBtn.classList.toggle("is-active", isUpload);
  modePasteBtn.classList.toggle("is-active", !isUpload);
  modeUploadBtn.setAttribute("aria-selected", String(isUpload));
  modePasteBtn.setAttribute("aria-selected", String(!isUpload));

  uploadMode.hidden = !isUpload;
  pasteMode.hidden = isUpload;

  updateResumeValidity();
}

modeUploadBtn.addEventListener("click", () => setResumeMode("upload"));
modePasteBtn.addEventListener("click", () => setResumeMode("paste"));

// ---- File helpers ----
function getExtension(filename) {
  const parts = filename.split(".");
  return parts.length > 1 ? parts.pop().toLowerCase() : "";
}

function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function showFileError(message) {
  fileError.textContent = message;
  fileError.hidden = false;
}

function clearFileError() {
  fileError.textContent = "";
  fileError.hidden = true;
}

function handleFileSelected(file) {
  clearFileError();

  const ext = getExtension(file.name);
  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    showFileError(`"${file.name}" isn't a supported file type. Please upload a PDF or DOCX.`);
    clearSelectedFile();
    return;
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    showFileError(`"${file.name}" is too large (${formatFileSize(file.size)}). Max size is 5MB.`);
    clearSelectedFile();
    return;
  }

  selectedFile = file;
  fileChipName.textContent = file.name;
  fileChipSize.textContent = formatFileSize(file.size);
  fileChip.hidden = false;

  updateResumeValidity();
}

function clearSelectedFile() {
  selectedFile = null;
  resumeFileInput.value = "";
  fileChip.hidden = true;
  fileChipName.textContent = "";
  fileChipSize.textContent = "";
  updateResumeValidity();
}

fileChipRemove.addEventListener("click", () => {
  clearSelectedFile();
});

resumeFileInput.addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (file) {
    handleFileSelected(file);
  }
});

// Drag and drop — preventDefault on dragover AND drop, or the browser
// will try to open the file itself instead of letting us handle it.
["dragover", "dragenter"].forEach((eventName) => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.add("is-dragover");
  });
});

["dragleave", "dragend"].forEach((eventName) => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.remove("is-dragover");
  });
});

dropzone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropzone.classList.remove("is-dragover");

  const file = event.dataTransfer.files[0];
  if (file) {
    handleFileSelected(file);
  }
});

// ---- Resume paste-text validation ----
function updateResumeTextValidity() {
  const length = resumeTextInput.value.trim().length;
  resumeCharCount.textContent = `${length} characters`;

  if (length === 0) {
    resumeTextError.hidden = true;
    return false;
  }

  if (length < MIN_RESUME_TEXT_LENGTH) {
    resumeTextError.textContent = `Add a bit more detail — at least ${MIN_RESUME_TEXT_LENGTH} characters (currently ${length}).`;
    resumeTextError.hidden = false;
    return false;
  }

  resumeTextError.hidden = true;
  return true;
}

resumeTextInput.addEventListener("input", () => {
  updateResumeValidity();
});

// ---- Job description validation ----
function updateJdValidity() {
  const length = jdTextInput.value.trim().length;
  jdCharCount.textContent = `${length} characters`;

  if (length === 0) {
    jdError.hidden = true;
    jdValid = false;
    return;
  }

  if (length < MIN_JD_LENGTH) {
    jdError.textContent = `Add a bit more detail — at least ${MIN_JD_LENGTH} characters (currently ${length}).`;
    jdError.hidden = false;
    jdValid = false;
    return;
  }

  jdError.hidden = true;
  jdValid = true;
}

jdTextInput.addEventListener("input", () => {
  updateJdValidity();
  updateAnalyzeButton();
});

// ---- Combined resume validity (whichever mode is active) ----
function updateResumeValidity() {
  if (resumeMode === "upload") {
    resumeValid = Boolean(selectedFile);
  } else {
    resumeValid = updateResumeTextValidity();
  }
  updateAnalyzeButton();
}

// ---- Analyze button enable/disable ----
function updateAnalyzeButton() {
  const ready = resumeValid && jdValid;
  analyzeBtn.disabled = !ready;

  if (ready) {
    analyzeHint.textContent = "Ready to analyze";
  } else if (!resumeValid && !jdValid) {
    analyzeHint.textContent = "Add your resume and a job description to continue";
  } else if (!resumeValid) {
    analyzeHint.textContent = "Add your resume to continue";
  } else {
    analyzeHint.textContent = "Add a job description to continue";
  }
}

// ---- Analyze click — real fetch() call to POST /analyze ----
function setLoadingState(isLoading) {
  loadingState.hidden = !isLoading;
  analyzeBtn.disabled = isLoading || !(resumeValid && jdValid);
}

function showAnalyzeResult(message, isError) {
  analyzeResult.textContent = message;
  analyzeResult.hidden = false;
  analyzeResult.style.color = isError ? "var(--error-red)" : "var(--slate)";
}

function triggerParsingFailedFallback(message) {
  // Auto-switch to paste mode and explain why, per Day 5 spec.
  setResumeMode("paste");
  resumeTextError.textContent = message;
  resumeTextError.hidden = false;
  resumeTextInput.focus();
}

// ---- Results rendering ----
function scoreTierLabel(score) {
  if (score >= 80) return "Strong match";
  if (score >= 60) return "Good match";
  if (score >= 40) return "Partial match";
  return "Needs work";
}

function scoreTierColor(score) {
  if (score >= 80) return "var(--match-green)";
  if (score >= 60) return "var(--accent)";
  return "var(--error-red)";
}

function fillChipList(containerEl, emptyNoteEl, items) {
  containerEl.innerHTML = "";
  const hasItems = Array.isArray(items) && items.length > 0;

  if (hasItems) {
    items.forEach((item) => {
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.textContent = item;
      containerEl.appendChild(chip);
    });
  }

  if (emptyNoteEl) {
    emptyNoteEl.hidden = hasItems;
  }
}

function fillList(listEl, items, fallbackText) {
  listEl.innerHTML = "";
  const hasItems = Array.isArray(items) && items.length > 0;

  if (!hasItems) {
    const li = document.createElement("li");
    li.textContent = fallbackText;
    li.style.opacity = "0.6";
    listEl.appendChild(li);
    return;
  }

  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    listEl.appendChild(li);
  });
}

function renderResults(data) {
  const overall = Math.max(0, Math.min(100, Number(data.overall_score) || 0));

  // Score ring
  const offset = SCORE_RING_CIRCUMFERENCE - (overall / 100) * SCORE_RING_CIRCUMFERENCE;
  scoreRingFill.style.stroke = scoreTierColor(overall);
  // Reset then set on next frame so the transition animates from empty each time.
  scoreRingFill.style.strokeDashoffset = SCORE_RING_CIRCUMFERENCE;
  requestAnimationFrame(() => {
    scoreRingFill.style.strokeDashoffset = offset;
  });
  scoreNumber.textContent = overall;
  scoreTier.textContent = scoreTierLabel(overall);

  // Sub-scores
  const sub = data.sub_scores || {};
  const subMap = [
    ["skills", "barSkills", "valSkills"],
    ["keywords", "barKeywords", "valKeywords"],
    ["experience", "barExperience", "valExperience"],
    ["education", "barEducation", "valEducation"],
  ];
  subMap.forEach(([key, barId, valId]) => {
    const value = Math.max(0, Math.min(100, Number(sub[key]) || 0));
    const bar = document.getElementById(barId);
    const val = document.getElementById(valId);
    bar.style.width = "0%";
    requestAnimationFrame(() => {
      bar.style.width = `${value}%`;
    });
    val.textContent = value;
  });

  // Chips
  fillChipList(
    document.getElementById("missingKeywords"),
    document.getElementById("missingKeywordsEmpty"),
    data.missing_keywords
  );
  fillChipList(
    document.getElementById("missingSkills"),
    document.getElementById("missingSkillsEmpty"),
    data.missing_skills
  );

  // Lists
  fillList(document.getElementById("strengthsList"), data.strengths, "No specific strengths identified.");
  fillList(document.getElementById("weaknessesList"), data.weaknesses, "No specific weaknesses identified.");
  fillList(document.getElementById("suggestionsList"), data.suggestions, "No suggestions available.");

  resultsBay.hidden = false;
  resultsBay.scrollIntoView({ behavior: "smooth", block: "start" });
}

function resetResults() {
  resultsBay.hidden = true;
  analyzeResult.hidden = true;
  jdTextInput.value = "";
  resumeTextInput.value = "";
  clearSelectedFile();
  updateJdValidity();
  updateResumeValidity();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

analyzeAnotherBtn.addEventListener("click", resetResults);

analyzeBtn.addEventListener("click", async () => {
  if (analyzeBtn.disabled) return;

  analyzeResult.hidden = true;
  resultsBay.hidden = true;
  loadingStateText.textContent = "Analyzing your match\u2026";
  setLoadingState(true);

  // Render's free tier can take 30-50s to wake up after inactivity.
  // Let the person know after a few seconds so it doesn't look stuck.
  const slowHintTimer = setTimeout(() => {
    loadingStateText.textContent = "Still working \u2014 the server is waking up, this can take up to a minute\u2026";
  }, 6000);

  const formData = new FormData();

  if (resumeMode === "upload" && selectedFile) {
    formData.append("resume_file", selectedFile);
  } else {
    formData.append("resume_text", resumeTextInput.value.trim());
  }

  formData.append("job_description", jdTextInput.value.trim());

  try {
    // NOTE: do not set a Content-Type header manually here — the browser
    // sets the correct multipart/form-data boundary automatically for
    // FormData bodies. Setting it yourself breaks Flask's file parsing.
    const response = await fetch(`${BACKEND_URL}/analyze`, {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (!response.ok) {
      if (data.error === "parsing_failed") {
        triggerParsingFailedFallback(
          data.message || "We couldn't read that file. Please paste your resume text instead."
        );
      } else {
        showAnalyzeResult(data.message || "Something went wrong. Please try again.", true);
      }
      return;
    }

    renderResults(data);
  } catch (err) {
    console.error("Analyze request failed:", err);
    showAnalyzeResult(
      "Couldn't reach the backend right now. Please check your connection and try again.",
      true
    );
  } finally {
    clearTimeout(slowHintTimer);
    setLoadingState(false);
  }
});

// ---- Init ----
document.addEventListener("DOMContentLoaded", () => {
  checkBackendHealth();
  setResumeMode("upload");
  updateAnalyzeButton();
});