import pandas as pd
import plotly.express as px
import os
import requests
import io

# OECDのCSV取得URL
URL = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI,/.M.JPN+KOR+MEX+USA+G7+BRA+CHN+IND.LI...AA...H?lastNObservations=600&format=csv"

def update_graph():
    print("OECDから最新データを取得中...")
    
    # 403 Forbidden対策: 一般のブラウザからのアクセスに見せかける
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # requestsを使ってデータを取得
    response = requests.get(URL, headers=headers)
    response.raise_for_status() # 万が一エラーがあればここでストップ
    
    # 取得したテキストデータをpandasで読み込む
    csv_data = io.StringIO(response.text)
    df = pd.read_csv(csv_data)
    
    # 国コードを日本語の名前に変換
    name_map = {
        'JPN': '日本', 'KOR': '韓国', 'MEX': 'メキシコ', 'USA': '米国',
        'G7': 'G7', 'BRA': 'ブラジル', 'CHN': '中国', 'IND': 'インド'
    }
    df['国名'] = df['REF_AREA'].map(name_map).fillna(df['REF_AREA'])
    
    # 日付形式を整える
    df['Date'] = pd.to_datetime(df['TIME_PERIOD'])
    
    print("グラフを作成中...")
    fig = px.line(df, x='Date', y='OBS_VALUE', color='国名',
                  title='OECD 景気先行指数 (CLI) - 最新データ',
                  labels={'OBS_VALUE': '指数 (100=トレンド)', 'Date': '年月'},
                  template='plotly_white')
    
    # トレンドライン(100)の追加
    fig.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="Trend (100)")
    
    # 保存処理
    if not os.path.exists('public'):
        os.makedirs('public')
    fig.write_html("public/index.html")
    print("成功: public/index.html が更新されました。")

if __name__ == "__main__":
    try:
        update_graph()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import sys
        sys.exit(1)