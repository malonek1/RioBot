from pydantic import BaseModel, ConfigDict


class Tag(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # All Tag fields are optional — Tag is not directly used in any logic yet
    id: int = 0
    name: str = ""
    type: str = ""
    desc: str = ""
    active: bool = True
    comm_id: int = 0
    date_created: int = 0
    gecko_code: str = ""
    gecko_code_desc: str = ""


class TagSet(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Required — used in mode filtering and lookups
    id: int
    name: str
    comm_type: str
    start_date: float
    end_date: float

    # Optional — modeled for future use
    comm_id: int = 0
    gecko_code: str = ""
    tag_ids: list[int] = []
    tags: list[Tag] = []
