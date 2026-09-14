# Category League Support

Status: planned, not started

## The idea
Extend the custom scoring layer to support head-to-head category
leagues (win or lose each stat category against an opponent for the
week), not just points leagues (sum every stat into one weighted
total).

## Why it's separate from the points-league scoring work
Category leagues are a genuinely different scoring paradigm, you're
not summing to one number, you're comparing category by category. This
touches the matchup comparison logic (the P(A > B) framework), not
just the scoring config and validation layer, since "who wins" in a
category league is a multi-dimensional comparison, not a single
probability. Scoped as its own piece of work rather than folded into
the initial custom-scoring feature.

## What would need to change
- Scoring config format would need a way to express "these categories
  matter for head-to-head comparison" rather than a single set of
  point weights.
- The comparison model would need to produce a probability (or
  expected category-win count) per category, then aggregate across
  categories for an overall matchup call, rather than one P(A > B) on
  a single combined point total.
- Validation logic (checking a custom upload against known Yahoo
  abbreviations) already exists and should be reusable as-is.

## Revisit when
Worth prioritizing based on actual demand, if this project is shared
and someone in a category league wants to use it, that's a concrete
reason to build it before it's otherwise scheduled.
