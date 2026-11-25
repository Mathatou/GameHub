/// A class representing the result of an HTTP request. 
// It includes the status code, response data, and any error message.
class Receipt {
    constructor(status, data = null, error = null) {
        this.status = status;
        this.ok = status !== null && status >= 200 && status < 300;
        this.data = data;
        this.error = error;
    }
}

// Helper function
// For functions : addGameToLib, removeGameFromLib, getGame, getRandomGame
// Makes an HTTP request to the specified URL with the given options and returns a Receipt object.
// If the request fails or the response is not valid JSON, the Receipt will contain an error message.
// The receipt is returned with the status code, data (if any), and error message (if any).
async function request(url, options = {}) {
    let response;

    try {
        response = await fetch(url, options);
    }
    catch (error) {
        return new Receipt(null, null, error.message);
    }

    let rawBody = null;
    let bodyError = null;

    try {
        rawBody = await response.text();
    }
    catch (error) {
        bodyError = "Unable to read response body";
        return new Receipt(response.status, null, bodyError);
    }

    // Parse JSON if possible, otherwise preserve text
    let data = null;

    if (rawBody !== null && rawBody !== "") {
        try {
            data = JSON.parse(rawBody);
        }
        catch {
            return new Receipt(response.status, null, "Response body is not valid JSON");
        }
    }

    // Create and return the receipt
    let errorMessage = null;

    if (!response.ok) {
        errorMessage = rawBody || response.statusText || "HTTP request failed";
        return new Receipt(response.status, data, errorMessage);
    }
    else if (bodyError !== null) {
        errorMessage = bodyError;
    }

    return new Receipt(response.status, data, errorMessage);
}

export function addGameToLib(id) {
    return request(`/library/${id}`, { method: "POST" });
}

export function removeGameFromLib(id) {
    return request(`/library/${id}`, { method: "DELETE" });
}

export function getGame(params) {
    return request(`/games?${params}`);
}

export function getRandomGame(params) {
    return request(`/games/random?${params}`);
}
