#  Project: Evo-Sim
#  Developed by: Irina Danes

import numpy as np
import matplotlib.pyplot as plt

N = 4
allocated = (77, 77, 77, 100)
not_allocated = (23, 23, 23, 0)

ind = np.arange(N)
width = 0.35

p1 = plt.bar(ind, allocated, width, color='green', alpha=0.7)
p2 = plt.bar(ind, not_allocated, width,
             bottom=allocated, color='red', alpha = 0.7)

plt.ylabel('Percentage')
plt.title('Percentage of EVs allocated to a Charging Station')
plt.xticks(ind, ('Random', 'Greedy', 'Top-k', 'Optimal'))
plt.yticks(np.arange(0, 101, 10))
plt.legend((p1[0], p2[0]), ('Allocated', 'Not allocated'))

plt.show()