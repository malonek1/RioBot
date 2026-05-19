from models.batting_stats import BattingStats

LINEAR_WEIGHTS = {
    "singles": 0.796,
    "doubles": 1.174,
    "triples": 1.451,
    "homeruns": 1.974,
    "walks_bb": 0.725,
    "walks_hbp": 0.725,
}

LEAGUE_RUNS_PER_PA = 0.16961480888026817


def calc_woba(stats: BattingStats) -> float:
    pa = stats.summary_at_bats + stats.summary_walks_bb + stats.summary_walks_hbp + stats.summary_sac_flys
    if pa == 0:
        return 0
    return (
        stats.summary_singles * LINEAR_WEIGHTS["singles"] +
        stats.summary_doubles * LINEAR_WEIGHTS["doubles"] +
        stats.summary_triples * LINEAR_WEIGHTS["triples"] +
        stats.summary_homeruns * LINEAR_WEIGHTS["homeruns"] +
        stats.summary_walks_bb * LINEAR_WEIGHTS["walks_bb"] +
        stats.summary_walks_hbp * LINEAR_WEIGHTS["walks_hbp"]
    ) / pa
