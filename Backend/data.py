from pathlib import Path
import pandas as pd

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "bgg_dataset.csv"

COLUMNS = {
    "ID": "id", "Name": "name", "Year Published": "year",
    "Min Players": "min_players", "Max Players": "max_players",
    "Play Time": "playing_time", "Min Age": "min_age",
    "Users Rated": "users_rated", "Rating Average": "rating",
    "BGG Rank": "rank", "Complexity Average": "complexity",
    "Owned Users": "owned_users", "Mechanics": "mechanics", "Domains": "domains",
}


def load_games() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, sep=";", decimal=",")
    if "Name" not in df.columns:           # file uses plain commas instead
        df = pd.read_csv(CSV_PATH)

    df = df.rename(columns=COLUMNS)[list(COLUMNS.values())]
    df = df.dropna(subset=["id", "name", "min_players", "max_players", "playing_time"])

    # remove unusable rows (zero values mean "unknown" in this dataset)
    df = df[(df["min_players"] > 0) & (df["max_players"] > 0)
            & (df["playing_time"] > 0) & (df["complexity"] > 0)]

    for col in ["id", "year", "min_players", "max_players", "playing_time",
                "min_age", "users_rated", "rank", "owned_users"]:
        df[col] = df[col].fillna(0).astype(int)
    df["mechanics"] = df["mechanics"].fillna("")
    df["domains"] = df["domains"].fillna("")
    return df.reset_index(drop=True)