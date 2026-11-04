def filter_games(df, players=None, max_time=None, max_complexity=None, only_ids=None):
    """A criterion set to None is ignored."""
    result = df
    if only_ids is not None:
        result = result[result["id"].isin(only_ids)]
    if players is not None:
        result = result[(result["min_players"] <= players) & (players <= result["max_players"])]
    if max_time is not None:
        result = result[result["playing_time"] <= max_time]
    if max_complexity is not None:
        result = result[result["complexity"] <= max_complexity]
    return result.sort_values("owned_users", ascending=False)