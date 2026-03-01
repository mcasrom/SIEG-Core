import pandas as pd
import json
import glob
import os

history_file = 'data/history_log.csv'
files = glob.glob('data/geoint_*.json')
new_rows = []

for f in files:
    try:
        with open(f, 'r') as j:
            content = json.load(j)
            new_rows.append({
                'timestamp': content.get('timestamp', 'N/A'),
                'region': os.path.basename(f)[7:-5].upper(),
                'score': content.get('score', 0)
            })
    except:
        continue

if new_rows:
    df_new = pd.DataFrame(new_rows)
    if os.path.exists(history_file):
        df_old = pd.read_csv(history_file)
        # Combinamos y quitamos duplicados exactos para no engordar el CSV
        df_final = pd.concat([df_old, df_new]).drop_duplicates(subset=['timestamp', 'region'])
    else:
        df_final = df_new
    
    # Guardamos las últimas 1000 entradas para tener un historial sólido
    df_final.tail(1000).to_csv(history_file, index=False)
    print(f"Historial actualizado: {len(df_final)} registros totales.")
