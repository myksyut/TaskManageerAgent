from datetime import datetime

def get_todays_date():
    return datetime.now().strftime("%Y-%m-%d")

def get_today_of_week():
    weekdays = ['月', '火', '水', '木', '金', '土', '日']
    return weekdays[datetime.now().weekday()]

if __name__ == "__main__":
    print('今日は', get_todays_date(), 'です。')
    print('今日は', get_today_of_week(), '曜日です。')
