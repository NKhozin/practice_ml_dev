from sqlalchemy import Column, Float, ForeignKey, Integer, String

from database.db import Base, Session, engine


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, unique=True)
    hashed_password = Column(String)
    balance = Column(Integer)


class Predict(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("users.username"), index=True)
    model_name = Column(String, index=True)
    temperature = Column(Float)
    humidity = Column(Float)
    co2_cos_ir_value = Column(Float)
    co2_mg811_value = Column(Float)
    mox1 = Column(Float)
    mox2 = Column(Float)
    mox3 = Column(Float)
    mox4 = Column(Float)
    co_value = Column(Float)
    prediction = Column(Integer)


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)


def create_tables():
    Base.metadata.create_all(engine)
