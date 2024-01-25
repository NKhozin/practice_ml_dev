from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError

from database.db import Session
from database.models import Predict, Token, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_username(username: str):
    """Функция для получения пользователя по имени пользователя"""
    db = Session()
    result = db.query(User).filter(User.username == username).first()
    db.close()
    return result


def get_password_hash(password):
    """Функция получение хэша пароля"""
    return pwd_context.hash(password)


def add_user(username: str, password: str):
    """Функция для добавления нового пользователя в таблицу"""
    db = Session()
    balance = 100
    hashed_password = get_password_hash(password)
    db_record = User(username=username, hashed_password=hashed_password, balance=balance)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    db.close()
    return db_record


def add_access_token(user_id: int, access_token: str):
    """Функция для добавления нового пользователя в таблицу"""
    db = Session()
    db_record = Token(access_token=access_token, user_id=user_id)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    db.close()
    return db_record


def get_token_by_user_id(user_id: int):
    """Функция получения access_token по user_id"""
    db = Session()
    result = db.query(Token).filter(Token.user_id == user_id).first()
    db.close()
    return result


def verify_password(plain_password, hashed_password):
    """Функция сравнения паролей"""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    """Функция проверки аутентификации"""
    user = get_user_by_username(username)
    if not user:
        return False
    # if not verify_password(password, user.hashed_password):
    #    return False
    return user


def change_user_balance(username: str, amount: int):
    """Функция для изменения баланса пользователя на заданное число"""
    db = Session()
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.balance += amount
        try:
            new_user_balance = user.balance
            db.commit()
            return {"Status:": "True", "username": username, "balance": new_user_balance}
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    else:
        raise ValueError("User not found")


def get_balance(username: str):
    """Функция для получения баланса пользователя на заданное число"""
    user = get_user_by_username(username)
    return user.balance


def add_predictions(
    username: str,
    model_name: str,
    temperature: float,
    humidity: float,
    co2_cos_ir_value: float,
    co2_mg811_value: float,
    mox1: float,
    mox2: float,
    mox3: float,
    mox4: float,
    co_value: float,
    prediction: int,
):
    """Функция для добавления записи в таблицу Predict"""
    db = Session()
    db_record = Predict(
        username=username,
        model_name=model_name,
        temperature=temperature,
        humidity=humidity,
        co2_cos_ir_value=co2_cos_ir_value,
        co2_mg811_value=co2_mg811_value,
        mox1=mox1,
        mox2=mox2,
        mox3=mox3,
        mox4=mox4,
        co_value=co_value,
        prediction=prediction,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    db.close()
    return db_record
