import os, web
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.environ['DATABASE_URL'])

Session = sessionmaker(bind=engine)
session = Session()

def load_sqla(handler):
    try:
        return handler()
    except web.HTTPError:
        session.commit()
        raise
    except:
        session.rollback()
        raise
    finally:
        session.commit()