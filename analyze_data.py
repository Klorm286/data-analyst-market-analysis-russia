import pandas as pd
import numpy as np
import json
import re
from bs4 import BeautifulSoup # Библиотека для очистки HTML

# Настройки для удобного вывода
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 50)

def load_vacancies_to_dataframe(file_path='vacancies_detailed.json'):
    """Загружает данные из JSON-файла с детальной информацией."""
    try:
        with open(file_path, 'r', encoding='utf8') as f:
            data = json.load(f)
        return pd.json_normalize(data)
    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден. Сначала запустите enrich_data.py")
        return None

def clean_and_prepare_data(df):
    """Базовая очистка и подготовка столбцов."""
    columns_to_keep = [
        'id', 'name', 'area.name', 'salary.from', 'salary.to', 
        'salary.currency', 'salary.gross', 'experience.name', 
        'employment.name', 'description', 'key_skills', 'alternate_url'
    ]
    existing_columns = [col for col in columns_to_keep if col in df.columns]
    df_cleaned = df[existing_columns].copy()

    rename_map = {
        'area.name': 'city', 'salary.from': 'salary_from', 'salary.to': 'salary_to',
        'salary.currency': 'salary_currency', 'salary.gross': 'salary_gross',
        'experience.name': 'experience', 'employment.name': 'employment'
    }
    df_cleaned = df_cleaned.rename(columns=rename_map)

    # Зарплата
    df_cleaned['salary_from'] = np.where(df_cleaned['salary_gross'] == False, df_cleaned['salary_from'] * 1.15, df_cleaned['salary_from'])
    df_cleaned['salary_to'] = np.where(df_cleaned['salary_gross'] == False, df_cleaned['salary_to'] * 1.15, df_cleaned['salary_to'])
    df_cleaned['salary_avg'] = df_cleaned[['salary_from', 'salary_to']].mean(axis=1)
    df_cleaned['salary_avg'] = df_cleaned['salary_avg'].fillna(df_cleaned['salary_from']).fillna(df_cleaned['salary_to'])
    
    df_cleaned = df_cleaned[df_cleaned['salary_currency'] == 'RUR'].copy()
    df_cleaned = df_cleaned.drop(columns=['salary_from', 'salary_to', 'salary_currency', 'salary_gross'])
    
    return df_cleaned

def extract_skills_from_detailed_data(df):
    """
    Извлекает навыки из key_skills и полного описания, очищенного от HTML.
    """
    # 1. Обработка key_skills
    def get_skills_from_list(skill_list):
        if isinstance(skill_list, list):
            return ', '.join([skill['name'] for skill in skill_list]).lower()
        return ''
    
    df['key_skills_str'] = df['key_skills'].apply(get_skills_from_list)

    # 2. Очистка HTML из описания
    def clean_html(html_text):
        if html_text:
            # Используем BeautifulSoup для корректного извлечения текста
            soup = BeautifulSoup(html_text, 'html.parser')
            return soup.get_text(separator=' ', strip=True).lower()
        return ''
        
    df['description_text'] = df['description'].apply(clean_html)

    # 3. Объединяем все текстовые поля для поиска
    df['full_text'] = df['name'].str.lower() + ' ' + df['key_skills_str'] + ' ' + df['description_text']
    
    # 4. Поиск навыков
    skills_patterns = {
        'SQL': r'sql', 'Python': r'python|питон', 'Pandas': r'pandas',
        'Excel': r'excel|эксель', 'Power BI': r'power\s?bi', 'Tableau': r'tableau',
        'A/B Tests': r'a/b|а/б|\bab\b', 'Machine Learning': r'ml|machine learning|машинн.*обучен',
        'Git': r'\bgit\b', 'English': r'english|английск'
    }

    for skill_name, pattern in skills_patterns.items():
        df[f'skill_{skill_name}'] = df['full_text'].str.contains(pattern, regex=True)

    # 5. Удаляем временные столбцы
    df = df.drop(columns=['key_skills', 'description', 'key_skills_str', 'description_text', 'full_text'])
    
    return df

if __name__ == '__main__':
    # Установка BeautifulSoup: pip install beautifulsoup4
    df_raw_detailed = load_vacancies_to_dataframe()
    
    if df_raw_detailed is not None:
        print("Загрузка и базовая очистка детальных данных...")
        df_cleaned = clean_and_prepare_data(df_raw_detailed)
        print(f"Вакансий с зарплатой после очистки: {len(df_cleaned)}")
        
        print("Извлечение навыков из полных описаний...")
        df_final = extract_skills_from_detailed_data(df_cleaned)
        
        print("\n--- ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ АНАЛИЗА ---")
        skill_columns = [col for col in df_final.columns if col.startswith('skill_')]
        
        print("\nТоп востребованных навыков (на основе полных данных):")
        skills_popularity = df_final[skill_columns].mean().sort_values(ascending=False) * 100
        print(skills_popularity.round(1).astype(str) + '%')

        # Сохраним итоговый датасет в CSV для дальнейшего анализа или визуализации
        final_csv_path = 'vacancies_final_dataset.csv'
        df_final.to_csv(final_csv_path, index=False, encoding='utf-8-sig')
        print(f"\nИтоговый датасет сохранен в файл: {final_csv_path}")