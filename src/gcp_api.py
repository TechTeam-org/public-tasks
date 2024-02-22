import google.auth
import google.auth.transport.requests
import google.oauth2.id_token
import gspread
from oauth2client.service_account import ServiceAccountCredentials



def authenticate_with_oidc():
    # Google Sheets APIのスコープ
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    # Google Cloudの認証情報を取得
    _, project = google.auth.default()
    token = id_token.fetch_id_token(reqs.Request(), url)
    wb = gspread.service_account()

    # ユーザーに対してブラウザを開き、認証コードを取得
    credentials, _ = google.auth.default(scopes=SCOPES)

    return credentials

def access_spreadsheet(credentials):
    # gspreadを使用してSpreadsheetにアクセス
    gc = gspread.authorize(credentials)

    # Spreadsheetを開く
    spreadsheet = gc.open_by_key('1qakDhRcewEWcfPj23jkPYTMJjuVvlKZjApYyDDED1OU')

    # 以下は適切な処理を実行（例：シートの取得やデータの読み書き）

    # シートの一覧を取得
    sheet_list = spreadsheet.sheet1.title
    print(f"Sheet List: {sheet_list}")

    # シートのデータを取得
    sheet = spreadsheet.sheet1
    data = sheet.get_all_records()
    print(f"Sheet Datas: {data}")
