import pandas as pd
import plotly.express as px
import os

# OECDのCSV取得URL（安定版）
# 日本, 韓国, メキシコ, 米国, G7, ブラジル, 中国, インドを取得
URL = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI,/.M.JPN+KOR+MEX+USA+G7+BRA+CHN+IND.LI...AA...H?lastNObservations=600&format=csv"

def update_graph():
    print("OECDから最新データを取得中...")
    # CSVを直接読み込む
    df = pd.read_csv(URL)
    
    # 国コードを日本語の名前に変換
    name_map = {
        'JPN': '日本', 'KOR': '韓国', 'MEX': 'メキシコ', 'USA': '米国',
        'G7': 'G7', 'BRA': 'ブラジル', 'CHN': '中国', 'IND': 'インド'
    }
    df['国名'] = df['REF_AREA'].map(name_map).fillna(df['REF_AREA'])
    
    # 日付形式を整える（1977-02 -> 1977-02-01）
    df['Date'] = pd.to_datetime(df['TIME_PERIOD'])
    
    print("グラフを作成中...")
    # Plotlyでインタラクティブなグラフを作成
    fig = px.line(df, x='Date', y='OBS_VALUE', color='国名',
                  title='OECD 景気先行指数 (CLI) - 最新データ',
                  labels={'OBS_VALUE': '指数 (100=トレンド)', 'Date': '年月'},
                  template='plotly_white')
    
    # 景気の強弱がわかりやすいように、100のライン（トレンド）を追加
    fig.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="Trend (100)")
    
    # publicフォルダに保存
    if not os.path.exists('public'):
        os.makedirs('public')
    fig.write_html("public/index.html")
    print("成功: public/index.html が更新されました。")

if __name__ == "__main__":
    try:
        update_graph()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        # GitHub Actionsに失敗を知らせるため、あえてエラーで終了させる
        import sys
        sys.exit(1)
