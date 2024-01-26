from dash import html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import ast
import pandas as pd
import base64
import io
import numpy as np
import requests
import dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets) #[dbc.themes.BOOTSTRAP]
app.title = 'Elderly Safety App'

# Стартовая страница
index_page = html.Div([
    html.Div([dcc.Link('Регистрация', href='/register')], style={'margin-top': 150}),
    html.Br(),
    html.Div([dcc.Link('Авторизация', href='/login')], style={'margin-top': 15}),
], style={'textAlign': 'center', 'marginTop': 50})

# Страница регистрации
register_page = html.Div([
    html.Div([dcc.Input(id='register-username', type='text', placeholder='Имя пользователя'), dcc.Input(id='register-password', type='password', placeholder='Пароль')]),
    html.Div([dbc.Button("Зарегистрироваться", id="submit-register", n_clicks=0)], style={'textAlign': 'center', 'marginTop': 10}),
    html.Br(),
    html.Div(id='register-message'),
    dcc.Link('Вернуться на стартовую страницу', href='/'),
], style={'textAlign': 'center', 'marginTop': 150})

# Страница авторизации
login_page = html.Div([
    html.Div([dcc.Input(id='login-username', type='text', placeholder='Имя пользователя'), dcc.Input(id='login-password', type='password', placeholder='Пароль')]),
    html.Div([dbc.Button("Авторизоваться", id="submit-login", n_clicks=0)], style={'textAlign': 'center', 'marginTop': 10}),
    html.Br(),
    html.Div(id='login-message'),
    dcc.Link('Вернуться на стартовую страницу', href='/'),
], style={'textAlign': 'center', 'marginTop': 150})


main_page = html.Div([
    html.Div(
        [
                html.Div([html.H4("Мониторинг безопасности одиноких пожилых людей:")], style={'margin-top': 15}),
                html.Div([html.H6("Выбор модели для предсказания:")], style={'margin-top': 10}),
                html.Div([dcc.Dropdown(
                    id="model-name",
                    options=[
                        {"label": "CatBoost Classifier (30 монет)", "value": "ctb_cl"},
                        {"label": "RandomForestClassifier (20 монет)", "value": "rf_cl"},
                        {"label": "KNeighborsClassifier (10 монет)", "value": "knn_cl"},
                    ],
                    value="ctb_cl",
                )], style={'margin-top': 15, 'width': 300}),
                html.Div([dash_table.DataTable(id="my-predict-datatable")], style={'margin-top': 5}),
                html.Div([html.Div(id='predict-message')], style={'margin-top': 5}),
                html.Div(
                    [
                        dbc.Button("Показать данные за последние часы", id="show-data-button", n_clicks=0, style={'width': '350px'})
                    ], style={'margin-top': 5}
                ),
                html.Div([dbc.Button("Получить предсказание", id="predict-button", n_clicks=0, style={'width': '350px'})], style={'margin-top': 5}),
                dcc.Upload(id='upload-data', children=html.Div([html.A('Загрузить свой файл')], style={'margin-top': 5})),

                html.Div([html.H6("Управление балансом")], style={'margin-top': 80}),
                html.Div([dbc.Button('Посмотреть свой баланс', id='balance-button', style={'width': '350px'})], style={'margin-top': 15}),
                html.Div([html.Div(id='balance-output')], style={'margin-top': 5}),
                html.Div([
                    html.Div([dcc.Input(id='replenishment-state', type='text', value=0, style={'width': '50px'})], style={'margin-top': 35}), #, style={'margin-left': 1}
                    html.Div([dbc.Button(id='replenishment-button', n_clicks=0, children='Пополнить баланс', style={'width': '350px'})], style={'margin-top': 5}),
                    html.Div([html.Div(id='replenishment-output')], style={'margin-top': 5}),
                ], style={'margin-top': 15})
            ],
            className="container",
        ),
], style={'textAlign': 'left', 'margin-bottom': 20, 'margin-top': 30})


# Макет приложения
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Store(id='public-tokens', storage_type='session')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/register':
        return register_page
    elif pathname == '/login':
        return login_page
    elif pathname == '/main':
        return main_page
    else:
        return index_page


@app.callback(Output('register-message', 'children'),
              [Input('submit-register', 'n_clicks')],
              [State('register-username', 'value'),
               State('register-password', 'value')])
def register_user(n_clicks, username, password):
    if n_clicks > 0:
        data = {
            'username': username,
            'password': password
        }
        response = requests.post('http://127.0.0.1:8000/user/signup', json=data)
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            return "Поздравляем! Вы успешно зарегистрировались!"
        else:
            text_response = ast.literal_eval(response.text)
            return text_response['detail']
    return dash.no_update


@app.callback([Output('login-message', 'children'),
               Output('url', 'pathname'),
               Output('public-tokens', 'data')],
              [Input('submit-login', 'n_clicks')],
              [State('login-username', 'value'),
               State('login-password', 'value')])
def login_user(n_clicks, username, password):
    if n_clicks > 0:
        data = {
            'username': username,
            'password': password
        }
        response = requests.post('http://127.0.0.1:8000/user/signin', json=data)
        if response.status_code == 200:
            access_token = response.json().get('access_token')
            return 'Успешная авторизация!', '/main', {'access_token': access_token}
        else:
            text_response = ast.literal_eval(response.text)
            return text_response['detail'], {'access_token': 'no_token'}
    return dash.no_update, '/login', {'access_token': 'no_token'}


