"""Constants for advanced batting metrics (wOBA / wRC+) and the opponent-quality
(strength-of-schedule) adjustment. The calculation logic lives in helpers/wrc.py."""

# Linear weights for wOBA. Derived from regression on Project Rio game data
# (they match the values in RioStatParsing's fip.py / xba.py), NOT MLB weights.
LINEAR_WEIGHTS = {
    "singles": 0.796,
    "doubles": 1.174,
    "triples": 1.451,
    "homeruns": 1.974,
    "walks_bb": 0.725,
    "walks_hbp": 0.725,
}

# League runs per plate appearance. Used as the wRC+ denominator and as a fallback
# when a mode's pitching table is empty; normally derived live per mode from
# total runs allowed / total batters faced (see helpers/wrc.league_runs_per_pa).
DEFAULT_LEAGUE_RUNS_PER_PA = 0.16961480888026817

# --- Opponent-quality adjustment tuning -------------------------------------
# The adjustment is additive on the run scale: a batter who faced tougher-than-
# average run prevention gets a higher adjusted wRC+. Two regression layers keep
# small samples from dominating. See helpers/wrc.py for the model.

# Transfer coefficient. 1.0 = full additive transfer (justified by the run-scale
# model); lower values dampen the adjustment uniformly.
OPPONENT_TRANSFER_COEFF = 1.0

# Per-opponent reliability: the batters-faced count at which an opponent's
# run-prevention rate is trusted halfway. Below this it's regressed toward league.
OPPONENT_REGRESSION_BF = 100

# Schedule reliability: the number of games at which a batter's strength-of-
# schedule estimate is trusted halfway. Thin schedules are damped toward zero.
SCHEDULE_REGRESSION_GAMES = 10
