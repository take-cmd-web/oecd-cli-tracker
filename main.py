import pandas as pd
import plotly.express as px
import os
import requests
import io

# OECDのCSV取得URL
URL = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI,all/JPN+KOR+MEX+USA+G7+BRA+CHN+IND.M.LI...AA...H?lastNObservations=600&format=csv"

def update_graph():
    print("OECDから最新データを取得中...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    response.raise_for_status() 
    
    df = pd.read_csv(io.StringIO(response.text))
    
    name_map = {
        'JPN': '日本', 'KOR': '韓国', 'MEX': 'メキシコ', 'USA': '米国',
        'G7': 'G7', 'BRA': 'ブラジル', 'CHN': '中国', 'IND': 'インド'
    }
    df['国名'] = df['REF_AREA'].map(name_map).fillna(df['REF_AREA'])
    df['Date'] = pd.to_datetime(df['TIME_PERIOD'])
    
    # 【変更】2000年以降のデータに絞り込み
    df = df[df['Date'] >= '2000-01-01']
    
    # グラフのグループ分け設定
    groups = [
        {"title": "グラフ1: 全地域比較", "countries": ['G7', '米国', '日本', '中国', '韓国', 'インド', 'メキシコ', 'ブラジル']},
        {"title": "グラフ2: G7全体", "countries": ['G7']},
        {"title": "グラフ3: 米国", "countries": ['米国']},
        {"title": "グラフ4: 日本", "countries": ['日本']},
        {"title": "グラフ5: アジア主要国", "countries": ['中国', '韓国', 'インド']},
        {"title": "グラフ6: ラテンアメリカ", "countries": ['メキシコ', 'ブラジル']}
    ]

    print("マルチグラフを作成中...")
    html_all = "<html><head><meta charset='utf-8'><title>OECD CLI Dashboard</title></head><body style='font-family: sans-serif; background-color: #f8f9fa; padding: 20px;'>"
    html_all += f"<h1 style='text-align: center; color: #333;'>OECD 景気先行指数 (2000年〜)</h1>"

    for group in groups:
        sub_df = df[df['国名'].isin(group['countries'])]
        fig = px.line(sub_df, x='Date', y='OBS_VALUE', color='国名',
                      title=group['title'],
                      labels={'OBS_VALUE': '指数', 'Date': '年月'},
                      template='plotly_white')
        
        # 【変更】Trend(100)の文字を消し、ラインのみにする
        fig.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.7)
        
        # HTMLの一部（Div）として追加
        html_all += fig.to_html(full_html=False, include_plotlyjs='cdn' if group == groups[0] else False)

    html_all += "</body></html>"

    # 保存
    if not os.path.exists('public'):
        os.makedirs('public')
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(html_all)
    
    print("成功: 6つのグラフを含むダッシュボードを更新しました。")

if __name__ == "__main__":
    try:
        update_graph()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import sys
        sys.exit(1)