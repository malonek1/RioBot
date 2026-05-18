from pydantic import BaseModel, ConfigDict


class Game(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Required — actively used in recent_games.py
    home_user: str
    away_user: str
    home_score: int
    away_score: int
    home_captain: str
    away_captain: str
    date_time_start: int
    innings_played: int
    innings_selected: int
    stadium: int
    game_mode: int

    # Optional — modeled for future use
    game_id: int = 0
    date_time_end: int = 0
    winner_incoming_elo: int = 0
    winner_result_elo: int = 0
    loser_incoming_elo: int = 0
    loser_result_elo: int = 0
