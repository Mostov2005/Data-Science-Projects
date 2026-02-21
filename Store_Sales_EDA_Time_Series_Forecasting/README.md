# Продажи в магазине — прогнозирование временных рядов (Store Sales Forecasting)

## 🔗 Ссылки

- [Датасет на Kaggle](https://www.kaggle.com/competitions/store-sales-time-series-forecasting/overview)
- [Решение на Kaggle](https://www.kaggle.com/code/mostov/store-sales-forecasting)

Данные предоставлены в рамках соревнования Store Sales - Time Series Forecasting и содержат исторические продажи сети
магазинов.

## Датасет:

* train.csv — исторические продажи (sales)

* test.csv — данные для построения прогноза

* stores.csv — информация о магазинах

* oil.csv — цены на нефть

* holidays_events.csv — праздники и события

* transactions.csv — количество транзакций

Целевая переменная — `sales` (объём продаж по магазину и категории товара на конкретную дату).

Метрика соревнования — `RMSLE` (Root Mean Squared Logarithmic Error).

## Задачи анализа

### 1. Изучение и подготовка данных

### 2. Предобработка и feature engineering

#### 2.1. Удаление выбросов

#### 2.2. Добавление лагов

#### 2.2.3. Работа с пропусками

### 3. Разделение данных

### 4. Использованные модели

* Random Forest Regressor
* XGBoost
* HistGradientBoostingRegressor
* CatBoost
* LightGBM

### 5. Результаты на валидации
| Модель                        | RMSLE (Validation) |
| ----------------------------- | ------------------ |
| **XGBoost**                   | **0.45406**        |
| LightGBM                      | 0.46532            |
| HistGradientBoostingRegressor | 0.47654            |
| Random Forest Regressor       | 0.47233            |
| CatBoost                      | 0.51605            |


Лучший результат показала модель XGBoost.

### 6. Подбор гиперпараметров

* GridSearch для XGBoost
* GridSearch для LightGBM

### 7. Обучение лучших моделей

7.1. Финальная модель XGBoost
7.2. Финальная модель LightGBM

