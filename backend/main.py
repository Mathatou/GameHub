from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from .data import load_games
from .filters import filter_games
from .library import (
    update_entry,
    read_lib,
    remove_from_lib,
    add_to_lib,
    InvalidEntryError,
    IDNotFoundInLibraryError,
    IDAlreadyExistsError
)
BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="Board Game Finder")
GAMES = load_games()

@app.exception_handler(InvalidEntryError)
async def invalid_entry_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)}
    )

@app.exception_handler(IDNotFoundInLibraryError)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )

@app.exception_handler(IDAlreadyExistsError)
async def already_exists_handler(request, exc):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)}
    )

def search(players, max_time, max_complexity, source):
    only_ids = read_lib().keys() if source == "library" else None
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
    return GAMES[GAMES["id"].isin(read_lib().keys())].to_dict("records")

@app.post("/library/{game_id}")
def add_to_library(game_id: int):
    if not (GAMES["id"] == game_id).any():
        raise HTTPException(404, "Unknown game")
    return add_to_lib(game_id)
    
@app.delete("/library/{game_id}")
def remove_from_library(game_id: int):
    if not (GAMES["id"] == game_id).any():
        raise HTTPException(404, "Unknown game")
    return {"library_size": remove_from_lib(game_id)}
        
@app.patch("/library/{game_id}")
def update_library(game_id: int, body : dict):
    # let body be a dict so that it is catched by the Exceptions
    game = GAMES[GAMES["id"] == game_id]
    if game.empty:
        raise HTTPException(404, "Unknown game")
    min_players = int(game.iloc[0]["min_players"])
    max_players = int(game.iloc[0]["max_players"])
    return update_entry(game_id, (min_players, max_players),body)
# Must stay last: serves the frontend at http://localhost:8000/
app.mount("/", StaticFiles(directory=BASE_DIR / "frontend", html=True), name="frontend")