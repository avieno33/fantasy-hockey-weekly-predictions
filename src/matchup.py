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


def weekly_from_per_game(per_game_mu, per_game_sigma, games_this_week):
    """
    Converts a per-game mu/sigma into a weekly total. Variance adds
    across independent games, so sigma scales with sqrt(games), not
    linearly, mu scales linearly. NOT YET TESTED end to end, confirm
    against a hand-checked example before trusting it in week01.
    """
    if games_this_week == 0:
        return 0.0, 0.0
    weekly_mu = per_game_mu * games_this_week
    weekly_sigma = per_game_sigma * (games_this_week ** 0.5)
    return weekly_mu, weekly_sigma


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
