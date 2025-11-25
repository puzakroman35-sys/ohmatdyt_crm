#!/usr/bin/env python3
"""
Test script to show datetime parsing
"""
from datetime import datetime

# We'll mock the query to see what SQL is generated
date_from = "2025-11-25"
date_to = "2025-11-25"

# Parse dates the same way as crud.py
date_from_dt = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
date_to_dt = datetime.fromisoformat(date_to.replace('Z', '+00:00'))

print("BEFORE end-of-day adjustment:")
print(f"date_to_dt: {date_to_dt} (tzinfo: {date_to_dt.tzinfo})")
print(f"hour={date_to_dt.hour}, minute={date_to_dt.minute}, second={date_to_dt.second}")

# Apply end-of-day logic
if date_to_dt.hour == 0 and date_to_dt.minute == 0 and date_to_dt.second == 0:
    date_to_dt = date_to_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    print("\nEnd-of-day adjustment APPLIED")

print("\nAFTER end-of-day adjustment:")
print(f"date_from_dt: {date_from_dt} (tzinfo: {date_from_dt.tzinfo})")
print(f"date_to_dt: {date_to_dt} (tzinfo: {date_to_dt.tzinfo})")
print(f"date_from_dt type: {type(date_from_dt)}")
print(f"date_to_dt type: {type(date_to_dt)}")

# Show how these would be used in SQL
print(f"\nExpected SQL filter:")
print(f"WHERE created_at >= '{date_from_dt}' AND created_at <= '{date_to_dt}'")
