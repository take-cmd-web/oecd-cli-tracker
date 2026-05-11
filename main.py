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
    
    # 2000年以降のデータに絞り込み
    df = df[df['Date'] >= '2000-01-01']
    
    # 【修正1】凡例の順番（ご指定の順序）
    master_order = ['G7', '米国', '日本', '中国', '韓国', 'インド', 'メキシコ', 'ブラジル']
    
    groups = [
        {"title": "グラフ1: 全地域比較", "countries": ['G7', '米国', '日本', '中国', '韓国', 'インド', 'メキシコ', 'ブラジル']},
        {"title": "グラフ2: G7", "countries": ['G7']},
        {"title": "グラフ3: 米国", "countries": ['米国']},
        {"title": "グラフ4: 日本", "countries": ['日本']},
        {"title": "グラフ5: 中国", "countries": ['中国']},
        {"title": "グラフ6: 韓国、インド", "countries": ['韓国', 'インド']},
        {"title": "グラフ7: メキシコ、ブラジル", "countries": ['メキシコ', 'ブラジル']}
    ]

    print("マルチグラフを作成中...")
    
    html_all = """
    <html>
    <head>
        <meta charset='utf-8'>
        <title>OECD CLI Dashboard</title>
        <style>
            body { font-family: sans-serif; background-color: #f8f9fa; padding: 20px; }
            h1 { text-align: center; color: #333; }
            h2 { text-align: center; color: #555; margin-top: 50px; font-size: 1.2em; }
            .interactive-container {
                max-width: 1400px;
                margin: 0 auto 30px auto;
                background: white;
                padding: 10px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .usage-text { text-align: center; font-size: 14px; color: #666; margin-top: 0; }
            .grid-container {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                max-width: 1400px;
                margin: 0 auto;
            }
            @media (max-width: 800px) {
                .grid-container { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <h1>OECD 景気先行指数 (2000年〜)</h1>
    """

    # インタラクティブグラフ（メイン）
    # 【修正2】下限を85に固定（range_y）し、凡例の順番を指定（category_orders）
    fig_inter = px.line(df, x='Date', y='OBS_VALUE', color='国名',
                        title='【カスタム分析】期間・国 選択グラフ',
                        labels={'OBS_VALUE': '指数', 'Date': '年月'},
                        template='plotly_white',
                        category_orders={"国名": master_order},
                        range_y=[85, None])
    
    fig_inter.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.7)
    
    fig_inter.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="過去1年", step="year", stepmode="backward"),
                dict(count=3, label="過去3年", step="year", stepmode="backward"),
                dict(count=5, label="過去5年", step="year", stepmode="backward"),
                dict(count=10, label="過去10年", step="year", stepmode="backward"),
                dict(step="all", label="全期間")
            ])
        )
    )

    html_all += "<div class='interactive-container'>"
    html_all += fig_inter.to_html(full_html=False, include_plotlyjs='cdn')
    html_all += (
        "<p class='usage-text'>💡 <strong>使い方：</strong>"
        "グラフ下のバーをドラッグして期間を絞り込めます。"
        "右側の「国名」をクリックすると表示/非表示を切り替えられます（ダブルクリックでその国だけを表示）。</p>"
    )
    html_all += "</div>"

    # 固定グラフ（サブ）
    html_all += "<h2>個別ピックアップグラフ（定点観測用）</h2>"
    html_all += "<div class='grid-container'>"

    for group in groups:
        sub_df = df[df['国名'].isin(group['countries'])]
        # ここでも下限85と凡例の順序を適用
        fig = px.line(sub_df, x='Date', y='OBS_VALUE', color='国名',
                      title=group['title'],
                      labels={'OBS_VALUE': '指数', 'Date': '年月'},
                      template='plotly_white',
                      category_orders={"国名": group['countries']},
                      range_y=[85, None])
        
        fig.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.7)
        html_all += "<div>" + fig.to_html(full_html=False, include_plotlyjs=False) + "</div>"

    html_all += """
        </div>
    </body>
    </html>
    """

    if not os.path.exists('public'):
        os.makedirs('public')
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(html_all)
    
    print("成功: 下限85と凡例の順序を適用したダッシュボードを更新しました。")

if __name__ == "__main__":
    try:
        update_graph()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import sys
        sys.exit(1)