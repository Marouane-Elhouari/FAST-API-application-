function apiHeaders(extra = {}) {
  return { "X-API-Key": window.API_KEY, ...extra };
}

async function apiPost(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: apiHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || res.statusText);
  return data;
}

async function apiGetBlob(path) {
  const res = await fetch(path, { headers: apiHeaders() });
  if (!res.ok) throw new Error(`Échec (${res.status})`);
  return res.blob();
}

function showError(el, message) {
  el.textContent = message;
  el.classList.remove("d-none");
}

function hideError(el) {
  el.classList.add("d-none");
  el.textContent = "";
}

const predictForm = document.getElementById("predict-form");
const predictError = document.getElementById("predict-error");
const predictResult = document.getElementById("predict-result");

predictForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const smiles = document.getElementById("predict-smiles").value.trim();
  if (!smiles) return;
  hideError(predictError);
  predictResult.classList.add("d-none");

  try {
    const data = await apiPost("/api/predict", { smiles });
    document.getElementById("predict-result-smiles").textContent = data.smiles;
    document.getElementById("predict-result-value").textContent = data.prediction.toFixed(4);
    document.getElementById("predict-result-version").textContent = `Modèle : ${data.model_version}`;
    predictResult.classList.remove("d-none");
  } catch (err) {
    showError(predictError, err.message);
  }
});

const historyBody = document.getElementById("history-body");
const historyError = document.getElementById("history-error");
const historyCount = document.getElementById("history-count");

async function loadHistory() {
  hideError(historyError);
  historyBody.innerHTML = `<tr><td colspan="3" class="text-center text-muted py-4">Chargement…</td></tr>`;
  try {
    const res = await fetch("/api/history", { headers: apiHeaders() });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || res.statusText);

    const rows = data.historique || [];
    historyCount.textContent = `${rows.length} entrée(s) enregistrée(s)`;
    historyBody.innerHTML = rows.length
      ? rows
          .map(
            (r) => `<tr>
              <td>${r.timestamp}</td>
              <td class="font-mono">${r.smiles}</td>
              <td>${Number(r.prediction).toFixed(4)}</td>
            </tr>`
          )
          .join("")
      : `<tr><td colspan="3" class="text-center text-muted py-4">Aucune prédiction pour l'instant.</td></tr>`;
  } catch (err) {
    showError(historyError, err.message);
    historyBody.innerHTML = "";
  }
}

document.getElementById("history-refresh").addEventListener("click", loadHistory);

async function downloadFile(path, filename) {
  try {
    const blob = await apiGetBlob(path);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (err) {
    showError(historyError, err.message);
  }
}

document.getElementById("history-export-csv").addEventListener("click", () =>
  downloadFile("/api/export-csv", "historique.csv")
);
document.getElementById("history-export-xlsx").addEventListener("click", () =>
  downloadFile("/api/export-xlsx", "historique.xlsx")
);

document
  .querySelector('.nav-sections [data-target="history"]')
  .addEventListener("click", loadHistory, { once: true });

const voxel3dForm = document.getElementById("voxel3d-form");
const voxel3dError = document.getElementById("voxel3d-error");
const voxel3dFrameWrap = document.getElementById("voxel3d-frame-wrap");
const voxel3dFrame = document.getElementById("voxel3d-frame");
let voxel3dObjectUrl = null;

voxel3dForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const smiles = document.getElementById("voxel3d-smiles").value.trim();
  if (!smiles) return;
  hideError(voxel3dError);
  voxel3dFrameWrap.classList.add("d-none");

  try {
    const { html_url } = await apiPost("/api/mol-3d", { smiles });
    const blob = await apiGetBlob(html_url);
    if (voxel3dObjectUrl) URL.revokeObjectURL(voxel3dObjectUrl);
    voxel3dObjectUrl = URL.createObjectURL(blob);
    voxel3dFrame.src = voxel3dObjectUrl;
    voxel3dFrameWrap.classList.remove("d-none");
  } catch (err) {
    showError(voxel3dError, err.message);
  }
});

const rdkitForm = document.getElementById("rdkit-form");
const rdkitError = document.getElementById("rdkit-error");
const rdkitImageWrap = document.getElementById("rdkit-image-wrap");
const rdkitImg = document.getElementById("rdkit-img");

rdkitForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const smiles = document.getElementById("rdkit-smiles").value.trim();
  if (!smiles) return;
  hideError(rdkitError);
  rdkitImageWrap.classList.add("d-none");

  try {
    const data = await apiPost("/api/mol-2d", { smiles });
    rdkitImg.src = `data:image/png;base64,${data.image_base64}`;
    rdkitImageWrap.classList.remove("d-none");
  } catch (err) {
    showError(rdkitError, err.message);
  }
});
