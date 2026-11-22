from pathlib import Path
import pandas as pd

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "bgg_dataset.csv"

# Mapping of column names in the CSV file to the internal column names we decided to use in our DataFrame.
# Key: column name in the CSV file, Value: internal column name
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
    df = df.rename(columns=COLUMNS)[list(COLUMNS.values())]
    df = clean_dataset(df)

    return df.reset_index(drop=True)

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    # We want only the games that have a name, a minimum and maximum number of players, and a playing time.
    df = df.dropna(subset=["id", "name", "min_players", "max_players", "playing_time"])

    # remove unusable rows (zero values mean "unknown" in this dataset)
    df = df[
            (df["min_players"] > 0) & 
            (df["max_players"] > 0) &
            (df["playing_time"] > 0) &
            (df["complexity"] > 0) &
            (df["id"] > 0) &
            (df["max_players"] >= df["min_players"])
         ]

    # if no value : write 0 for int columns, "" for string columns
    for intCol in ["id", "year", "min_players", "max_players", "playing_time",
                "min_age", "users_rated", "rank", "owned_users"]:
        df[intCol] = df[intCol].fillna(0).astype(int)

    for stringCol in ["mechanics", "domains"]:
        df[stringCol] = df[stringCol].fillna("").astype(str)

    return df
