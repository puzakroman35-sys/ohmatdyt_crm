"""
Check cases dates to see if any should be highlighted
"""
import requests
from datetime import datetime, timezone

# Login
login_data = {"username": "executor1", "password": "Executor123!"}
login_response = requests.post("http://localhost:8000/auth/login", json=login_data)
tokens = login_response.json()
access_token = tokens.get("access_token")

# Get cases
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get("http://localhost:8000/api/cases/assigned?skip=0&limit=100", headers=headers)
data = response.json()

print(f"📊 Аналіз звернень (всього: {data.get('total', 0)})\n")
print("="*80)

stale_count = 0
overdue_count = 0
fresh_count = 0

for case in data.get('cases', []):
    public_id = case['public_id']
    status = case['status']
    created_at = case['created_at']
    last_change = case.get('last_status_change_at', created_at)
    
    # Skip completed/rejected
    if status in ['DONE', 'REJECTED']:
        continue
    
    # Parse dates
    created_date = datetime.fromisoformat(created_at.replace('Z', ''))
    if created_date.tzinfo is None:
        created_date = created_date.replace(tzinfo=timezone.utc)
    
    change_date = datetime.fromisoformat(last_change.replace('Z', ''))
    if change_date.tzinfo is None:
        change_date = change_date.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    
    days_since_change = (now - change_date).days
    days_since_created = (now - created_date).days
    
    # Classify
    highlight = ""
    if days_since_change >= 3:
        highlight = "🔴 STALE (>=3 днів без зміни статусу)"
        stale_count += 1
    elif days_since_created > 7:
        highlight = "🟠 OVERDUE (>7 днів від створення)"
        overdue_count += 1
    else:
        highlight = "✅ Fresh"
        fresh_count += 1
    
    print(f"#{public_id:6} | {status:12} | Створено: {days_since_created:2}д тому | Остання зміна: {days_since_change:2}д тому | {highlight}")

print("="*80)
print(f"\n📈 Підсумок:")
print(f"   🔴 Застарілі (>=3 днів): {stale_count}")
print(f"   🟠 Прострочені (>7 днів): {overdue_count}")
print(f"   ✅ Свіжі: {fresh_count}")

if stale_count == 0 and overdue_count == 0:
    print(f"\n⚠️  Немає звернень для підсвічування!")
    print(f"   Всі звернення свіжі (статус змінювався менше 3 днів тому)")
    print(f"\n💡 Рішення: Створіть тестове звернення або зачекайте 3 дні")
else:
    print(f"\n✅ Є звернення які мають бути підсвічені!")
    print(f"   Перевірте чи вони підсвічені на http://localhost:3000/cases")
