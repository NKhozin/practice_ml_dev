from dash import html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import ast
import pandas as pd
import numpy as np
import requests
import dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
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
                html.Div([html.H4("Кейс 3. Мониторинг безопасности одиноких пожилых людей:")], style={'margin-top': 15}),
                html.Div([html.H6("Выбор модели для предсказания:")], style={'margin-top': 25}),
                html.Div([dcc.Dropdown(
                    id="model-name",
                    options=[
                        {"label": "CatBoost Classifier (30 монет)", "value": "ctb_cl"},
                        {"label": "RandomForestClassifier (20 монет)", "value": "rf_cl"},
                        {"label": "KNeighborsClassifier (10 монет)", "value": "knn_cl"},
                    ],
                    value="ctb_cl",
                )], style={"width": "30%"}),
                html.Div(id='predict-message'),
                dash_table.DataTable(id="my-predict-datatable"),
                html.Div([html.Button("Получить предсказание за последние несколько часов", id="predict-button", n_clicks=0)], style={'margin-top': 15}),
                html.Div([html.Button('Посмотреть свой баланс', id='balance-button')], style={'margin-top': 15}),
                html.Div([html.Div(id='main-output-2')], style={'margin-top': 15}),
                html.Div(id='main-output-3')
            ],
            className="container",
        ),
], style={'textAlign': 'left', 'margin-bottom': 20, 'margin-top': 100})


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


@app.callback(Output('main-output-2', 'children'),
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
            return "Ошибка получения баланса!"


@app.callback([Output("my-predict-datatable", "data"),
               Output("my-predict-datatable", "columns"),
               Output('predict-message', 'children')],
              [Input('predict-button', 'n_clicks'),
               Input('public-tokens', 'modified_timestamp')],
              [State('public-tokens', 'data'),
                State("model-name", "value")])
def main_predict_buttons(n_click, timestamp, data, model_name):
    if n_click > 0:
        access_token = data["access_token"]
        header = {"Authorization": f"bearer {access_token}"}
        response = requests.get(f'http://127.0.0.1:8000/ml/make_predict/{model_name}', headers=header)
        response_text = response.text
        response_dict = ast.literal_eval(response_text)

        if "success" in response_text:

            predict_dict = response_dict['predict_dict']
            predict = pd.DataFrame(predict_dict)
            predict['predict'] = np.where(predict['predict'] == 1, 'Да', 'Нет')
            predict = predict.rename(columns={'predict': 'Человек в опасности'})
            return predict.to_dict("records"), [{"name": i, "id": i} for i in predict.columns], 'Успешно!'
        else:
            return pd.DataFrame().to_dict("records"), [], response_dict['detail']
    return pd.DataFrame().to_dict("records"), [], ''


if __name__ == "__main__":
    app.run_server("localhost", port=8050, debug=True, use_reloader=True)