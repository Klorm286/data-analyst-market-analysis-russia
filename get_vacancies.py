import requests
import json
import time

# --- Ваши учетные данные (ПРОВЕРЬТЕ ИХ ОЧЕНЬ ВНИМАТЕЛЬНО) ---
CLIENT_ID = 'ВАШ_CLIENT_ID' # Вставьте ваш Client ID
CLIENT_SECRET = 'ВАШ_CLIENT_SECRET' # Вставьте ваш Client Secret

# --- Адреса API ---
AUTH_URL = 'https://hh.ru/oauth/token'
API_BASE_URL = 'https://api.hh.ru'
VACANCIES_URL = f'{API_BASE_URL}/vacancies'

def get_access_token():
    """Получает токен доступа."""
    
    # ИСПРАВЛЕНО: Добавлен заголовок User-Agent, как требует API hh.ru
    headers = {
        'User-Agent': 'HH-API-Explorer/1.0 (varlamovevga@gmail.com)' # Укажите вашу почту
    }
    
    params = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    
    response = requests.post(AUTH_URL, data=params, headers=headers)
    response.raise_for_status()
    return response.json()['access_token']

def search_vacancies_page(token, text, page=0, per_page=100, area=113):
    """Получает одну страницу с вакансиями."""
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'text': text,
        'area': area,
        'page': page,
        'per_page': per_page
    }
    
    response = requests.get(VACANCIES_URL, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

if __name__ == '__main__':
    try:
        access_token = get_access_token()
        print("Токен доступа успешно получен!")

        search_query = 'Аналитик данных'
        all_vacancies = []
        
        print(f"Выполняю поиск по запросу: '{search_query}'...")
        first_page_data = search_vacancies_page(access_token, search_query, page=0)
        all_vacancies.extend(first_page_data['items'])
        
        total_pages = first_page_data['pages']
        print(f"Найдено {first_page_data['found']} вакансий на {total_pages} страницах.")

        pages_to_process = min(total_pages, 20) 

        for page_num in range(1, pages_to_process):
            print(f"Обработка страницы {page_num + 1} из {pages_to_process}...")
            page_data = search_vacancies_page(access_token, search_query, page=page_num)
            all_vacancies.extend(page_data['items'])
            time.sleep(0.25)

        output_file = 'vacancies.json'
        with open(output_file, 'w', encoding='utf8') as f:
            json.dump(all_vacancies, f, ensure_ascii=False, indent=4)
            
        print(f"\nСбор данных завершен. Всего собрано {len(all_vacancies)} вакансий.")
        print(f"Результаты сохранены в файл: {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"Произошла ошибка при выполнении запроса: {e}")
    except KeyError as e:
        print(f"Не удалось найти ключ в ответе: {e}. Проверьте структуру ответа от сервера.")
