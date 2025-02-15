import webbrowser
from datetime import datetime
import pytz

def main():
    # 日本のタイムゾーンで現在の日付を取得
    jst = pytz.timezone('Asia/Tokyo')
    today = datetime.now(jst)
    
    # Googleカレンダーの日付表示用フォーマット（YYYYMMDD）
    date_str = today.strftime('%Y%m%d')
    
    # Googleカレンダーの特定の日付を表示するURL
    # 日本語インターフェース（hl=ja）で表示
    calendar_url = "https://calendar.google.com/calendar/r/day?hl=ja"
    
    # デフォルトのWebブラウザでURLを開く
    print(f"カレンダーを開いています: {calendar_url}")
    webbrowser.open(calendar_url)

if __name__ == "__main__":
    main()