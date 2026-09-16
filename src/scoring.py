"""
scoring.py

Turning a league's scoring rules (abbreviation based, e.g. G, A, HIT)
into fantasy points, and validating a scoring config against the real
set of Yahoo fantasy hockey categories before trusting it.
"""

import pandas as pd

# Recognized fantasy stat categories (skaters and goalies use different sets).
VALID_SKATER_STATS = {
    "G", "A", "P", "+/-", "PIM", "PPG", "PPA", "PPP",
    "SHG", "SHA", "SHP", "GWG", "SOG", "SH%", "FW", "FL", "HIT", "BLK"
}

VALID_GOALIE_STATS = {
    "GS", "W", "L", "SHO", "SA", "SV", "GA", "GAA", "SV%"
}


def validate_scoring_config(config, valid_stats, label):
    """
    Checks that every key in a scoring config is a recognized fantasy
    stat. Returns (clean_config, rejected_keys), invalid keys are
    dropped, not silently kept.
    """
    clean_config = {}
    rejected = []
    for stat, value in config.items():
        if stat in valid_stats:
            clean_config[stat] = value
        else:
            rejected.append(stat)
    if rejected:
        print(f"Warning: the following {label} keys were not recognized and were dropped: {rejected}")
    return clean_config, rejected


# Maps scoring abbreviations to the actual column name in a cleaned game log.
# None means it's not directly available, and needs either a derived
# calculation (handled in apply_scoring) or isn't available at all.
SKATER_FIELD_MAP = {
    "G": "goals",
    "A": "assists",
    "P": "points",
    "+/-": "plusMinus",
    "PIM": "pim",
    "PPG": "powerPlayGoals",
    "PPA": "ppAssists",       # derived, powerPlayPoints minus powerPlayGoals
    "PPP": "powerPlayPoints",
    "SHG": "shorthandedGoals",
    "SHA": "shAssists",       # derived, shorthandedPoints minus shorthandedGoals
    "SHP": "shorthandedPoints",
    "GWG": "gameWinningGoals",
    "SOG": "shots",
    "SH%": "shootingPctg",
    "HIT": "hits",            # from boxscore pull
    "BLK": "blockedShots",    # from boxscore pull
    "FW": None,   # not available as a raw count, only a percentage exists
    "FL": None,
}

GOALIE_FIELD_MAP = {
    "SA": "shotsAgainst",
    "SV": None,   # derived, shotsAgainst minus goalsAgainst
    "GA": "goalsAgainst",
    "SV%": "savePctg",
    "SHO": "shutouts",
    "W": "decision",
    "L": "decision",
    "GS": "gamesStarted",
    "GAA": None,  # rate stat across games, not scored per-game, see future_directions
}


def get_relevant_columns(scoring_config, field_map):
    """
    Works out which raw columns are needed to score a given scoring
    config, based on field_map. Used to decide what a cleaning step
    needs to check for, tied directly to a league's real scoring rules.
    """
    columns = set()
    for stat in scoring_config:
        if stat in ("W", "L"):
            columns.add("decision")
        elif stat == "SV":
            columns.add("shotsAgainst")
            columns.add("goalsAgainst")
        else:
            field = field_map.get(stat)
            if field is not None:
                columns.add(field)
    return sorted(columns)


def apply_scoring(games_df, scoring_config, field_map):
    """
    Converts a scoring config (abbreviation based) into fantasy points
    per game, using field_map to translate abbreviations into actual
    column names. Handles derived cases (W, L, SV) separately, since
    they're not a direct column read.
    """
    points = pd.Series(0.0, index=games_df.index)
    unmapped = []

    for stat, weight in scoring_config.items():
        field = field_map.get(stat)

        if stat == "W":
            points += (games_df["decision"] == "W").astype(int) * weight
        elif stat == "L":
            points += (games_df["decision"] == "L").astype(int) * weight
        elif stat == "SV":
            points += (games_df["shotsAgainst"] - games_df["goalsAgainst"]) * weight
        elif field is None:
            unmapped.append(stat)
        else:
            points += games_df[field] * weight

    if unmapped:
        print(f"Warning, these scored categories aren't available from this data source and were skipped: {unmapped}")

    return points


def apply_scoring_breakdown(games_df, scoring_config, field_map):
    """
    Same logic as apply_scoring, but returns a DataFrame with one
    column per scored category showing its point contribution, plus a
    total column, useful for checking a result category by category
    rather than trusting a single summed number.
    """
    breakdown = {}
    unmapped = []

    for stat, weight in scoring_config.items():
        field = field_map.get(stat)

        if stat == "W":
            breakdown[f"{stat}_pts"] = (games_df["decision"] == "W").astype(int) * weight
        elif stat == "L":
            breakdown[f"{stat}_pts"] = (games_df["decision"] == "L").astype(int) * weight
        elif stat == "SV":
            breakdown[f"{stat}_pts"] = (games_df["shotsAgainst"] - games_df["goalsAgainst"]) * weight
        elif field is None:
            unmapped.append(stat)
            breakdown[f"{stat}_pts"] = 0.0
        else:
            breakdown[f"{stat}_pts"] = games_df[field] * weight

    breakdown_df = pd.DataFrame(breakdown)
    breakdown_df["total"] = breakdown_df.sum(axis=1)

    if unmapped:
        print(f"Note, these categories aren't available and are showing as 0: {unmapped}")

    return breakdown_df
