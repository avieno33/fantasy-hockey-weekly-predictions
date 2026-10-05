"""
matchup.py

Comparing two players (or one player across a week's worth of games),
and the goalie opponent shot-volume adjustment.
"""

from scipy.stats import norm


def compare_players(estimates_a, estimates_b, label_a="Player A", label_b="Player B", use="season"):
    """
    Computes the probability that player A outperforms player B, using
    either season-level (blended) or recent (EWMA) mu/sigma, season by
    default. Handles the zero-volatility edge case without dividing
    by zero.
    """
    mu_key = f"{use}_mu"
    sigma_key = f"{use}_sigma"

    mu_a, sigma_a = estimates_a[mu_key], estimates_a[sigma_key]
    mu_b, sigma_b = estimates_b[mu_key], estimates_b[sigma_key]

    combined_sigma = (sigma_a**2 + sigma_b**2) ** 0.5

    if combined_sigma == 0:
        probability_a_wins = 1.0 if mu_a > mu_b else (0.0 if mu_a < mu_b else 0.5)
    else:
        z = (mu_a - mu_b) / combined_sigma
        probability_a_wins = norm.cdf(z)

    return {
        "label_a": label_a, "mu_a": mu_a, "sigma_a": sigma_a,
        "label_b": label_b, "mu_b": mu_b, "sigma_b": sigma_b,
        "probability_a_outperforms_b": probability_a_wins,
    }


def print_comparison(result):
    print(f"{result['label_a']}: mu={result['mu_a']:.2f}, sigma={result['sigma_a']:.2f}")
    print(f"{result['label_b']}: mu={result['mu_b']:.2f}, sigma={result['sigma_b']:.2f}")
    print(f"P({result['label_a']} outperforms {result['label_b']}) = {result['probability_a_outperforms_b']:.1%}")


def weekly_from_per_game(per_game_mu, per_game_sigma, games_this_week, start_share=1.0):
    """
    Converts a per-game mu/sigma into a weekly total. Variance adds
    across independent games, so sigma scales with sqrt(games), not
    linearly, mu scales linearly.

    start_share is the chance the player actually plays in any one of
    his team's games, 1.0 for a skater who's in the lineup every night.
    A goalie only starts some of his team's games, and whether he
    starts at all is an extra source of week-to-week uncertainty on
    top of how he plays when he does. Per game the player scores X
    with probability s, else 0, so the mean is s*mu and the variance
    is s*sigma^2 + s*(1-s)*mu^2, summed over the week's games. At
    s=1.0 this reduces exactly to the plain sqrt(games) scaling.
    """
    if not 0 <= start_share <= 1:
        raise ValueError(f"start_share must be between 0 and 1, got {start_share}")
    if games_this_week == 0 or start_share == 0:
        return 0.0, 0.0

    weekly_mu = per_game_mu * start_share * games_this_week
    per_game_variance = (start_share * per_game_sigma**2
                         + start_share * (1 - start_share) * per_game_mu**2)
    weekly_sigma = (games_this_week * per_game_variance) ** 0.5
    return weekly_mu, weekly_sigma


def scale_estimates_to_week(estimates, games_this_week, start_share=1.0):
    """
    Takes a per-game estimates dict from get_player_estimates and
    returns a copy with both the season and recent mu/sigma converted
    to weekly totals, so the result can go straight into
    compare_players unchanged. Adds games_this_week to the dict.
    """
    scaled = dict(estimates)
    for kind in ("season", "recent"):
        weekly_mu, weekly_sigma = weekly_from_per_game(
            estimates[f"{kind}_mu"], estimates[f"{kind}_sigma"], games_this_week, start_share
        )
        scaled[f"{kind}_mu"] = weekly_mu
        scaled[f"{kind}_sigma"] = weekly_sigma
    scaled["games_this_week"] = games_this_week
    return scaled


def compare_weekly(estimates_a, games_a, estimates_b, games_b,
                    label_a="Player A", label_b="Player B", use="season",
                    start_share_a=1.0, start_share_b=1.0):
    """
    Probability that player A outscores player B over one fantasy week,
    given how many games each one's team plays that week. A player
    with four games against a player with three gets a real edge
    here that compare_players, which is per game, can't see. Weekly
    totals are also closer to normal than single games are (sums of
    several games), so the normality assumption sits a little easier.
    """
    return compare_players(
        scale_estimates_to_week(estimates_a, games_a, start_share_a),
        scale_estimates_to_week(estimates_b, games_b, start_share_b),
        label_a, label_b, use=use,
    )


def adjust_goalie_for_opponent(opponent_team, team_shot_rates, league_avg_shots,
                                 fit_intercept, fit_slope, sv_weight, ga_weight):
    """
    Computes the fantasy point adjustment for a goalie facing a given
    opponent, based on that opponent's typical shot volume relative to
    the league average, and the league-wide fitted shots-vs-save-
    percentage relationship (see METHODOLOGY.md).

    This is fully parameterized rather than reaching for globals, so
    the caller must supply:
    - team_shot_rates: DataFrame with columns 'team', 'shots_generated_per_game'
    - league_avg_shots: the league-wide average of that column
    - fit_intercept, fit_slope: from the fitted shots-vs-save-pctg line
    - sv_weight, ga_weight: this league's point values for SV and GA

    team_shot_rates and the fit coefficients are expensive to compute
    (a full pass over every goalie in the league), consider computing
    them once and reusing across all three leagues, rather than
    recomputing per league.
    """
    if opponent_team not in team_shot_rates["team"].values:
        return 0.0

    projected_shots = team_shot_rates.loc[
        team_shot_rates["team"] == opponent_team, "shots_generated_per_game"
    ].iloc[0]

    def project_save_pctg(shots_against):
        return fit_intercept + fit_slope * shots_against

    save_pctg_at_league_avg = project_save_pctg(league_avg_shots)
    save_pctg_at_projected = project_save_pctg(projected_shots)

    shots_delta = projected_shots - league_avg_shots
    extra_saves_volume = shots_delta * save_pctg_at_league_avg
    extra_ga_volume = shots_delta * (1 - save_pctg_at_league_avg)

    save_pctg_delta = save_pctg_at_projected - save_pctg_at_league_avg
    extra_saves_quality = save_pctg_delta * projected_shots
    extra_ga_quality = -save_pctg_delta * projected_shots

    adjustment = (
        (extra_saves_volume + extra_saves_quality) * sv_weight +
        (extra_ga_volume + extra_ga_quality) * ga_weight
    )
    return adjustment
