from sqlalchemy import BigInteger, Boolean, Column, MetaData
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData(schema="public")
Base = declarative_base(metadata=metadata)


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    send_apod = Column(Boolean, nullable=False, default=False)
