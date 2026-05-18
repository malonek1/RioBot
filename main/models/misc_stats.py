from pydantic import BaseModel, ConfigDict


class MiscStats(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Required — used in games/winrate calculations
    home_wins: int
    away_wins: int
    home_loses: int
    away_loses: int

    # Optional — modeled for future use
    game_appearances: int = 0
