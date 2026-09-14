# Injury / Missed Game Detection

Status: noted, not built yet

## The problem
The NHL API's roster endpoint doesn't distinguish healthy players from
injured ones. Injured reserve is a roster designation, not a removal,
so injured players still show up as normal on a team's roster. There's
no clean structured injury field to pull either, the league is often
vague publicly anyway ("upper body injury," no return date).

## The idea
Instead of relying on an injury flag that doesn't really exist,
compare a player's game log against their team's actual schedule. If
the team played and the player has no entry for that game, that's a
signal worth surfacing, could be injury, a healthy scratch, or a
minors assignment, but either way it means "didn't play when
expected," which is the actually useful thing for lineup and waiver
decisions, regardless of the specific cause.

## Why it's not built now
This needs a team schedule pull and a join against each player's game
log, a small pipeline of its own, rather than an extension of the
existing caching or cleaning work. Better to prioritize the core
model's remaining pieces (skater opponent strength, category league
support) before this, since those affect prediction quality directly,
while this affects a secondary "why is this player projected low"
explanation.

## Revisit when
Once the weekly prediction cycle is running, if a specific prediction
miss turns out to be explained by an unflagged missed game, that's a
concrete case worth pointing to when prioritizing this.
