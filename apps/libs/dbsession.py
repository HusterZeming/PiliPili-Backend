from sqlalchemy.orm import sessionmaker
from exts import db


class DBSession:

    @staticmethod
    def make_session():
        return sessionmaker(bind=db.get_engine())()
