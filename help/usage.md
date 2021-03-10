```prolog
Usage:
    `!roll n [options]` posts results as markdown text
    `!rolli n [options]` posts results as a transparent PNG image

Options (case insensitive):
    `rr`    ReRoll: rerolls matching dice until they cease to appear.
                `!roll 6 rr=1` rerolls 1s until there are none left
                `!roll 6 rr<7` rerolls `{ 1, 2, 3, 4, 5, 6 }` until none are left
                rerolled dice DO NOT contribute to results

    `ro`    Reroll Once: as `rr` but each die is only rerolled once.

    `do`    Double: matching faces are counted as 2 successes instead of 1.
                `!roll 6 do>7` counts 8s, 9s and 10s as double-successes.
                `!roll 6 do=7` counts only 7s as double-successes
                default: `=10`

    `fs`    Faces Subtract: matching faces subtract from accumulated successes.
                `!roll 5 fs<3` would subtract 1s and 2s from successes

    `+N`,   Adds or Subtracts successes to/from the final result, minimum of zero.
    `-N`        `!roll 2 -3` would roll 2 dice and subtract 3 successes from the result.
                `!roll 5 +1` would roll 5 dice and add 1 success to the result.

    `*N`,   Multiplies or Divides the final result by 'N'.
    `/N`        you can specify 'up' or 'dn' for the result to be rounded up or rounded down.
                default: rounded up.

    `stunt` applies a level 1, 2 or 3 stunt to the roll
                `stunt 1` provides  +2 dice
                `stunt 2` provides  +2 dice + 1 success
                `stunt 3` provides  +2 dice + 2 successes

    `damage`    treats roll as a damage roll: 10s are not doubled unless explicitly specified.
```