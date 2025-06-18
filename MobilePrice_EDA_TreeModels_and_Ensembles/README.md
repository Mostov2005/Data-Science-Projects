# Анализ характеристик мобильных телефонов и классификация (MobilePrice_EDA_TreeModels_and_Ensembles)

## 🔗 Ссылки
- [Датасет на Kaggle](https://www.kaggle.com/datasets/iabhishekofficial/mobile-price-classification)
- [Решение](https://www.kaggle.com/code/mostov/mobileprice-eda-treemodels-and-ensembles)

## Датасет

Набор содержит характеристики мобильных телефонов и ценовой диапазон, представленный целевой меткой `price_range` (0 — low cost, 1 — medium cost, 2 — high cost, 3 — very high cost). Признаки включают такие параметры, как объём памяти, размеры экрана, наличие 4G/3G, камера, аккумулятор и другие.

## Задачи анализа

1. Изучение структуры и содержимого набора данных  
2. Подготовка данных для классификации:
   - Обработка и удаление нерелевантных или дублирующихся данных  
   - Отделение целевого признака `price_range`
   - Разделение данных на обучающую и тестовую выборки  
3. Обучение модели `DecisionTreeClassifier`  
4. Оценка качества предсказаний с использованием метрик: accuracy, precision, recall, f1-score  
5. Визуализация дерева решений и анализ важности признаков  
6. Нормализация данных с последующим обучением модели на нормализованных данных  
7. Подбор гиперпараметров модели с помощью `RandomizedSearchCV`  
8. Построение модели с оптимальными параметрами
9. Применение и сравнение ансамблевых методов:
    - `RandomForestClassifier`
    - `AdaBoostClassifier`
    - `GradientBoostingClassifier` / `HistGradientBoostingClassifier`
10. Stacking

