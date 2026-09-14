# Back-to-Back Goalie Adjustment

Status: tested, not implemented, insufficient evidence

## What was tried
Back-to-back starts were flagged directly from each goalie's own game
log (a rest gap of one day or less between consecutive appearances).
Fantasy points on back-to-back starts were then pooled across every
goalie with a reasonable sample size (142 goalies, minimum 15 games
each) and compared against all other starts.

## Result
- Back-to-back starts: 53 games, average 1.90 fantasy points
- All other starts: 2,521 games, average 2.24 fantasy points
- Observed difference: -0.34 fantasy points
- Two-sample t-test: p = 0.560

A p-value that high means this data is entirely consistent with there
being no real difference at all between back-to-back and rested
performance. The observed -0.34 gap is well within what's expected
from random noise given only 53 back-to-back games league-wide in a
season.

A secondary check looked at whether the back-to-back bucket was
dominated by a small number of specific (likely backup) goalies, which
would suggest the effect, if any, reflects who plays back-to-backs
rather than fatigue itself. 36 distinct goalies contributed at least
one back-to-back game out of 53 total, reasonably spread rather than
concentrated in a handful of players, so that specific selection bias
doesn't look like the dominant explanation. The bigger issue is simply
sample size.

## Why this isn't built into v1
53 back-to-back games league-wide in a season isn't enough to detect
an effect of this likely size. If a real effect exists, even a
meaningful one, distinguishing it from noise would need either more
seasons of pooled data or a substantially larger sample than one
season alone provides.

## Revisit when
Once multiple seasons of pooled back-to-back data are available, or if
the weekly prediction review process surfaces goalies on back-to-backs
consistently underperforming their season-level mu, a real pattern
worth then testing formally rather than assumed from a small sample.
