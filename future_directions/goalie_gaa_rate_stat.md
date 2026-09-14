# Goalie GAA (Goals Against Average) Scoring

Status: known gap, not scored, not yet addressed

## The problem
GAA is a rate stat computed across multiple games (goals against per
60 minutes, typically), not a single-game value. The scoring pipeline
works game by game, converting one row of raw stats into one fantasy
point total, so a category that's only meaningful aggregated across
games doesn't fit the current per-game scoring model. It's currently
mapped to `None` in the goalie field map and silently excluded from
scoring if a league includes it.

## The idea
If a league scores GAA, it likely wants it evaluated on some rolling
or season-long basis (e.g., "if your goalie's rolling GAA is under
2.50, get X points that week") rather than per game. This would need
its own scoring pathway, separate from the per-game `apply_scoring`
function, probably tied into the mu/sigma estimation step instead,
since that's already where rolling, multi-game aggregates are
computed.

## Why not addressed yet
No custom league scoring tested so far has included GAA (the current
default league config doesn't use it), so this has stayed a documented
gap rather than a blocker. Worth solving properly once there's an
actual scoring config that needs it, rather than guessing at the right
rolling-window design in the abstract.

## Revisit when
If a custom scoring upload includes GAA, at minimum the validation
step should flag it clearly as "recognized but not currently scored"
rather than silently dropping it the same way as a truly unavailable
category like faceoffs.
