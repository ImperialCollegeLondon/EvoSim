#  Project: Evo-Sim
#  Developed by: Irina Danes

import matplotlib.pyplot as plt
import numpy as np

font = {'family': 'normal', 'size': 19}
plt.rc('font', **font)
plt.figure(figsize=(20,10))

allocation_rates_5000 = [38.78, 38.74, 38.76, 38.8, 38.76, 38.76, 38.7, 38.72, 37.66, 36.66, 35.74, 35.36, 35.4, 35.64, 35.74, 36.36, 37.08, 37.46, 37.68, 37.56, 37.44, 38.14, 38.72]
allocation_rates_10000 = [23.41, 23.38, 23.47, 23.48, 23.46, 23.5, 23.54, 23.5, 22.66, 21.93, 21.09, 20.93, 20.9, 21.09, 21.27, 21.61, 22.04, 22.39, 22.48, 22.42, 22.31, 22.79, 23.38]
allocation_rates_20000 = [12.63, 12.68, 12.75, 12.74, 12.75, 12.75, 12.77, 12.75, 12.3, 11.83, 11.32, 11.27, 11.21, 11.35, 11.4, 11.66, 11.95, 12.08, 12.12, 12.11, 11.96, 12.3, 12.68]

x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

axes = plt.gca()
axes.set_ylim([0,100])
axes.set_xlim([-1, 24])

plt.plot(x, allocation_rates_5000, '-o', label='5,000 EVs')
plt.plot(x, allocation_rates_10000, '-o', label='10,000 EVs')
plt.plot(x, allocation_rates_20000, '-o', label='20,000 EVs')

plt.xlabel('Time of day')
plt.ylabel('Percentage of allocated EVs')
plt.title('Allocation rates')

plt.xticks(np.arange(24), ('00:00', '01:00', '02:00', '03:00', '04:00','05:00', '06:00', '07:00', '08:00', '09:00','10:00', '11:00', '12:00', '13:00', '14:00',
                           '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'), fontsize=13)
plt.legend()

plt.show()
# plt.savefig('wednesday_final.png')

