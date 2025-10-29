from app import crud
from app.database import SessionLocal

db = SessionLocal()
result = crud.get_dashboard_summary(db)

print("=== Dashboard Summary ===")
print(f"Total cases: {result['total_cases']}")
print(f"NEW: {result['new_cases']}")
print(f"IN_PROGRESS: {result['in_progress_cases']}")
print(f"NEEDS_INFO: {result['needs_info_cases']}")
print(f"REJECTED: {result['rejected_cases']}")
print(f"DONE: {result['done_cases']}")

calc_sum = (result['new_cases'] + result['in_progress_cases'] + 
            result['needs_info_cases'] + result['rejected_cases'] + result['done_cases'])
print(f"\nCalculated sum: {calc_sum}")
print(f"Match: {calc_sum == result['total_cases']}")

db.close()
