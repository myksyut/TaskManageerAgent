from datetime import datetime

def get_todays_date():
    return datetime.now().strftime("%Y-%m-%d")

def get_today_of_week():
    weekdays = ['月', '火', '水', '木', '金', '土', '日']
    return weekdays[datetime.now().weekday()]

def get_now_time():
    return datetime.now().strftime("%H:%M:%S")

if __name__ == "__main__":
    print('今日は', get_todays_date(), 'です。')
    print('今日は', get_today_of_week(), '曜日です。')
    print('現在は', get_now_time(), 'です。')