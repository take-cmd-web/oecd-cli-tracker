import pandas as pd
import requests
import plotly.express as px
import os

# OECD API URL (日本, 韓国, メキシコ, 米国, G7, ブラジル, 中国, インド)
URL = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_CLI,/.M.JPN+KOR+MEX+USA+G7+BRA+CHN+IND.LI...AA...H?lastNObservations=600&dimensionAtObservation=AllDimensions"

def fetch_oecd_data():
    print("Fetching data from OECD...")
    response = requests.get(URL, headers={'Accept': 'application/vnd.sdmx.data+json;version=1.0-expect'})
    data = response.json()
    
    observations = data['data']['dataSets'][0]['observations']
    structure = data['data']['structures'][0]['dimensions']['observation']
    
    loc_idx = next(i for i, d in enumerate(structure) if d['id'] == 'REF_AREA')
    time_idx = next(i for i, d in enumerate(structure) if d['id'] == 'TIME_PERIOD')
    
    locations = structure[loc_idx]['values']
    times = structure[time_idx]['values']
    
    records = []
    for key, value in observations.items():
        indices = key.split(':')
        loc = locations[int(indices[loc_idx])]['name']
        time = times[int(indices[time_idx])]['id']
        val = value[0]
        records.append({'Date': time, 'Country': loc, 'CLI': val})
    
    df = pd.DataFrame(records)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def create_graph(df):
    print("Creating graph...")
    fig = px.line(df, x='Date', y='CLI', color='Country',
                  title='OECD Composite Leading Indicators (CLI) - Monthly',
                  labels={'CLI': 'Index (Amplitude adjusted)', 'Date': 'Year'},
                  template='plotly_white')
    
    if not os.path.exists('public'):
        os.makedirs('public')
    # index.htmlとして保存
    fig.write_html("public/index.html")

if __name__ == "__main__":
    try:
        df = fetch_oecd_data()
        create_graph(df)
        print("Success: public/index.html created.")
    except Exception as e:
        print(f"Error: {e}")