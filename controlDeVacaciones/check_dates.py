
from datetime import date, timedelta

def check_weeks(year):
    print(f"--- Checking Weeks for {year} ---")
    # First week
    jan1 = date(year, 1, 1)
    # Start on Sunday
    start_date = jan1 - timedelta(days=(jan1.weekday() + 1) % 7)
    end_date = start_date + timedelta(days=6)
    print(f"First Week (contains Jan 1): {start_date} to {end_date}")
    
    # Last week
    dec31 = date(year, 12, 31)
    # Start of that week (Sunday)
    # dec31 weekday: Mon=0... Sun=6
    # If dec31 is Wed(2), start is Sun(Dec 28).
    # days to subtract = (weekday + 1) % 7
    start_last = dec31 - timedelta(days=(dec31.weekday() + 1) % 7)
    end_last = start_last + timedelta(days=6)
    print(f"Last Week (contains Dec 31): {start_last} to {end_last}")

check_weeks(2025)
