from sqlalchemy import create_engine
from omegaconf import DictConfig, OmegaConf
from typing import Callable, Optional
import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from models.tmdb_request import TMDBRequest

from models.model_base import SqlAlchemyBase

__factory: Optional[Callable[[], Session]] = None

def global_init():
    global __factory

    if __factory:
        return

    conf = OmegaConf.load('config/config.yaml')

    DB_URL = (conf.DATABASE.DATABASE_URL)

    engine = sa.create_engine(DB_URL)
    __factory = orm.sessionmaker(bind=engine)

    # noinspection PyUnresolvedReferences
    from models.tmdb_request import TMDBRequest

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory

    if not __factory:
        raise Exception("You must call global_init() before using this method.")

    session: Session = __factory()
    session.expire_on_commit = False

    return session

global_init()




