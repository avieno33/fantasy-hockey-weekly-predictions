"""
data_pull.py

All communication with the NHL public API and the local disk cache.
No scoring or statistics logic lives here, only pulling and caching
raw data.
"""

import os
import time
from datetime import datetime

import pandas as pd
import requests

CACHE_DIR = "data"
os.makedirs(CACHE_DIR, exist_ok=True)


# --- caching helpers -------------------------------------------------

def cache_path(key):
    return os.path.join(CACHE_DIR, f"{key}.csv")


def cache_age_hours(key):
    """Returns how old a cached file is, in hours, or None if it doesn't exist yet."""
    path = cache_path(key)
    if not os.path.exists(path):
        return None
    modified = datetime.fromtimestamp(os.path.getmtime(path))
    return (datetime.now() - modified).total_seconds() / 3600


def save_to_cache(df, key):
    if df.empty:
        return
    df.to_csv(cache_path(key), index=False)


def load_from_cache(key):
    return pd.read_csv(cache_path(key))


def get_current_season():
    """
    Works out the current NHL season string, like 20262027, based on
    today's date. New seasons typically start in October, so anything
    July or later counts as the start of a new season year.
    """
    today = datetime.now()
    start_year = today.year if today.month >= 7 else today.year - 1
    return f"{start_year}{start_year + 1}"


CURRENT_SEASON = get_current_season()


# --- player lookup -----------------------------------------------------

def get_player_id(player_name):
    """
    Looks up a single player's NHL API id by name. Lighter than pulling
    every team's full roster, useful when you already know which
    specific players you need (as week01 does), rather than needing
    the full league-wide player table.
    """
    url = "https://search.d3.nhle.com/api/v1/search/player"
    params = {"culture": "en-us", "limit": 5, "q": player_name, "active": "true"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json()
    if not results:
        print(f"No player found matching '{player_name}'")
        return None
    return results[0]["playerId"]


# --- game logs -----------------------------------------------------------

def fetch_game_log(player_id, season, game_type=2):
    """
    Pulls a player's game log for a given season, directly from the API,
    no caching. season format is like 20232024, game_type 2 is regular
    season, 3 is playoffs. Returns a DataFrame, one row per game.
    """
    url = f"https://api-web.nhle.com/v1/player/{player_id}/game-log/{season}/{game_type}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    games = data.get("gameLog", [])
    return pd.DataFrame(games)


def get_game_log(player_id, season=None, game_type=2, refresh_after_hours=6, force_refresh=False):
    """
    Loads a player's game log, from cache if fresh enough, otherwise
    pulls fresh from fetch_game_log and caches the result. Handles an
    empty season gracefully (pre-season, or a player who wasn't in the
    NHL that season) rather than crashing.
    """
    season = season or CURRENT_SEASON
    key = f"gamelog_{player_id}_{season}"
    age = cache_age_hours(key)

    if not force_refresh and age is not None and age < refresh_after_hours:
        print(f"Loading game log for {player_id}, {season} from cache, {age:.1f} hours old")
        return load_from_cache(key)

    print(f"Pulling fresh game log for {player_id}, {season}")
    log_df = fetch_game_log(player_id, season, game_type)

    if log_df.empty:
        if season == CURRENT_SEASON:
            print(f"No games found for {player_id} in {season}, season may not have started yet")
        else:
            print(f"No games found for {player_id} in {season}, player likely wasn't in the NHL that season")
        return log_df

    save_to_cache(log_df, key)
    return log_df


# --- boxscores, for hits and blocked shots ------------------------------

def get_boxscore(game_id, refresh_after_hours=24, force_refresh=False):
    """
    Pulls the boxscore for a single game, cached by game id. A finished
    game's boxscore never changes, so once cached, it's cached for good.
    """
    key = f"boxscore_{game_id}"
    age = cache_age_hours(key)

    if not force_refresh and age is not None and age < refresh_after_hours:
        return load_from_cache(key)

    url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    rows = []
    stats = data.get("playerByGameStats", {})
    for side in ["awayTeam", "homeTeam"]:
        for group in ["forwards", "defense", "goalies"]:
            for player in stats.get(side, {}).get(group, []):
                row = dict(player)
                row["gameId"] = game_id
                rows.append(row)

    boxscore_df = pd.DataFrame(rows)
    if not boxscore_df.empty:
        save_to_cache(boxscore_df, key)
    return boxscore_df


def get_hits_and_blocks(player_id, game_log, pause=0.3):
    """
    For every game in a player's game log, pulls that game's boxscore
    (cached, reused for other players in the same game later) and
    extracts hits and blockedShots for this specific player.
    """
    records = []
    for game_id in game_log["gameId"]:
        boxscore = get_boxscore(game_id)
        if boxscore.empty:
            continue
        player_row = boxscore[boxscore["playerId"] == player_id]
        if player_row.empty:
            continue
        records.append({
            "gameId": game_id,
            "hits": player_row.iloc[0].get("hits", 0),
            "blockedShots": player_row.iloc[0].get("blockedShots", 0),
        })
        time.sleep(pause)
    return pd.DataFrame(records)


# --- schedule, for weekly game counts ---------------------------------

def get_games_this_week(team_abbrev, week_start_date):
    """
    Returns the number of games a team plays in the week starting on
    week_start_date (YYYY-MM-DD). NOT YET TESTED against a real
    schedule, confirm against a team you know the schedule for before
    trusting this in week01.
    """
    url = f"https://api-web.nhle.com/v1/club-schedule/{team_abbrev}/week/{week_start_date}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return len(data.get("games", []))
