"""
Тест для діагностики пошуку користувачів
"""
import sys
sys.path.insert(0, 'ohmatdyt-crm/api')

from sqlalchemy import create_engine, select, or_
from sqlalchemy.orm import Session
from app import models
from app.database import Base

# Підключення до БД
DATABASE_URL = "postgresql+psycopg://ohm_user:change_me@localhost:5432/ohm_db"
engine = create_engine(DATABASE_URL)

with Session(engine) as db:
    # Тест 1: Всі користувачі
    print("\n=== Тест 1: Всі користувачі ===")
    query = select(models.User)
    all_users = db.execute(query).scalars().all()
    print(f"Загальна кількість: {len(all_users)}")
    
    # Тест 2: Пошук з фільтром
    print("\n=== Тест 2: Пошук 'admin' ===")
    search = "admin"
    query = select(models.User)
    
    search_filter = or_(
        models.User.username.ilike(f"%{search}%"),
        models.User.email.ilike(f"%{search}%"),
        models.User.full_name.ilike(f"%{search}%")
    )
    query = query.where(search_filter)
    
    filtered_users = db.execute(query).scalars().all()
    print(f"Знайдено користувачів: {len(filtered_users)}")
    
    for user in filtered_users:
        print(f"  - {user.username} | {user.email} | {user.full_name}")
    
    # Тест 3: Перевірка, чи містить "admin"
    print("\n=== Тест 3: Які користувачі містять 'admin' ===")
    for user in all_users:
        if 'admin' in user.username.lower() or 'admin' in user.email.lower() or 'admin' in user.full_name.lower():
            print(f"  ✓ {user.username} | {user.email} | {user.full_name}")