@app.callback(Output('transaction-table', 'children'),
              [Input('public-tokens', 'modified_timestamp')],
              [State('public-tokens', 'data')])
def display_output(timestamp, data):
    return data["access_token"]


@app.callback(Output('balance-output', 'children'),
              [Input('balance-button', 'n_clicks'),
               Input('public-tokens', 'modified_timestamp')],
              [State('public-tokens', 'data')])
def main_page_buttons(n_click, timestamp, data):
    if n_click:
        access_token = data["access_token"]
        header = {"Authorization": f"bearer {access_token}"}
        response = requests.get('http://127.0.0.1:8000/user/balance', headers=header)
        if response.status_code == 200:
            text_response = ast.literal_eval(response.text)
            balance = text_response["current_user"]["balance"]
            return f"Ваш баланс: {balance}"
        else:
            return "Ошибка получения баланса"


@app.callback(Output('replenishment-output', 'children'),
              [Input('replenishment-button', 'n_clicks'),
               Input('public-tokens', 'modified_timestamp')],
              [State('public-tokens', 'data'),
               State('replenishment-state', 'value')])
def update_output(n_clicks, timestamp, data, amount):
    if n_clicks > 0:
        if not str(amount).isdigit() or (int(amount) < 0):
            return "Некорректный формат числа"
        else:
            access_token = data["access_token"]
            header = {"Authorization": f"bearer {access_token}"}
            response = requests.get(f'http://127.0.0.1:8000/user/change_balance/{amount}', headers=header)
            if response.status_code == 200:
                text_response = ast.literal_eval(response.text)
                balance = text_response["current_user"]["balance"]
                return f"Баланс успешно пополнен на {amount} монет"
            else:
                return "Ошибка авторизации"
    return ""


@app.callback([Output("my-predict-datatable", "data"),
               Output("my-predict-datatable", "columns"),
               Output('predict-message', 'children'),
               Output('show-data-button', 'n_clicks'),
               Output('predict-button', 'n_clicks')],
              [Input('show-data-button', 'n_clicks'),
               Input('predict-button', 'n_clicks'),
               Input('upload-data', 'contents'),
               Input("my-predict-datatable", "data"),
               Input('public-tokens', 'modified_timestamp')],
              [State('public-tokens', 'data'),
               State("model-name", "value"),
               State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def main_predict_buttons(n_click_show, n_click_predict, contents, predict_data, timestamp, data, model_name, list_of_names, list_of_dates):
    print(n_click_show, n_click_predict)
    #print(file_data)

    #Получение исторических данных
    if n_click_show > 0:
        access_token = data["access_token"]
        header = {"Authorization": f"bearer {access_token}"}
        response = requests.get(f'http://127.0.0.1:8000/ml/get_last_data', headers=header)
        response_text = response.text
        response_dict = ast.literal_eval(response_text)

        if "success" in response_text:
            data_dict = response_dict['data']
            data = pd.DataFrame(data_dict)
            return data.to_dict("records"), [{"name": i, "id": i} for i in data.columns], '', 0, 0
        else:
            return pd.DataFrame().to_dict("records"), [], response_dict['detail'], 0, 0

    #Получение предсказания по загруженным данным
    if n_click_predict > 0 and predict_data:
        access_token = data["access_token"]
        header = {"Authorization": f"bearer {access_token}"}

        post_data = {'dataset': f'{pd.DataFrame(predict_data).to_dict()}'}

        response = requests.post(f'http://127.0.0.1:8000/ml/make_predict/{model_name}', headers=header, json=post_data)
        response_text = response.text

        response_dict = ast.literal_eval(response_text)

        if "success" in response_text:
            predict = pd.DataFrame(response_dict['predict_dict'])
            predict['predict'] = np.where(predict['predict'] == 1, 'Да', 'Нет')
            predict = predict.rename(columns={'predict': 'Человек в опасности'})
            return predict.to_dict("records"), [{"name": i, "id": i} for i in predict.columns], '', 0, 0
        else:
            return pd.DataFrame().to_dict("records"), [], response_dict['detail'], 0, 0

    #Получение предсказание по данным из файла
    if n_click_predict > 0 and contents:

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        unload_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')), index_col=0)

        access_token = data["access_token"]

        header = {"Authorization": f"bearer {access_token}"}
        post_data = {'dataset': f'{unload_data.to_dict()}'}

        response = requests.post(f'http://127.0.0.1:8000/ml/make_predict/{model_name}', headers=header, json=post_data)
        response_text = response.text

        response_dict = ast.literal_eval(response_text)

        if "success" in response_text:
            predict = pd.DataFrame(response_dict['predict_dict'])
            predict['predict'] = np.where(predict['predict'] == 1, 'Да', 'Нет')
            predict = round(predict, 1)
            predict = predict.rename(columns={'predict': 'Человек в опасности'})
            return predict.to_dict("records"), [{"name": i, "id": i} for i in predict.columns], '', 0, 0
        else:
            return pd.DataFrame().to_dict("records"), [], response_dict['detail'], 0, 0
    return pd.DataFrame().to_dict("records"), [], '', 0, 0


if __name__ == "__main__":
    app.run_server("localhost", port=8050, debug=True, use_reloader=True)