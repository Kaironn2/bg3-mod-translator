from sqlmodel import SQLModel, Field

class En_Ptbr(SQLModel, table=True):
    id: int = Field(primary_key=True)
    en: str
    ptbr: str
    mod: str

