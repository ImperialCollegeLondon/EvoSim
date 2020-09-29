#  Project: Evo-Sim
#  Developed by: Irina Danes

import matplotlib.pyplot as plt
import numpy as np

plt.figure(figsize=(20,10))
font = {'family': 'normal', 'size': 17}
plt.rc('font', **font)

monday_percentage = [13.16, 13.14, 13.19, 13.21, 13.18, 13.22, 13.18, 13.2, 13.19, 12.76, 12.33, 11.98, 11.8, 11.99, 12.01, 12.09, 12.1, 12.48, 12.66, 12.63, 12.68, 12.73, 12.89, 13.01, 13.01]
saturday_percentage = [13.17, 13.06, 13.07, 13.13, 13.15, 13.18, 13.2, 13.17, 13.1, 12.87, 12.67, 12.5, 12.29, 12.22, 12.16, 12.01, 12.25, 12.51, 12.74, 12.78, 12.76, 12.83, 12.89, 13.05, 13.16]

x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]

axes = plt.gca()
axes.set_ylim([11.7, 13.3])
axes.set_xlim([-1, 25])

plt.plot(x, monday_percentage, '-o', label='Monday, 03.02.2020')
plt.plot(x, saturday_percentage, '-o', label='Saturday, 01.02.2020')

plt.xlabel('Time of day')
plt.ylabel('Percentage of allocated EVs')

plt.title('Weekend vs. weekday allocation rates')

plt.xticks(np.arange(25), ('00:00', '01:00', '02:00', '03:00', '04:00','05:00', '06:00', '07:00', '08:00', '09:00','10:00', '11:00', '12:00', '13:00', '14:00',
                           '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '24:00'), fontsize=13)

plt.legend()

plt.show()
# plt.savefig('static_saturday_vs_monday_20000.png')