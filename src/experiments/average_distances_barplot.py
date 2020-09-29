#  Project: Evo-Sim
#  Developed by: Irina Danes

import matplotlib.pyplot as plt
import numpy as np
fig, ax = plt.subplots(figsize=(15,10))

labels = ['No constraints', 'Time constraint', 'Distance constraint', 'Time and distance constraints']
average_distances = [4.97, 4.71, 0.69, 0.74]

y_pos = np.arange(len(labels))

bars = plt.bar(y_pos, average_distances, width=0.35)

plt.xticks(y_pos, labels, fontsize=13)
plt.yticks(fontsize=13)
plt.ylabel('Distance (in kms)', fontsize=13)
plt.title('Average distance (10,000 EVs)', fontsize=13)

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy = (rect.get_x() + rect.get_width() / 2, height),
                    xytext = (0, 3),
                    textcoords = "offset points",
                    ha = 'center', va = 'bottom')

autolabel(bars)

plt.show()
# plt.savefig('average_distances.png')