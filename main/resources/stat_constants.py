"""Constants for the advanced batting/pitching metrics (wOBA / wRC+ / pitching
index) and the opponent-quality (strength-of-schedule) adjustment. The metric
logic lives in helpers/sabermetrics.py; the adjustment in
helpers/opponent_adjustment.py."""

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
# total runs allowed / total batters faced (see helpers/sabermetrics.league_runs_per_pa).
DEFAULT_LEAGUE_RUNS_PER_PA = 0.16961480888026817

# --- Opponent-quality adjustment tuning -------------------------------------
# The adjustment is additive on the run scale: facing tougher competition raises
# the skill index. Opponent quality is measured leave-one-out from the game log
# (runs per inning). See helpers/opponent_adjustment.py for the model.

# Transfer coefficient. 1.0 = full additive transfer (the principled value, and
# validated across three seasons once the opponent input is de-confounded via LOO;
# higher values overfit on individual seasons). Lower values dampen uniformly.
OPPONENT_TRANSFER_COEFF = 1.0

# Per-opponent reliability: the innings count at which an opponent's run rate is
# trusted halfway; below it the rate is regressed toward league. ~90 innings
# (~400 batters faced), in line with the measured stabilization of run rate.
OPPONENT_REGRESSION_INN = 90

# Schedule reliability: the number of games at which a player's strength-of-
# schedule estimate is trusted halfway. Thin schedules are damped toward zero.
SCHEDULE_REGRESSION_GAMES = 10

# Most-recent games fetched per mode (in one bulk call) to build every user's
# opponent schedule. Modes are season-scoped, so this comfortably covers a full
# season — the largest live mode is ~1.1k games. Raise it if a season ever
# approaches this many games (older games would otherwise drop out of schedules).
GAME_LOG_LIMIT = 5000
