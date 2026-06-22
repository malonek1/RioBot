from pydantic import BaseModel, ConfigDict


class QueuedPlayer(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Required — identity, display and matching all depend on these.
    discord_id: str
    name: str
    rating: float
    joined_at: float

    # Optional — internal bookkeeping, defaulted.
    afk_reminded: bool = False


class MatchAnnouncement(BaseModel):
    """A committed match waiting to be announced outside the lock."""
    game_type: str
    number: int
    # `searcher` is the player whose search produced the match; `opponent` is
    # the best match found. This mirrors the original player_1/player_2 roles.
    searcher: QueuedPlayer
    opponent: QueuedPlayer
