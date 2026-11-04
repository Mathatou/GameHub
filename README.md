# GameHub - Board Game Finder & Explorer

GameHub is a web application designed to help board game enthusiasts find the perfect game for any gathering. It features customizable criteria, strict/relaxed matching (such as ideal player counts vs. supported counts), max rule explanation time filtering, profiles, and quick preset modes (e.g., Child Mode).

---

## Prerequisites

Before starting, ensure you have the following installed on your machine:
* [Node.js](https://nodejs.org/) (Version 18.x or higher)
* `npm` (Included with Node.js)

---

## Project Structure

```text
GameHub/
├── backend/            # Express.js REST API
│   ├── package.json
│   ├── server.js
│   └── games.json
├── frontend/           # Vite + React UI
│   ├── package.json
│   ├── src/
│   └── index.html
├── setup.bat           # Automated setup script for Windows
├── setup.sh            # Automated setup script for Linux/macOS
└── README.md
```

---

## Quick Setup (Automated)

### Windows
Double-click `setup.bat` or run it from Command Prompt / PowerShell:
```cmd
.\setup.bat
```

### Linux / macOS
Grant execution permissions and run `setup.sh`:
```bash
chmod +x setup.sh
./setup.sh
```

---

## Manual Installation Guide

If you prefer installing dependencies manually, follow these steps:

### 1. Install Backend Dependencies
Navigate to the root directory where `server.js` resides (or the `backend` folder depending on your setup) and run:
```bash
npm install
```

### 2. Install Frontend Dependencies
Navigate to the `frontend` folder and install packages:
```bash
cd frontend
npm install
cd ..
```

---

## Running the Application

To run the application, you need to start both the **backend server** and the **frontend development server** in separate terminal windows.

### Terminal 1: Backend Server
From the root directory (or `backend/` folder):
```bash
node server.js
```
> Server runs at: `http://localhost:5000`

### Terminal 2: Frontend Client
From the `frontend/` directory:
```bash
cd frontend
npm run dev
```
> Client runs at: `http://localhost:5173`

---

## API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/games` | Retrieve filtered games based on query parameters (`player_count`, `max_explanation_time`, `play_style`). Returns suggested matches if no exact match is found. |