from pydantic import BaseModel


class StatusFDO(BaseModel):
    status: str
    message: str
