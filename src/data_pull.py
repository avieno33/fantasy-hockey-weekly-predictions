"""
data_pull.py

All communication with the NHL public API and the local disk cache.
No scoring or statistics logic lives here, only pulling and caching
raw data.
"""

import os
import time
from datetime import datetime, timedelta

import pandas as pd
import requests

from difflib import SequenceMatcher

CACHE_DIR = "data"
os.makedirs(CACHE_DIR, exist_ok=True)

# A boxscore only gets cached once the game is over, since an in-progress
# boxscore changes by the minute and would go stale on disk.
FINAL_GAME_STATES = {"FINAL", "OFF"}

SCHEDULE_COLUMNS = ["gameId", "gameDate", "gameType", "gameState", "awayTeam", "homeTeam"]


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

def name_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def get_player_id(player_name, min_similarity=0.75):
    """
    Looks up a single player's NHL API id by name. Tries an active-only
    search first, and if the best match looks weak, retries without the
    active filter, since a player with an unusual season (an injury,
    a leave of absence, a return with a new team) can be excluded from
    the active-only search and cause a false match otherwise. Always
    prints the matched name, so a mismatch is visible immediately.
    """
    def search(active_only):
        url = "https://search.d3.nhle.com/api/v1/search/player"
        params = {"culture": "en-us", "limit": 5, "q": player_name}
        if active_only:
            params["active"] = "true"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    results = search(active_only=True)
    scored = [(r, name_similarity(player_name, r["name"])) for r in results]

    best_match, best_score = (max(scored, key=lambda pair: pair[1]) if scored else (None, 0))

    if best_score < min_similarity:
        # active-only search gave a weak match, try without the filter
        fallback_results = search(active_only=False)
        fallback_scored = [(r, name_similarity(player_name, r["name"])) for r in fallback_results]
        if fallback_scored:
            fallback_best, fallback_score = max(fallback_scored, key=lambda pair: pair[1])
            if fallback_score > best_score:
                best_match, best_score = fallback_best, fallback_score
                print(f"Note, '{player_name}' wasn't found in the active-only search, "
                      f"matched via a broader search instead")

    if best_match is None:
        print(f"No player found matching '{player_name}'")
        return None

    if best_score < min_similarity:
        print(f"Warning, low-confidence match for '{player_name}', best guess was "
              f"'{best_match['name']}' (similarity {best_score:.2f}), double check this is right")
    else:
        print(f"Matched '{player_name}' to '{best_match['name']}'")

    return int(best_match["playerId"])

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

    A completed season never changes, so once a past season's log is
    cached it's reused as long as the file exists, refresh_after_hours
    only applies to the current season, where new games keep landing.
    force_refresh overrides both.
    """
    season = season or CURRENT_SEASON
    key = f"gamelog_{player_id}_{season}"
    age = cache_age_hours(key)
    season_is_completed = str(season) != CURRENT_SEASON

    cache_is_usable = age is not None and (season_is_completed or age < refresh_after_hours)

    if not force_refresh and cache_is_usable:
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

def get_boxscore(game_id, force_refresh=False):
    """
    Pulls the boxscore for a single game, cached by game id. A finished
    game's boxscore never changes, so once a finished game is cached
    it's cached for good. A game that isn't finished yet is returned but
    never cached, so a partial boxscore can't get stuck on disk.
    """
    key = f"boxscore_{game_id}"

    if not force_refresh and cache_age_hours(key) is not None:
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
    if not boxscore_df.empty and data.get("gameState") in FINAL_GAME_STATES:
        save_to_cache(boxscore_df, key)
    return boxscore_df


def get_hits_and_blocks(player_id, game_log, pause=0.3):
    """
    For every game in a player's game log, pulls that game's boxscore
    (cached, reused for other players in the same game later) and
    extracts hits and blockedShots for this specific player. Only
    pauses between real API calls, a cached boxscore costs no wait.
    """
    records = []
    for game_id in game_log["gameId"]:
        was_cached = cache_age_hours(f"boxscore_{game_id}") is not None
        boxscore = get_boxscore(game_id)
        if not was_cached:
            time.sleep(pause)
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
    # explicit columns, so an empty result still merges cleanly on gameId
    return pd.DataFrame(records, columns=["gameId", "hits", "blockedShots"])


# --- schedule, for weekly game counts ---------------------------------

def get_team_schedule(team_abbrev, season=None, refresh_after_hours=12, force_refresh=False):
    """
    Pulls a team's full season schedule (preseason, regular season and
    anything else the API lists) as one row per game, cached per team.
    Uses the full-season endpoint rather than the weekly one, so any
    date window works, including a league's odd-length first week.
    Schedules do get changed (postponements), so the cache expires.
    """
    season = season or CURRENT_SEASON
    key = f"schedule_{team_abbrev}_{season}"
    age = cache_age_hours(key)

    if not force_refresh and age is not None and age < refresh_after_hours:
        schedule = load_from_cache(key)
        schedule["gameDate"] = pd.to_datetime(schedule["gameDate"])
        return schedule

    url = f"https://api-web.nhle.com/v1/club-schedule-season/{team_abbrev}/{season}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    rows = [{
        "gameId": game["id"],
        "gameDate": game["gameDate"],
        "gameType": game["gameType"],
        "gameState": game.get("gameState"),
        "awayTeam": game["awayTeam"]["abbrev"],
        "homeTeam": game["homeTeam"]["abbrev"],
    } for game in data.get("games", [])]

    schedule = pd.DataFrame(rows, columns=SCHEDULE_COLUMNS)
    if schedule.empty:
        return schedule

    schedule["gameDate"] = pd.to_datetime(schedule["gameDate"])
    save_to_cache(schedule, key)
    return schedule


def get_games_in_window(team_abbrev, start_date, end_date, season=None, game_type=2):
    """
    Returns a team's games between start_date and end_date, both
    inclusive (YYYY-MM-DD), regular season only by default so
    preseason games can't inflate a count. gameDate is the date the
    NHL lists for the game, so a late West Coast start still counts
    on its listed day.
    """
    schedule = get_team_schedule(team_abbrev, season=season)
    if schedule.empty:
        return schedule

    in_window = (
        (schedule["gameDate"] >= pd.Timestamp(start_date)) &
        (schedule["gameDate"] <= pd.Timestamp(end_date)) &
        (schedule["gameType"] == game_type)
    )
    return schedule[in_window].reset_index(drop=True)


def get_games_this_week(team_abbrev, week_start_date, days=7):
    """
    Returns the number of regular season games a team plays in the
    window starting on week_start_date (YYYY-MM-DD) and lasting `days`
    days, 7 by default. Pass a different `days` for a league week
    that isn't seven days long. Checked against the TOR schedule, see
    tests/test_src.ipynb.
    """
    start = pd.Timestamp(week_start_date)
    end = start + timedelta(days=days - 1)
    return len(get_games_in_window(team_abbrev, start, end))
