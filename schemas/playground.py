from typing import Optional

from pydantic import BaseModel, ConfigDict


class PlaygroundBase(BaseModel):
    title: str = "Untitled Playground"
    language: str = "python"
    code: str = ""
    stdin: str = ""
    is_public: bool = True
    user_id: Optional[int] = None


class PlaygroundCreate(PlaygroundBase):
    pass


class PlaygroundUpdate(BaseModel):
    title: Optional[str] = None
    language: Optional[str] = None
    code: Optional[str] = None
    stdin: Optional[str] = None
    is_public: Optional[bool] = None
    user_id: Optional[int] = None


class PlaygroundRunRequest(BaseModel):
    code: Optional[str] = None
    stdin: Optional[str] = None
    language: Optional[str] = None


class PlaygroundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int]
    title: str
    language: str
    code: str
    stdin: str
    last_output: Optional[str]
    last_error: Optional[str]
    is_public: bool