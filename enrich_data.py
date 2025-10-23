import requests
import json
import time
import os
from tqdm import tqdm # Библиотека для красивого индикатора прогресса

def get_full_vacancy_details(vacancy_id):
    """
    Получает полную информацию о вакансии по ее ID.
    """
    url = f'https://api.hh.ru/vacancies/{vacancy_id}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе вакансии {vacancy_id}: {e}")
        return None

if __name__ == '__main__':
    input_file = 'vacancies.json'
    output_file = 'vacancies_detailed.json'
    
    # Проверяем, существует ли исходный файл
    if not os.path.exists(input_file):
        print(f"Ошибка: Файл {input_file} не найден. Сначала запустите get_vacancies.py")
    else:
        with open(input_file, 'r', encoding='utf8') as f:
            vacancies_list = json.load(f)

        all_detailed_vacancies = []
        
        print(f"Начинаем обогащение данных для {len(vacancies_list)} вакансий...")
        
        # Используем tqdm для отображения прогресс-бара
        for vacancy in tqdm(vacancies_list, desc="Получение детальной информации"):
            vacancy_id = vacancy['id']
            detailed_info = get_full_vacancy_details(vacancy_id)
            
            if detailed_info:
                all_detailed_vacancies.append(detailed_info)
            
            # Пауза между запросами, чтобы не нагружать API
            time.sleep(0.25)
            
        # Сохраняем обогащенные данные
        with open(output_file, 'w', encoding='utf8') as f:
            json.dump(all_detailed_vacancies, f, ensure_ascii=False, indent=4)
            
        print(f"\nОбогащение завершено. {len(all_detailed_vacancies)} вакансий с детальной информацией сохранены в {output_file}.")