import json
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles

from .data import load_games
from .filters import filter_games

BASE_DIR = Path(__file__).resolve().parent.parent
LIBRARY_FILE = BASE_DIR / "data" / "library.json"

app = FastAPI(title="Board Game Finder")
GAMES = load_games()


def load_library() -> set[int]:
    if LIBRARY_FILE.exists():
        return set(json.loads(LIBRARY_FILE.read_text()))
    return set()


def save_library(ids: set[int]) -> None:
    LIBRARY_FILE.write_text(json.dumps(sorted(ids)))


def search(players, max_time, max_complexity, source):
    only_ids = load_library() if source == "library" else None
    return filter_games(GAMES, players, max_time, max_complexity, only_ids)


@app.get("/games")
def get_games(players: Optional[int] = Query(None, ge=1),
              max_time: Optional[int] = Query(None, ge=1),
              max_complexity: Optional[float] = Query(None, ge=1, le=5),
              source: Literal["catalog", "library"] = "catalog"):
    result = search(players, max_time, max_complexity, source)
    return {"count": len(result), "games": result.head(50).to_dict("records")}


@app.get("/games/random")   # must be declared before any /games/{id} route
def random_game(players: Optional[int] = Query(None, ge=1),
                max_time: Optional[int] = Query(None, ge=1),
                max_complexity: Optional[float] = Query(None, ge=1, le=5),
                source: Literal["catalog", "library"] = "catalog"):
    result = search(players, max_time, max_complexity, source)
    if result.empty:
        raise HTTPException(404, "No game matches these criteria")
    return result.sample(1).iloc[0].to_dict()


@app.get("/library")
def get_library():
    return GAMES[GAMES["id"].isin(load_library())].to_dict("records")


@app.post("/library/{game_id}")
def add_to_library(game_id: int):
    if not (GAMES["id"] == game_id).any():
        raise HTTPException(404, "Unknown game")
    ids = load_library()
    ids.add(game_id)
    save_library(ids)
    return {"library_size": len(ids)}


@app.delete("/library/{game_id}")
def remove_from_library(game_id: int):
    ids = load_library()
    ids.discard(game_id)
    save_library(ids)
    return {"library_size": len(ids)}


# Must stay last: serves the frontend at http://localhost:8000/
app.mount("/", StaticFiles(directory=BASE_DIR / "frontend", html=True), name="frontend")