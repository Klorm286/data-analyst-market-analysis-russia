import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Настройки для красивых графиков
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 7) # Устанавливаем размер графиков
plt.rcParams['font.family'] = 'DejaVu Sans' # Шрифт, поддерживающий кириллицу

def perform_eda(file_path='vacancies_final_dataset.csv'):
    """
    Выполняет исследовательский анализ данных (EDA) и строит графики.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Ошибка: Файл {file_path} не найден. Сначала запустите analyze_data.py")
        return

    print("--- 1. Анализ зарплат по опыту работы ---")
    # Группируем данные по опыту и считаем среднюю зарплату
    experience_salary = df.groupby('experience')['salary_avg'].mean().sort_values(ascending=False)
    print(experience_salary.round(0))
    
    # Визуализация
    experience_order = ['Нет опыта', 'От 1 года до 3 лет', 'От 3 до 6 лет', 'Более 6 лет']
    plt.figure() # Создаем новую фигуру для графика
    sns.barplot(x='experience', y='salary_avg', data=df, order=experience_order, palette='viridis', errorbar=None, hue='experience', legend=False)
    plt.title('Средняя зарплата в зависимости от опыта работы')
    plt.xlabel('Опыт работы')
    plt.ylabel('Средняя зарплата (RUR, gross)')
    plt.xticks(rotation=45)
    plt.tight_layout() # Чтобы подписи не обрезались
    plt.savefig('salary_by_experience.png') # Сохраняем график в файл
    print("График 'salary_by_experience.png' сохранен.")

    print("\n--- 2. Влияние ключевых навыков на зарплату ---")
    skill_columns = [col for col in df.columns if col.startswith('skill_')]
    
    for skill in skill_columns:
        # Сравниваем среднюю зарплату для вакансий, где навык требуется и где нет
        salary_with_skill = df[df[skill] == True]['salary_avg'].mean()
        salary_without_skill = df[df[skill] == False]['salary_avg'].mean()
        
        if not pd.isna(salary_with_skill):
            print(f"Средняя зарплата для '{skill.replace('skill_', '')}': {salary_with_skill:.0f} RUR "
                  f"(без навыка: {salary_without_skill:.0f} RUR)")

    print("\n--- 3. Топ-10 городов по количеству вакансий и средней зарплате ---")
    top_cities = df['city'].value_counts().nlargest(10)
    print("Топ-10 городов по количеству вакансий:")
    print(top_cities)

    # Считаем среднюю зарплату для этих городов
    top_cities_salary = df[df['city'].isin(top_cities.index)].groupby('city')['salary_avg'].mean().sort_values(ascending=False)
    print("\nСредняя зарплата в топ-10 городах:")
    print(top_cities_salary.round(0))

    # Визуализация зарплат по городам
    plt.figure()
    sns.barplot(x=top_cities_salary.index, y=top_cities_salary.values, palette='plasma', hue=top_cities_salary.index, legend=False)
    plt.title('Средняя зарплата в топ-10 городах')
    plt.xlabel('Город')
    plt.ylabel('Средняя зарплата (RUR, gross)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('salary_by_city.png')
    print("График 'salary_by_city.png' сохранен.")


if __name__ == '__main__':
    perform_eda()