import numpy as np
import pandas as pd


from bri_data_wrangle.filepaths import  chris_mac_datapath, chris_linux_datapath
data_path = chris_linux_datapath
from bri_data_wrangle.plotting import plot_object_check
data_path = chris_linux_datapath

df = pd.read_csv("nagelhus_pearson.csv")

mice = np.unique(df['mouse'].values)
for mouse in mice:
    dates = np.unique(df.query(f'mouse == {mouse}')['date'].values)

    for date in dates:

        clusters = np.unique(df.query(f'mouse == {mouse} & date == "{date}"')['cluster_id'].values)

        #sessions = np.unique(df.query(f'mouse == {mouse} & date == "{date}"')['session'].values)
        
        #print("clusters: ", clusters)

        for cluster_id in clusters:
            
            scores = df.query(f'mouse == {mouse} & date == "{date}" & cluster_id == {cluster_id}')[['pearson_score', 'cluster_id', 'session']]
            scores_values = scores.values
            # of_score = scores.query('session == "of"')['pearson_score'].values[0] 
            # obj_score = scores.query('session == "obj"')['pearson_score'].values[0] 
            # of2_score = scores.query('session == "of2"')['pearson_score'].values[0] 
            #
            # 
            

            if len(scores) > 2:

                sessions = [scores_values[0][2], scores_values[1][2], scores_values[2][2]]
                print(sessions)
                    
                if (scores_values[1][0] - scores_values[0][0] > 0.2) & (scores_values[1][0] - scores_values[2][0] > 0.2):
                    print(f"mouse {mouse}, date {date}, cluster_id {cluster_id}")
                   # print(scores)

                    fig = plot_object_check(mouse, date, sessions[:3], cluster_id, data_path=data_path)
                    fig.savefig(f"figs/M{mouse}_D{date}_C{cluster_id}.png")
                
