"""Тестування пошуку категорій на продакшні"""
import requests
from urllib.parse import quote

BASE_URL = "https://10.24.2.187/api"

# Ігноруємо SSL попередження
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_search(search_term):
    """Тест пошуку категорій"""
    encoded_search = quote(search_term)
    url = f"{BASE_URL}/api/categories?search={encoded_search}&include_inactive=true"
    
    print(f"\n🔍 Пошук: '{search_term}'")
    print(f"URL: {url}")
    
    response = requests.get(url, verify=False)
    data = response.json()
    
    print(f"✅ Знайдено: {data['total']} категорій")
    for cat in data['categories']:
        print(f"   - {cat['name']}")
    
    return data['total']

if __name__ == "__main__":
    print("=" * 60)
    print("Тестування пошуку категорій (ПРОДАКШН)")
    print("=" * 60)
    
    # Спочатку отримаємо всі категорії
    response = requests.get(f"{BASE_URL}/api/categories?include_inactive=true", verify=False)
    all_cats = response.json()
    print(f"\nВсього категорій: {all_cats['total']}")
    print("Список:")
    for cat in all_cats['categories']:
        print(f"  - {cat['name']}")
    
    # Тести
    print("\n" + "=" * 60)
    print("ТЕСТИ ПОШУКУ")
    print("=" * 60)
    
    result1 = test_search("Інш")  # Має знайти "Інше"
    result2 = test_search("Сервіс")  # Має знайти "Сервіс"
    result3 = test_search("Комунікація")  # Має знайти "Комунікація та інформація"
    result4 = test_search("Медична")  # Має знайти "Медична допомога"
    
    print("\n" + "=" * 60)
    print("ПІДСУМОК")
    print("=" * 60)
    
    if result1 == 1 and result2 == 1 and result3 == 1 and result4 == 1:
        print("✅ ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!")
    else:
        print("⚠️ Деякі тести не пройшли")
    
    print("=" * 60)
