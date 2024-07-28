import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict

CSV_FILE = 'work_log.csv'

def create_entry(date, minutes, pay_rate, project_title):
    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, minutes, pay_rate, project_title])

def read_entries():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, 'r') as file:
        reader = csv.reader(file)
        return list(reader)

def update_entry(index, date, minutes, pay_rate, project_title):
    entries = read_entries()
    if 0 <= index < len(entries):
        entries[index] = [date, minutes, pay_rate, project_title]
        write_entries(entries)
        return True
    return False

def delete_entry(index):
    entries = read_entries()
    if 0 <= index < len(entries):
        del entries[index]
        write_entries(entries)
        return True
    return False

def write_entries(entries):
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(entries)

def validate_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_minutes(minutes_string):
    try:
        minutes = int(minutes_string)
        return minutes > 0
    except ValueError:
        return False

def validate_pay_rate(pay_rate_string):
    try:
        pay_rate = float(pay_rate_string)
        return pay_rate > 0
    except ValueError:
        return False

def get_week_start(date):
    date = datetime.strptime(date, '%Y-%m-%d')
    first_work_day = min(entry[0] for entry in read_entries())
    first_work_day = datetime.strptime(first_work_day, '%Y-%m-%d')
    days_since_start = (date - first_work_day).days
    week_number = days_since_start // 7
    return first_work_day + timedelta(days=week_number*7)

def calculate_take_home_pay(hours, average_hourly_rate):
    pay_structure = [
        (7, 0.50),
        (13, 0.60),
        (float('inf'), 0.75)
    ]
    
    total_pay = 0
    remaining_hours = hours
    
    for threshold, percentage in pay_structure:
        if remaining_hours <= 0:
            break
        
        hours_in_bracket = min(remaining_hours, threshold)
        pay_in_bracket = hours_in_bracket * average_hourly_rate * percentage
        total_pay += pay_in_bracket
        remaining_hours -= hours_in_bracket
    
    return total_pay

def calculate_weekly_stats():
    entries = read_entries()
    weekly_stats = defaultdict(lambda: {'total_hours': 0, 'total_pay': 0, 'entries': 0})

    for entry in entries:
        date, minutes, pay_rate = entry[:3]
        week_start = get_week_start(date).strftime('%Y-%m-%d')
        
        hours = int(minutes) / 60
        pay = hours * float(pay_rate)

        weekly_stats[week_start]['total_hours'] += hours
        weekly_stats[week_start]['total_pay'] += pay
        weekly_stats[week_start]['entries'] += 1

    result = []
    for week_start, stats in weekly_stats.items():
        week_end = (datetime.strptime(week_start, '%Y-%m-%d') + timedelta(days=6)).strftime('%Y-%m-%d')
        avg_hourly_rate = stats['total_pay'] / stats['total_hours'] if stats['total_hours'] > 0 else 0
        take_home_pay = calculate_take_home_pay(stats['total_hours'], avg_hourly_rate)
        result.append({
            'week': f"{week_start} to {week_end}",
            'total_hours': round(stats['total_hours'], 2),
            'total_pay': round(stats['total_pay'], 2),
            'avg_hourly_rate': round(avg_hourly_rate, 2),
            'take_home_pay': round(take_home_pay, 2)
        })

    return sorted(result, key=lambda x: x['week'])

def calculate_total_take_home_earnings():
    weekly_stats = calculate_weekly_stats()
    return sum(week['take_home_pay'] for week in weekly_stats)

def calculate_daily_earnings():
    entries = read_entries()
    daily_earnings = defaultdict(float)

    for entry in entries:
        date, minutes, pay_rate = entry[:3]
        hours = int(minutes) / 60
        pay = hours * float(pay_rate)
        daily_earnings[date] += pay

    return sorted(daily_earnings.items())