from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def __repr__(self):
       return "<User('%s','%s', '%s')>" % (self.name, self.email, self.password)

users_table = User.__table__
metadata = Base.metadata

from db import engine
if __name__ == "__main__":
    metadata.create_all(engine)