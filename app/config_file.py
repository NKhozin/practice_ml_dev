import dill

config_data = {
    "models_path": {
        "ctb_cl": "C:/Users/User/PycharmProjects/pythonProject2/data/ctb_cl.dill",
        "rf_cl": "C:/Users/User/PycharmProjects/pythonProject2/data/rf_cl.dill",
        "knn_cl": "C:/Users/User/PycharmProjects/pythonProject2/data/knn_cl.dill",
    },
    "models_price": {
        "ctb_cl": 30,
        "rf_cl": 20,
        "knn_cl": 10,
    },
    "SECRET_KEY": "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
    "ALGORITHM": "HS256",
    "data_path": "C:/Users/User/PycharmProjects/pythonProject2/data/for_predict.csv"
}


def load_model(path_name):
    with open(path_name, "rb") as file:
        ctb_cl = dill.load(file)
    return ctb_cl
