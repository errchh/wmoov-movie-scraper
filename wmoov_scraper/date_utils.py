from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import pytz


def get_current_date():
    """Get current date in Hong Kong timezone"""
    return datetime.now(pytz.timezone('Asia/Hong_Kong')).date()


def get_weekend_dates(current_date):
    """
    Calculate upcoming weekend dates (Saturday + Sunday)
    Weekend = Saturday + Sunday
    """
    # Find next Saturday
    days_until_saturday = (5 - current_date.weekday()) % 7
    if days_until_saturday == 0 and current_date.weekday() != 5:
        days_until_saturday = 7
    
    saturday = current_date + timedelta(days=days_until_saturday)
    sunday = saturday + timedelta(days=1)
    
    return [saturday, sunday]