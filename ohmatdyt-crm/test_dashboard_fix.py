"""
Тест для перевірки виправлення підрахунку звернень на dashboard
"""
import sys
import os

# Додаємо шлях до API модуля
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app import crud
import os
from dotenv import load_dotenv

# Завантажуємо env
load_dotenv()

# Підключення до БД
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://ohm_user:change_me@localhost:5432/ohm_db")
# Замінюємо хост db на localhost для локального доступу
DATABASE_URL = DATABASE_URL.replace("@db:", "@localhost:")

print(f"Підключаюся до БД: {DATABASE_URL.replace('change_me', '***')}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def test_direct_count():
    """Прямий підрахунок в БД"""
    print("\n" + "="*60)
    print("1. ПРЯМИЙ ПІДРАХУНОК В БАЗІ ДАНИХ")
    print("="*60)
    
    with engine.connect() as conn:
        # Загальна кількість
        result = conn.execute(text("SELECT COUNT(*) FROM cases"))
        total = result.scalar()
        print(f"Загальна кількість звернень: {total}")
        
        # По статусах
        result = conn.execute(text("""
            SELECT status, COUNT(*) as count 
            FROM cases 
            GROUP BY status 
            ORDER BY status
        """))
        
        print("\nРозподіл по статусах:")
        status_sum = 0
        for row in result:
            print(f"  {row[0]:15} : {row[1]:3}")
            status_sum += row[1]
        
        print(f"\nСума по статусах: {status_sum}")
        print(f"Співпадає з total: {'✓' if status_sum == total else '✗ ПОМИЛКА!'}")


def test_crud_function():
    """Тест CRUD функції"""
    print("\n" + "="*60)
    print("2. ТЕСТ CRUD ФУНКЦІЇ get_dashboard_summary()")
    print("="*60)
    
    db = SessionLocal()
    try:
        result = crud.get_dashboard_summary(db)
        
        print(f"\nРезультат функції:")
        print(f"  total_cases         : {result['total_cases']}")
        print(f"  new_cases           : {result['new_cases']}")
        print(f"  in_progress_cases   : {result['in_progress_cases']}")
        print(f"  needs_info_cases    : {result['needs_info_cases']}")
        print(f"  rejected_cases      : {result['rejected_cases']}")
        print(f"  done_cases          : {result['done_cases']}")
        
        # Перевірка суми
        calculated_sum = (
            result['new_cases'] + 
            result['in_progress_cases'] + 
            result['needs_info_cases'] + 
            result['rejected_cases'] + 
            result['done_cases']
        )
        
        print(f"\nСума по статусах: {calculated_sum}")
        print(f"Total cases      : {result['total_cases']}")
        print(f"Співпадає        : {'✓' if calculated_sum == result['total_cases'] else '✗ ПОМИЛКА!'}")
        
    finally:
        db.close()


def test_status_distribution():
    """Тест розподілу по статусах"""
    print("\n" + "="*60)
    print("3. ТЕСТ ФУНКЦІЇ get_status_distribution()")
    print("="*60)
    
    db = SessionLocal()
    try:
        result = crud.get_status_distribution(db)
        
        print(f"\nЗагальна кількість: {result['total_cases']}")
        print("\nРозподіл:")
        
        total_percentage = 0
        for item in result['distribution']:
            status = item['status']
            count = item['count']
            percentage = item['percentage']
            print(f"  {status:15} : {count:3} ({percentage:6.2f}%)")
            total_percentage += percentage
        
        print(f"\nСума відсотків: {total_percentage:.2f}%")
        print(f"Має бути 100%  : {'✓' if abs(total_percentage - 100.0) < 0.01 or result['total_cases'] == 0 else '✗ ПОМИЛКА!'}")
        
    finally:
        db.close()


if __name__ == "__main__":
    try:
        test_direct_count()
        test_crud_function()
        test_status_distribution()
        
        print("\n" + "="*60)
        print("ВИСНОВОК")
        print("="*60)
        print("Якщо всі тести показують співпадіння - код правильний.")
        print("Якщо є розбіжності - потрібно виправляти CRUD функції.")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ПОМИЛКА: {e}")
        import traceback
        traceback.print_exc()
