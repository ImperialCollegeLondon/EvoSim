#  Project: Evo-Sim
#  Developed by: Irina Danes

import numpy as np
import matplotlib.pyplot as plt

font = {'family': 'normal', 'size': 17}
plt.rc('font', **font)

N = 4
ind = np.arange(N)
width = 0.25

fig = plt.figure(figsize=(20,10))
ax = fig.add_subplot(111)

allocation_rates_5000 = [100.0, 78, 71.34, 45.38]
bars_5000 = ax.bar(ind, allocation_rates_5000, width, color='#cb3335')

allocation_rates_10000 = [100.0, 47.25, 72.42, 30.76]
bars_10000 = ax.bar(ind+width, allocation_rates_10000, width, color='#477ca8')

allocation_rates_20000 = [100, 26.45, 71.56, 18.72]
bars_20000 = ax.bar(ind+2*width, allocation_rates_20000, width, color='#59a257')

ax.set_ylim(0, 107)
ax.set_xticks(ind+width)
ax.set_xticklabels( ('No constraints', 'Time constraint', 'Distance constraint', 'Time and distance constraints') )
ax.legend( (bars_5000[0], bars_10000[0], bars_20000[0]), ('5,000 EVs', '10,000 EVs', '20,000 EVs') )

def autolabel(bars):
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., 1.02*h, '%0.2f'%float(h),
                ha='center', va='bottom')

autolabel(bars_5000)
autolabel(bars_10000)
autolabel(bars_20000)

plt.ylabel('Percentage of allocated EVs')
plt.title('Allocation rates')
plt.show()
# plt.savefig('allocation_rates.png')