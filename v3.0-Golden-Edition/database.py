# database.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from config import DB_FILE

engine = create_engine(f'sqlite:///{DB_FILE}', echo=False)

@event.listens_for(engine, "connect")
def enable_fk(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

Session = sessionmaker(bind=engine)

def get_session():
    return Session()

def init_database():
    from models import Base
    Base.metadata.create_all(engine)