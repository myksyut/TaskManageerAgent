from pydantic_settings import BaseSettings
from pathlib import Path

class Config(BaseSettings):
    GOOGLE_CREDENTIALS_PATH: str = str(Path(__file__).parent / 'credentials.json')
    GOOGLE_TOKEN_PATH: str = str(Path(__file__).parent / 'token.pickle')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 認証ファイルの存在確認
        credentials_path = Path(self.GOOGLE_CREDENTIALS_PATH)
        if not credentials_path.exists():
            raise FileNotFoundError(f"認証ファイルが見つかりません: {credentials_path}")

config = Config()
