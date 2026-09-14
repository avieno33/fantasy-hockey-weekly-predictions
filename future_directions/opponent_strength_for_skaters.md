# Opponent Strength Adjustment for Skaters

Status: planned, next priority once the base model (v1) is complete

## The idea
Goalies get an opponent-strength adjustment based on the opponent's
offense, goals (and shots) generated per game. Skaters need the mirror
version, an adjustment based on the opponent's defense, goals and
shots allowed per game. A mid-level scorer facing a weak defensive
team should be expected to produce more than the same player facing a
shutdown defense.

## Why this wasn't built alongside goalies
The team-level stats pull needed for this (goals-against and, per the
goalie work, shots-against per team) is largely the same data used for
the goalie adjustment, so the data layer is shared. But applying it
correctly to skaters is its own piece of work: deciding how strongly
to weight it against a player's own mu/sigma, and testing it with the
same rigor the goalie adjustment went through (checking for confounds,
verifying against a real correlation, not assuming the effect exists).
Treating it as its own build rather than folding it in on top of an
already large goalie-adjustment session.

## What the goalie work suggests about how to approach this
The goalie side went through several rounds of "does this actually
hold up" before landing on something real:
- A simple opponent-goals metric alone was weak (the goalie equivalent,
  opponent goals-for, only reached r=-0.137).
- The stronger relationship came from something more specific (shots
  faced vs. save percentage, r=0.260), not just raw scoring totals.
- Confounds mattered: small-sample arithmetic effects and selection
  effects (who plays in which situations) both needed to be ruled out
  before trusting the number.

The skater version should follow the same process: test a few
candidate metrics (opponent goals-against per game, opponent shots
allowed per game, maybe opponent penalty minutes for a power-play
angle) against real fantasy point outcomes, check for confounds
(e.g., a skater's own team's playstyle could correlate with strength
of schedule in ways that confuse the picture), and only build in
what's statistically real, not what's merely intuitive.

## Priority
Marked as the next thing to build immediately after the base model
(current sections through the goalie adjustments) is finished and
stable, not a someday item.
