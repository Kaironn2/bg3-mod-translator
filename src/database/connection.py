from sqlmodel import SQLModel, create_engine
from src.database.models import En_Ptbr
from src.config.paths import DB_PATH


connection_string = f'sqlite:///{DB_PATH}'
engine = create_engine(connection_string, echo=False)
SQLModel.metadata.create_all(engine, checkfirst=True)
