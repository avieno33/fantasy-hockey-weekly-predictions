"""
stats.py

Cleaning game logs, building a skater's full stat line, and computing
mu/sigma two ways: EWMA (recent form) and shrinkage-blended toward a
prior season (season-level talent).

Note: scoring_config and field_map are required arguments throughout,
no silent fallback to any one default league, since this module is
meant to score the same player under several different leagues.
"""

import pandas as pd

from data_pull import get_game_log, get_hits_and_blocks
from scoring import apply_scoring

ALL_SKATER_RAW_FIELDS = [
    "goals", "assists", "points", "plusMinus", "pim",
    "powerPlayGoals", "powerPlayPoints",
    "shorthandedGoals", "shorthandedPoints",
    "gameWinningGoals", "shots", "shootingPctg",
]

# savePctg is always included regardless of a league's specific scoring,
# it's used throughout analysis even when not itself a scored category.
GOALIE_NUMERIC_COLUMNS_BASE = ["savePctg", "goalsAgainst", "shotsAgainst", "shutouts", "gamesStarted"]


def clean_game_log(log_df, numeric_columns, required_columns=None):
    """
    Cleans a raw game log. numeric_columns get coerced to numeric
    types. required_columns (defaults to numeric_columns) get checked
    for missing values and dropped if missing, kept separate from
    numeric_columns since some required fields (like decision) are
    categorical, not numeric.
    """
    df = log_df.copy()

    if required_columns is None:
        required_columns = numeric_columns

    if "gameDate" in df.columns:
        df["gameDate"] = pd.to_datetime(df["gameDate"])

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    before = len(df)
    df = df.dropna(subset=[c for c in required_columns if c in df.columns])
    dropped = before - len(df)
    if dropped > 0:
        print(f"Dropped {dropped} rows with missing stats")

    return df.sort_values("gameDate").reset_index(drop=True) if "gameDate" in df.columns else df


def clean_goalie_log(log_df, numeric_columns=None):
    """
    Cleaning specifically for goalie game logs. Never requires
    'decision' to be present, relief appearances legitimately have
    none but still have real, scoreable stats. Missing decision
    becomes 'ND' rather than causing the row to be dropped.
    """
    numeric_columns = numeric_columns or GOALIE_NUMERIC_COLUMNS_BASE
    df = clean_game_log(log_df, numeric_columns, required_columns=numeric_columns)
    df["decision"] = df["decision"].fillna("ND") if "decision" in df.columns else "ND"
    return df


def build_full_skater_log(player_id, season, include_hits_blocks=True):
    """
    Pulls a skater's game log and builds every stat category that's
    sourceable: direct fields, derived fields (PPA, SHA), and
    hits/blocks from the boxscore. Returns an empty DataFrame if the
    player hasn't played this season, rather than erroring.
    """
    log = get_game_log(player_id, season=season, force_refresh=False)

    if log.empty:
        return log

    log = clean_game_log(log, ALL_SKATER_RAW_FIELDS)

    log["ppAssists"] = log["powerPlayPoints"] - log["powerPlayGoals"]
    log["shAssists"] = log["shorthandedPoints"] - log["shorthandedGoals"]

    if include_hits_blocks:
        hits_blocks = get_hits_and_blocks(player_id, log)
        log = log.merge(hits_blocks, on="gameId", how="left")

    return log


def compute_ewma_mu_sigma(points_series, half_life=5):
    """
    Computes the exponentially weighted mean (mu) and standard
    deviation (sigma) of a fantasy points series, most recent games
    weighted most heavily.
    """
    ewm = points_series.ewm(halflife=half_life, adjust=True)
    return ewm.mean(), ewm.std()


def blend_mu_sigma(current_mu, current_sigma, prior_mu, prior_sigma, n, k=10):
    """
    Blends a current-season flat-mean estimate with a prior-season
    estimate, weighted by how many current-season games have been
    observed (n) and a trust constant k. Uses the flat mean, not
    EWMA, see METHODOLOGY.md for why the two shouldn't be combined.
    """
    blended_mu = (n * current_mu + k * prior_mu) / (n + k)
    blended_var = (n * current_sigma**2 + k * prior_sigma**2) / (n + k)
    return blended_mu, blended_var**0.5


def get_prior_season_stats(player_id, season, position, scoring_config, field_map):
    """
    Computes simple season-long mean and std from a completed season,
    used as the shrinkage prior. Not EWMA, the season is already over,
    so there's no recency to weight, just the overall level and spread.
    """
    if position == "G":
        log = get_game_log(player_id, season=season, force_refresh=False)
        if log.empty:
            return None, None
        log = clean_goalie_log(log)
        log["fantasy_points"] = apply_scoring(log, scoring_config, field_map)
    else:
        log = build_full_skater_log(player_id, season)
        if log.empty:
            return None, None
        log["fantasy_points"] = apply_scoring(log, scoring_config, field_map)

    return log["fantasy_points"].mean(), log["fantasy_points"].std()


def get_player_estimates(player_id, position, scoring_config, field_map,
                           season, prior_season, half_life=5, k=10):
    """
    Computes both estimates for a player: EWMA (recent form) and
    shrinkage-blended (season-level talent, leaning on the prior
    season early). scoring_config and field_map are required, this
    is meant to be called once per league for the same player, not
    tied to any single default league's rules.
    """
    if position == "G":
        log = get_game_log(player_id, season=season, force_refresh=False)
        if log.empty:
            return None
        log = clean_goalie_log(log)
        log["fantasy_points"] = apply_scoring(log, scoring_config, field_map)
    else:
        log = build_full_skater_log(player_id, season)
        if log.empty:
            return None
        log["fantasy_points"] = apply_scoring(log, scoring_config, field_map)

    prior_mu, prior_sigma = get_prior_season_stats(player_id, prior_season, position, scoring_config, field_map)

    ewma_mu, ewma_sigma = compute_ewma_mu_sigma(log["fantasy_points"], half_life=half_life)

    n_games = len(log)
    current_mu = log["fantasy_points"].mean()
    current_sigma = log["fantasy_points"].std() if n_games > 1 else 0

    if prior_mu is not None:
        blended_mu, blended_sigma = blend_mu_sigma(current_mu, current_sigma, prior_mu, prior_sigma, n=n_games, k=k)
    else:
        blended_mu, blended_sigma = current_mu, current_sigma

    return {
        "games_played": n_games,
        "recent_mu": ewma_mu.iloc[-1],
        "recent_sigma": ewma_sigma.iloc[-1],
        "season_mu": blended_mu,
        "season_sigma": blended_sigma,
    }
