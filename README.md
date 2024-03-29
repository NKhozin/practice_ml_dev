### Мониторинг безопасности одиноких пожилых людей
#### Описание задачи
Задача - создать модель машинного обучения для мониторинга безопасности одиноких пожилых людей на основе данных от датчиков газа, температуры и инфракрасных датчиков движения. Модель должна способна определять аномалии и необычное поведение, которые могут потребовать вмешательства или помощи.
#### ML задачи
- провести входной анализ данных (EDA)
- определить метрики для оценки эффективности модели
- сформировть baseline-модель
- предложить улучшенную модель и вывести ее в продакшн
#### Описание датасета
Датасет содержит данные от датчиков газа и температуры, а также инфракрасных датчиков движения, установленных для мониторинга пожилого человека, проживающего один в собственном доме с 2019-11-06 по 2020-02-13. Измерения проводились с временным разрешением в 20 секунд. Датчики воздуха и газа измеряют температуру, влажность, уровень CO2, CO и MOX. Данные от датчиков позиции бинарны: для каждой комнаты 1 означает обнаружение движения в комнате, в то время как 0 означает возврат сенсора к базовому состоянию. Датасет также включает в себя 19 дней измерений (с 2020-01-25 по 2020-02-13), когда никто не находился в помещении (за исключением случайного посещения 2020-01-29 в 15:00) и используется в качестве эталонных данных. Разрешается использовать не весь набор признаков.
#### Описание сервиса
Сервис предназначен для мониторинга за безопасностью одиноких пожилых людей. Предполагается, что сервис делает запрос к системе дома человека, получает данные датчиков, на основе этих данных предсказывает вероятность того, что что-то произошло.
Классификация осуществяется на выбор из трех моделей: CatBoost, RandomForestClassifier, KNeighborsClassifier.
#### Пример работы сервиса
![Новый проект (1)](https://github.com/NKhozin/practice_ml_dev/assets/92330362/c16acb8a-50a2-4917-9bfd-f4cfa75495a5)
#### Инструкции по запуску

