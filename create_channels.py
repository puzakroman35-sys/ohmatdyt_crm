from app.database import SessionLocal
from app import crud, schemas

db = SessionLocal()

channels = [
    {'name': 'Контакт-центр', 'description': 'Звернення через телефонний контакт-центр', 'color': '#2196F3'},
    {'name': 'Рецепція', 'description': 'Звернення через рецепцію', 'color': '#4CAF50'},
    {'name': 'Онлайн', 'description': 'Онлайн звернення через веб-сайт', 'color': '#9C27B0'},
    {'name': 'QR', 'description': 'Звернення через QR-код', 'color': '#FF9800'},
    {'name': 'Email', 'description': 'Звернення через електронну пошту', 'color': '#F44336'},
    {'name': 'Скринька', 'description': 'Звернення через поштову скриньку', 'color': '#795548'},
    {'name': 'МОЗ', 'description': 'Звернення через Міністерство охорони здоров\'я', 'color': '#3F51B5'},
    {'name': 'Інше', 'description': 'Інші канали звернень', 'color': '#9E9E9E'}
]

for channel_data in channels:
    try:
        channel = crud.create_channel(db, schemas.ChannelCreate(**channel_data))
        print(f'✓ Створено: {channel.name}')
    except Exception as e:
        print(f'✗ Помилка для {channel_data["name"]}: {str(e)[:80]}')

db.commit()
db.close()
print('\n✓ Канали створені!')
