from typing import Annotated

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta

from database.functions import add_predictions, change_user_balance
from dependencies import get_current_user
from config_file import config_data, load_model
from models import User


ml = APIRouter()


def make_predict(model_name):
    current_time = datetime.now()

    rounded_time = current_time - timedelta(minutes=current_time.minute % 10,
                                            seconds=current_time.second,
                                            microseconds=current_time.microsecond)

    date_list = [rounded_time - timedelta(minutes=x * 10) for x in range(1, 11)]

    data = (
        pd.read_csv("C:/Users/User/PycharmProjects/pythonProject2/data/for_predict.csv", index_col=0)
        .sample(10)
        .round(1)
    )

    if model_name != 'knn_cl':
        data["predict_proba"] = load_model(config_data["models_path"][model_name]).predict_proba(data)[:, 1]
        data["predict"] = np.where(data["predict_proba"] >= 0.9,1,0)
        data = data.drop(["predict_proba"], axis=1)
    else:
        data["predict"] = load_model(config_data["models_path"][model_name]).predict(data)

    data.insert(0, 'Дата', date_list)
    return data


@ml.get("/make_predict/{model_name}")
def predict(model_name: str, current_user: Annotated[User, Depends(get_current_user)]):
    """Получения предскзания по выбранной модели"""

    if model_name in config_data["models_price"]:
        price = config_data["models_price"][model_name]
    else:
        raise HTTPException(status_code=400, detail="Неправильное название модели")

    if current_user.balance < price:
        raise HTTPException(status_code=400, detail="Недостаточно средств")

    predict = make_predict(model_name)

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
