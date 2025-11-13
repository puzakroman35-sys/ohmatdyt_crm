"""Тестування пошуку категорій локально"""
import requests
from urllib.parse import quote

BASE_URL = "http://localhost:8000"

def test_search(search_term):
    """Тест пошуку категорій"""
    # URL encode для українських символів
    encoded_search = quote(search_term)
    url = f"{BASE_URL}/api/categories?search={encoded_search}&include_inactive=true"
    
    print(f"\n🔍 Пошук: '{search_term}'")
    print(f"URL: {url}")
    
    response = requests.get(url)
    data = response.json()
    
    print(f"✅ Знайдено: {data['total']} категорій")
    for cat in data['categories']:
        print(f"   - {cat['name']}")
    
    return data['total']

if __name__ == "__main__":
    print("=" * 60)
    print("Тестування пошуку категорій (локально)")
    print("=" * 60)
    
    # Спочатку отримаємо всі категорії
    response = requests.get(f"{BASE_URL}/api/categories?include_inactive=true")
    all_cats = response.json()
    print(f"\nВсього категорій: {all_cats['total']}")
    print("Список:")
    for cat in all_cats['categories']:
        print(f"  - {cat['name']}")
    
    # Тести
    print("\n" + "=" * 60)
    print("ТЕСТИ ПОШУКУ")
    print("=" * 60)
    
    test_search("Admin")  # Англійська
    test_search("Medical")  # Англійська
    test_search("Медична")  # Українська (якщо є)
    test_search("Соціальна")  # Українська (якщо є)
    
    print("\n" + "=" * 60)
