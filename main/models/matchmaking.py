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
    """A committed match waiting to be announced outside the lock.

    The two players are interchangeable — matching is symmetric. Which one is
    listed first / assigned home/away is decided cosmetically at render time.
    """
    game_type: str
    player_a: QueuedPlayer
    player_b: QueuedPlayer
