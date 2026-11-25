export async function addGameToLib(id) {
    const response = await fetch(`/library/${id}`, { method: "POST" });
    if (!response.ok) throw new Error(`Add failed: ${response.status} ${response.statusText}`);
    }

export async function removeGameFromLib(id) {
    const response = await fetch(`/library/${id}`, { method: "DELETE" });
    if (!response.ok) throw new Error(`Remove failed: ${response.status} ${response.statusText}`);
}

export async function getGame(params) {
    const response = await fetch(`/games?${params}`);
    if(!response.ok) throw new Error(`Search failed: ${response.status} ${response.statusText}`);
    const data = await response.json();
    return data;
}

export async function getRandomGame(params) {
    const response = await fetch(`/games/random?${params}`);
    if (response.status === 404) {
        return null;
    }
    if (!response.ok) throw new Error(`Random failed: ${response.status} ${response.statusText}`);
    const data = await response.json();
    return data;
}