import pandas as pd
from geopy.geocoders import Nominatim
from tqdm import tqdm
import time
import os

def add_coordinates_to_data(input_file='vacancies_final_dataset.csv', output_file='vacancies_with_coords.csv'):
    """
    Добавляет столбцы с широтой и долготой к датасету вакансий.
    """
    if not os.path.exists(input_file):
        print(f"Ошибка: Исходный файл {input_file} не найден.")
        return

    df = pd.read_csv(input_file)
    
    # Создаем "очищенное" поле города
    df['city_clean'] = df['city'].apply(lambda x: str(x).split('(')[0].strip())

    # Получаем список уникальных городов для геокодирования
    unique_cities = df['city_clean'].unique()
    
    # Инициализируем геокодер
    geolocator = Nominatim(user_agent="hh_vacancy_analyzer_project")
    
    coordinates = {}
    
    print(f"Начинаем геокодирование {len(unique_cities)} уникальных городов...")
    
    for city in tqdm(unique_cities, desc="Геокодирование городов"):
        try:
            # Добавляем "Россия" для точности
            location = geolocator.geocode(f"{city}, Россия")
            if location:
                coordinates[city] = (location.latitude, location.longitude)
            else:
                coordinates[city] = (None, None)
        except Exception as e:
            print(f"Ошибка при обработке города {city}: {e}")
            coordinates[city] = (None, None)
        
        # Важно: делаем паузу, чтобы не нарушать политику использования API
        time.sleep(1)

    # Добавляем координаты в основной DataFrame
    df['latitude'] = df['city_clean'].map(lambda c: coordinates.get(c, (None, None))[0])
    df['longitude'] = df['city_clean'].map(lambda c: coordinates.get(c, (None, None))[1])

    # Удаляем временный столбец
    df = df.drop(columns=['city_clean'])
    
    df.to_csv(output_file, index=False)
    print(f"\nГотово! Новый файл с координатами сохранен как {output_file}")
    
    # Считаем, сколько городов не нашлось
    failed_count = df['latitude'].isnull().sum()
    if failed_count > 0:
        print(f"Не удалось определить координаты для {failed_count} записей.")

if __name__ == '__main__':
    add_coordinates_to_data()