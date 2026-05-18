from pydantic import BaseModel, ConfigDict


class PitchingStats(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Required — used in calc_slash_line and display
    batters_faced: int
    outs_pitched: int
    hits_allowed: int
    runs_allowed: int
    strikeouts_pitched: int
    walks_bb: int
    walks_hbp: int

    # Optional — modeled for future use
    total_pitches: int = 0
    strikes: int = 0
    balls: int = 0
    star_pitches_thrown: int = 0
