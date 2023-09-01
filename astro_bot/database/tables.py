from sqlalchemy import BigInteger, Boolean, Column, MetaData, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData(schema="public")
Base = declarative_base(metadata=metadata)


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    send_apod = Column(Boolean, nullable=False, default=False)


class Rovers(Base):
    __tablename__ = "rovers"

    name = Column(String(30), primary_key=True)
    data = Column(JSONB, nullable=False, default="{}")
