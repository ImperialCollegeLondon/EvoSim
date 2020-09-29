#  Project: Evo-Sim
#  Developed by: Irina Danes

import matplotlib.pyplot as plt
import numpy as np

font = {'family': 'normal', 'size': 17}
plt.rc('font', **font)
plt.figure(figsize=(20,10))

distance_none = [4.68, 4.87, 4.86, 4.86, 4.88, 4.86, 4.72, 4.81, 4.74, 4.82, 4.84, 4.9, 4.79, 4.86, 4.72, 5.05, 4.82, 4.65, 4.83, 4.93, 4.92, 4.83, 4.63, 4.72, 4.84]
distance_time = [4.78, 4.93, 4.74, 4.76, 4.73, 4.89, 4.99, 4.93, 4.84, 5.02, 4.91, 4.76, 4.84, 4.76, 4.8, 5.03, 4.76, 4.91, 5, 4.87, 4.97, 4.9, 4.72, 4.74, 4.82]
distance_dist = [0.71, 0.71, 0.71, 0.71, 0.71, 0.71, 0.71, 0.71, 0.71, 0.71, 0.72, 0.73, 0.73, 0.72, 0.72, 0.72, 0.73, 0.72, 0.72, 0.71, 0.71, 0.72, 0.72, 0.71, 0.71]
distance_both = [0.72, 0.72, 0.72, 0.72, 0.72, 0.72, 0.72, 0.72, 0.72, 0.73, 0.75, 0.76, 0.75, 0.75, 0.74, 0.74, 0.74, 0.74, 0.73, 0.73, 0.73, 0.74, 0.74, 0.73, 0.72]

x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]

axes = plt.gca()
axes.set_ylim([0,8])
axes.set_xlim([-1, 25])

plt.plot(x, distance_none, '-o', label='No constraint')
plt.plot(x, distance_time, '-o', label='Time constraint')
plt.plot(x, distance_dist, '-o', label='Distance constraint')
plt.plot(x, distance_both, '-o', label='Time and distance constraints')

plt.xlabel('Time of day')
plt.ylabel('Average distance (in kms)')

plt.xticks(fontsize=13)
plt.xticks(np.arange(25), ('00:00', '01:00', '02:00', '03:00', '04:00','05:00', '06:00', '07:00', '08:00', '09:00','10:00', '11:00', '12:00', '13:00', '14:00',
                           '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00','24:00'))
plt.legend()

plt.show()
# plt.savefig('distance_hourly.png')

