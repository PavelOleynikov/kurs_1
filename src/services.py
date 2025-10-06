import json

from config import PATH_TO_EXCEL
from src.utils import process_bank_search


def service_search(search: str) -> dict[str, str | list[dict[str, str | float]]]:
    """функция фильтрации операций в категории по строке поиска"""

    result = process_bank_search(PATH_TO_EXCEL, search)

    json_result = json.dumps(result, ensure_ascii=False, indent=4)  # упорядоченный вывод json

    return json_result
