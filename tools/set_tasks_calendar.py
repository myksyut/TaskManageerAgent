from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import sys
import os
import pickle
import yaml
import socket

# プロジェクトルートへのパスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config

# OAuth 2.0の認証スコープ
SCOPES = ['https://www.googleapis.com/auth/calendar']

def find_available_port(start_port=8080, max_attempts=10):
    """利用可能なポートを見つける"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except socket.error:
            continue
    raise RuntimeError("利用可能なポートが見つかりませんでした")

def get_credentials():
    """OAuth認証情報を取得する"""
    creds = None
    
    try:
        # トークンが既に存在する場合は読み込む
        if os.path.exists(config.GOOGLE_TOKEN_PATH):
            with open(config.GOOGLE_TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
        
        # 有効な認証情報がない場合は、ユーザーにログインを要求
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                port = find_available_port()
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.GOOGLE_CREDENTIALS_PATH, 
                    SCOPES
                )
                
                print("\nGoogleカレンダーへのアクセス認証が必要です")
                print("以下のURLをブラウザで開いて認証を行ってください:")
                auth_url = flow.authorization_url(
                    access_type='offline',
                    include_granted_scopes='true',
                    prompt='consent'
                )[0]
                print(auth_url)
                print("\n認証が完了すると自動的に処理が継続されます\n")
                
                creds = flow.run_local_server(
                    port=port,
                    prompt='consent'
                )
            
            # 次回のために認証情報を保存
            with open(config.GOOGLE_TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds

    except Exception as e:
        print(f"認証エラー: {str(e)}")
        raise

def create_calendar_event(service, schedule, date):
    """スケジュールをGoogleカレンダーに追加する"""
    try:
        # 時間の解析
        start_time, end_time = schedule['duration'].split('-')
        start_datetime = datetime.strptime(f"{date} {start_time}", "%Y%m%d %H:%M")
        end_datetime = datetime.strptime(f"{date} {end_time}", "%Y%m%d %H:%M")

        event = {
            'summary': schedule['title'],
            'description': f"{schedule['description']}\n\n" \
                         f"優先度: {schedule['priority']}\n" \
                         f"カテゴリ: {schedule['category']}\n" \
                         f"ステータス: {schedule['status']}\n" \
                         f"(TaskManagerAgentによって自動作成されました)",
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Asia/Tokyo',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Asia/Tokyo',
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"予定を追加しました: {schedule['title']}")
        return True

    except Exception as e:
        print(f"予定の追加に失敗しました ({schedule['title']}): {str(e)}")
        return False

def set_tasks_calendar(yaml_path):
    """YAMLファイルから予定をGoogleカレンダーに追加する"""
    try:
        # YAMLファイルを読み込む
        with open(yaml_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)

        if not data or 'schedules' not in data:
            print("有効なスケジュールが見つかりません")
            return

        # 認証情報を取得
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)

        # ファイル名から日付を取得
        date = os.path.splitext(os.path.basename(yaml_path))[0]

        # 各スケジュールをカレンダーに追加
        success_count = 0
        for schedule in data['schedules']:
            if create_calendar_event(service, schedule, date):
                success_count += 1

        print(f"\n処理完了: {success_count}/{len(data['schedules'])}件の予定を追加しました")

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python set_tasks_calendar.py <schedule_yaml_path>")
        sys.exit(1)

    yaml_path = sys.argv[1]
    if not os.path.exists(yaml_path):
        print(f"ファイルが見つかりません: {yaml_path}")
        sys.exit(1)

    set_tasks_calendar(yaml_path)
