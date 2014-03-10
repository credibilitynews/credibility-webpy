from sqlalchemy.ext.declarative import declarative_base
from db import engine
Base = declarative_base()
Base.extend_existing = True

from models.user import User
users_table = User.__table__
metadata = Base.metadata


if __name__ == "__main__":
    metadata.create_all(engine)
