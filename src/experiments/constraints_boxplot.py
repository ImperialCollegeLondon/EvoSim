#  Project: Evo-Sim
#  Developed by: Irina Danes

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

plt.figure(figsize=(25,20))
sns.set(style="white", font_scale=4)

distance_none5000 = []
distance_none10000 = []
distance_none20000 = []

distance_time5000 = []
distance_time10000 = []
distance_time20000 = []

distance_distance5000 = []
distance_distance10000 = []
distance_distance20000 = []

distance_both5000 = []
distance_both10000 = []
distance_both20000 = []


all_distances =[distance_none5000, distance_none10000, distance_none20000, distance_time5000, distance_time10000, distance_time20000, distance_distance5000, distance_distance10000, distance_distance20000, distance_both5000, distance_both10000, distance_both20000]

sorted_data = sorted(all_distances, key = lambda x: np.median(x), reverse = True)
df =pd.DataFrame(all_distances).T

df = df.rename(columns={k: f'Data{k+1}' for k in range(len(sorted_data))}).reset_index()
df = pd.wide_to_long(df, stubnames = ['Data'], i = 'index', j = 'ID').reset_index()[['ID', 'Data']]

conditions = [df['ID']%3==1, df['ID']%3==2, df['ID']%3==0]
choices = ['5,000 EVs', '10,000 EVs', '20,000 EVs']
df['Number of EVs'] = np.select(conditions, choices)

print(df.head)
conditions = [df['ID']<4, (df['ID']>3) & (df['ID']<7), (df['ID']>6) & (df['ID']<10), df['ID']>9]
choices = ['No constraints', 'Time constraint', 'Distance constraint', 'Time and distance constraints']
df['Scenario'] = np.select(conditions, choices)

sns.boxplot(x = 'Scenario', y = 'Data', hue = 'Number of EVs', data = df, showfliers = False, width = 0.3, palette = "Set1", whis = 100)\
        .set(ylabel = 'Distance (in kms)', xlabel = '')

plt.show()
# plt.savefig('boxplot_distance.png')



