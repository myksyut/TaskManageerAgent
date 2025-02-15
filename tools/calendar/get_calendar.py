from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, UTC
import sys
import os
import pickle
import socket

# プロジェクトルートへのパスを追加
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from config import config

# OAuth 2.0の認証スコープ
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

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
                # 利用可能なポートを見つける
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

def get_calendar():
    """GoogleカレンダーAPIを使用して今日のスケジュールを取得する"""
    try:
        # OAuth認証情報を取得
        creds = get_credentials()
        
        # Google Calendar APIのサービスを構築
        service = build('calendar', 'v3', credentials=creds)

        # 今日の日付の開始と終了を取得
        now = datetime.now(UTC)
        start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=UTC).isoformat()
        end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=UTC).isoformat()

        # カレンダーイベントを取得
        events_result = service.events().list(
            calendarId='primary',  # プライマリーカレンダー
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return []
        
        # イベント情報を整形
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            formatted_events.append({
                'summary': event.get('summary', '(タイトルなし)'),
                'start': start,
                'end': end,
                'description': event.get('description', ''),
                'location': event.get('location', '')
            })
        
        return formatted_events

    except HttpError as e:
        print(f"Google Calendar APIエラー: {str(e)}")
        return []
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return []

if __name__ == "__main__":
    try:
        events = get_calendar()
        if not events:
            print("本日のイベントはありません")
        else:
            print("本日のイベント:")
            for event in events:
                print(f"- {event['summary']}")
                print(f"  開始: {event['start']}")
                print(f"  終了: {event['end']}")
                if event['location']:
                    print(f"  場所: {event['location']}")
                if event['description']:
                    print(f"  説明: {event['description']}")
                print()
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise
