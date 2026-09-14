# Learned Team Strength Rating

Status: idea, noted for later, not scoped yet

## The idea
Rather than a flat or even recency-weighted average of a team's goals
for/against or shots for/against, a model that updates a team's
strength rating game by game based on actual outcomes, closer to an
Elo rating than a moving average. Would let opponent strength reflect
not just recent scoring or shot volume, but recent performance against
strength of schedule, a team that's been beating good teams looks
different than one racking up stats against weak ones, which a simple
average can't distinguish.

## Why not now
This is a genuinely different kind of model than anything else in v1.
Elo-style ratings need their own update rule and starting assumptions,
not just a rolling window or a linear fit. Worth its own dedicated
build once there's time to do it properly, rather than folding it into
the opponent-strength work already underway for goalies and planned
for skaters.

## What's being built instead, for now
For goalies, a league-wide pooled linear relationship (shots faced vs.
save percentage) applied as a shift on top of each goalie's own
baseline, with an optional partial-pooling refinement for
goalie-specific slopes, blending each goalie's own trend with the
league trend based on how much of their own data exists. Simpler,
reuses existing, trusted statistical machinery (the same shrinkage
logic already used for mu/sigma), and captures "this opponent has
been tougher or easier than average" without needing a full ratings
system.

## Revisit when
If the simpler pooled/blended approach proves insufficient once real
weekly predictions accumulate, e.g., if certain teams' true strength
seems to be systematically mis-estimated by a season-long or even
recency-weighted average, that would be a concrete, evidence-based
reason to build the more sophisticated version.
