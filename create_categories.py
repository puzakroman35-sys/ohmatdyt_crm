from app.database import SessionLocal
from app import crud, schemas

db = SessionLocal()

categories = [
    {'name': 'Медична допомога', 'description': 'Питання медичного обслуговування та лікування', 'color': '#4CAF50'},
    {'name': 'Сервіс', 'description': 'Питання щодо якості сервісу та обслуговування', 'color': '#2196F3'},
    {'name': 'Фінансові та страхові питання', 'description': 'Питання фінансування, оплати та страхування', 'color': '#FF9800'},
    {'name': 'Комунікація та інформація', 'description': 'Питання комунікації та отримання інформації', 'color': '#9C27B0'},
    {'name': 'Технічні проблеми', 'description': 'Технічні питання та проблеми з обладнанням', 'color': '#607D8B'},
    {'name': 'Корупція', 'description': 'Повідомлення про корупційні випадки', 'color': '#F44336'},
    {'name': 'Подяки та пропозиції', 'description': 'Подяки та конструктивні пропозиції', 'color': '#8BC34A'},
    {'name': 'Інше', 'description': 'Інші питання', 'color': '#9E9E9E'}
]

for cat_data in categories:
    try:
        cat = crud.create_category(db, schemas.CategoryCreate(**cat_data))
        print(f'✓ Створено: {cat.name}')
    except Exception as e:
        print(f'✗ Помилка для {cat_data["name"]}: {str(e)[:80]}')

db.commit()
db.close()
print('\n✓ Категорії створені!')
