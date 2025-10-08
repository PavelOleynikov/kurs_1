import pandas as pd

from src.views import main_page
from src.services import service_search
from src.reports import spending_by_category
from config import PATH_TO_EXCEL

df = pd.read_excel(PATH_TO_EXCEL)  # читаем файл xlsx и получаем объект DataFrame
list_dict = df.to_dict(orient="records")  # преобразуем df в список словарей

if __name__ == "__main__":
    # print(main_page("2021-05-02 15:30:00"))
    print(service_search(list_dict, "жкх"))
    # print(spending_by_category(df, "Аптеки", "15.04.2020"))
