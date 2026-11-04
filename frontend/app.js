const $ = (id) => document.getElementById(id);

function getSource() {
  return document.querySelector('input[name="source"]:checked').value;
}

// Blank fields are simply not sent, so the backend ignores them
function buildParams() {
  const params = new URLSearchParams({ source: getSource() });
  if ($("players").value) params.append("players", $("players").value);
  if ($("maxTime").value) params.append("max_time", $("maxTime").value);
  if ($("maxComplexity").value) params.append("max_complexity", $("maxComplexity").value);
  return params;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function gameLine(g) {
  return `${escapeHtml(g.name)} (${g.min_players}-${g.max_players} players, ` +
         `${g.playing_time} min, complexity ${g.complexity.toFixed(1)})`;
}

async function search() {
  $("randomResult").innerHTML = "";
  const response = await fetch(`/games?${buildParams()}`);
  const data = await response.json();
  const inLibrary = getSource() === "library";

  $("message").textContent = `${data.count} games found` +
    (data.count > data.games.length ? ` (showing ${data.games.length})` : "");
  $("results").innerHTML = data.games.map((g) => `
    <li>
      <span>${gameLine(g)}</span>
      <button data-id="${g.id}" data-action="${inLibrary ? "remove" : "add"}">
        ${inLibrary ? "Remove" : "Add to library"}
      </button>
    </li>`).join("");
}

async function pickRandom() {
  const response = await fetch(`/games/random?${buildParams()}`);
  if (!response.ok) {
    $("randomResult").textContent = "No game matches these criteria.";
    return;
  }
  const game = await response.json();
  $("randomResult").innerHTML = `<strong>Your pick:</strong> ${gameLine(game)}`;
}

async function onResultClick(event) {
  const button = event.target.closest("button");
  if (!button) return;
  const adding = button.dataset.action === "add";
  await fetch(`/library/${button.dataset.id}`, { method: adding ? "POST" : "DELETE" });
  if (adding) {
    button.textContent = "Added ✓";
    button.disabled = true;
  } else {
    button.closest("li").remove();
  }
}

$("searchBtn").addEventListener("click", search);
$("randomBtn").addEventListener("click", pickRandom);
$("results").addEventListener("click", onResultClick);