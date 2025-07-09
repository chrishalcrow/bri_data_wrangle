from pathlib import Path
import pandas as pd

obj_scores = pd.read_csv("/home/nolanlab/Work/Bri_Project/derivatives/chR2/1544/summary/all_object_scores.parquet")

dates = list(set(obj_scores['date'].values))

for date in dates:
    


