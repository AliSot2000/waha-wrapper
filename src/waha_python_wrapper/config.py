from pydantic import BaseModel


class WAHAConfig(BaseModel):
    waha_url: str = "http://localhost:3000"


cfg = WAHAConfig()
