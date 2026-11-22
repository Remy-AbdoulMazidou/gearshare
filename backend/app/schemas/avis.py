from pydantic import BaseModel, ConfigDict, Field


class AvisCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    note: int = Field(strict=True, ge=1, le=5)
    commentaire: str | None = Field(default=None, max_length=500)


class AvisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reservation_id: int
    note: int
