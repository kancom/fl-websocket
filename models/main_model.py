import datetime

from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import MetaData, Table
from sqlalchemy.types import JSON, DateTime

mymetadata = MetaData()
Base = declarative_base(metadata=mymetadata)


class ExchRsp(Base):
    __table__ = Table(
        "responses",
        Base.metadata,
        Column("id", Integer, autoincrement=True, primary_key=True),
        Column("dt", DateTime, default=datetime.datetime.now),
        Column("data", JSON),
    )
