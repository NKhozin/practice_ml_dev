from typing import Annotated

import ast
import hashlib
import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime, timedelta

from database.functions import add_predictions, change_user_balance
from dependencies import get_current_user
from config_file import config_data, load_model
from models import User


ml = APIRouter()


def get_random_state(my_string):
    """Получение уникального random_state для каждого пользователя. Для генерации случайных данных"""
    return int(hashlib.sha256(my_string.encode('utf-8')).hexdigest()[:5], base=16)


def get_data(random_state):
    """Функция получения данных извне. В простом виде считывается из csv"""
    current_time = datetime.now()

    rounded_time = current_time - timedelta(minutes=current_time.minute % 10,
                                            seconds=current_time.second,
                                            microseconds=current_time.microsecond)

    date_list = [rounded_time - timedelta(minutes=x * 10) for x in range(1, 11)]

    data = (
        pd.read_csv("", index_col=0)
        .sample(10, random_state=random_state)
        .round(1)
    )

    data.insert(0, 'Дата', date_list)
    return data


def make_predict(data, model_name):
    if 'Человек в опасности' in data.columns:
        data.drop('Человек в опасности', axis=1, inplace=True)

    data_column = data['Дата'].tolist()
    data.drop('Дата', axis=1, inplace=True)

    if model_name != 'knn_cl':
        data["predict"] = load_model(config_data["models_path"][model_name]).predict(data)
    else:
        data["predict"] = load_model(config_data["models_path"][model_name]).predict(data)

    data.insert(0, 'Дата', data_column)
    return data


@ml.get("/get_last_data", tags=["ml"])
async def predict(current_user: Annotated[User, Depends(get_current_user)]):
    """Получение последних данных"""
    random_state = get_random_state(current_user.username)
    data = get_data(random_state)
    return {
        "status": "success",
        "data": data.to_dict()
        }

import json
@ml.post("/make_predict/{model_name}", tags=["ml"])
async def predict(model_name: str, request: Request, current_user: Annotated[User, Depends(get_current_user)]):
    """Получение предскзания по выбранной модели"""
    json_data = await request.json()

    list_data = json_data["dataset"] #ast.literal_eval(

    data = pd.DataFrame(ast.literal_eval(list_data))

    if model_name in config_data["models_price"]:
        price = config_data["models_price"][model_name]
    else:
        raise HTTPException(status_code=400, detail="Неправильное название модели")

    if current_user.balance < price:
        raise HTTPException(status_code=400, detail="Недостаточно средств")

    predict = make_predict(data, model_name)

    for index, row in predict.iterrows():
        add_predictions(
            username=current_user.username,
            model_name=model_name,
            temperature=row["temperature"],
            humidity=row["humidity"],
            co2_cos_ir_value=row["CO2CosIRValue"],
            co2_mg811_value=row["CO2MG811Value"],
            mox1=row["MOX1"],
            mox2=row["MOX2"],
            mox3=row["MOX3"],
            mox4=row["MOX4"],
            co_value=row["COValue"],
            prediction=row["predict"],
        )

    updated_user_balance = change_user_balance(current_user.username, -price)

    return {
        "status": "success",
        "model_name": model_name,
        "price": price,
        "user": current_user.username,
        "balance": current_user.balance,
        "new_balance": updated_user_balance,
        "predict_dict": predict.to_dict()
    }
