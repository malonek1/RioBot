from pydantic import BaseModel, ConfigDict


class BattingStats(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Required — used in calc_slash_line and display
    summary_at_bats: int
    summary_hits: int
    summary_singles: int
    summary_doubles: int
    summary_triples: int
    summary_homeruns: int
    summary_rbi: int
    summary_strikeouts: int
    summary_walks_bb: int
    summary_walks_hbp: int
    summary_sac_flys: int
    perfect_hits: int = 0
    nice_hits: int = 0
    sour_hits: int = 0

    # Optional — modeled for future use
    summary_bases_stolen: int = 0
    plate_appearances: int = 0
    singles: int = 0
    doubles: int = 0
    triples: int = 0
    homeruns: int = 0
    rbi: int = 0
    strikeouts: int = 0
    sacflys: int = 0
    outs: int = 0
    fair_hits: int = 0
    foul_hits: int = 0
    gidps: int = 0
    star_hits: int = 0
