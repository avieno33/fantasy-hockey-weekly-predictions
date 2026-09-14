# Goalie-Specific Shot-Volume Slopes (Partial Pooling)

Status: explored, promising, not yet wired into the main pipeline

## The idea
The core opponent-shot-volume adjustment (shots faced vs. save
percentage, r=0.260 league-wide) applies the same shift to every
goalie, since no single goalie's season provides enough data to fit
their own slope reliably. This note explores whether goalies actually
do differ from each other in this relationship, and whether that
difference is usable.

## What was tried
Rather than fitting each goalie's own slope from their data alone
(too few games per shot-volume bucket to trust) or refusing to
differentiate goalies at all, a partial-pooling approach blends each
goalie's own fitted slope with the league-wide slope, weighted by how
many of their own games are available (a shrinkage constant of k=200,
deliberately large since a slope is a much noisier thing to estimate
than a mean).

## Result
Tested on four goalies individually (Vasilevskiy, Swayman, Wedgewood,
Brossoit), all three with real samples showed blended slopes flatter
than the league average, elite/established starters appearing less
dependent on shot volume for their save percentage than the league as
a whole. Brossoit, with only 1 game, correctly fell back entirely to
the league slope (the partial-pooling guard for n < 5 games).

Extended to all 67 goalies with sufficient full-game samples: blended
slope correlates negatively with average save percentage, r=-0.284,
p=0.0199. Real and statistically significant, but modest, r-squared is
under 0.09, meaning save percentage alone explains a small fraction of
the variation in slope. Plenty of individual exceptions exist in both
directions.

## Known caveat
There's a mild circularity risk worth flagging: blended slope and
average save percentage for a given goalie are both derived from the
same underlying games, so part of the correlation could reflect how
the blending interacts with a goalie's own noisy fit, rather than a
fully independent confirmation of "better goalies have flatter
slopes." Not chased down further yet.

## Why this isn't wired into the main pipeline yet
The core, league-wide adjustment already ships and works. This
refinement is real but moderate, and the circularity caveat means it's
worth more scrutiny before it replaces the simpler, more defensible
league-wide shift in `project_final_estimate`.

## Revisit when
Decide whether to swap in each goalie's own blended slope (instead of
the flat league slope) in the final estimate function, once either
more seasons of data exist to shrink the circularity concern, or a
cleaner way to validate the finding independently is found (e.g.,
checking it against next season's actual performance rather than the
same season's data used to fit it).
