from pydantic import BaseModel, Field


class Data(BaseModel):
    class Config:
        orm_mode = True

    max_sol: int = 50
    empty_sols: list[int] = Field(default_factory=list)


class Rover(BaseModel):
    class Config:
        orm_mode = True

    name: str
    data: Data = Field(default_factory=Data)
