#  Project: Evo-Sim
#  Developed by: Irina Danes

import matplotlib.pyplot as plt

font = {'family': 'normal', 'size': 17}
plt.rc('font', **font)
fig=plt.figure(figsize=(15,10))

greedy_execution_times =[195, 280, 406, 660, 701]
optimal_execution_times = [3142, 5802, 7682, 11763, 36355]

x = [100,200,300,400,500]

axes = plt.gca()
axes.set_ylim([0, 37000])
axes.set_xlim([0, 600])

plt.plot(x, greedy_execution_times, '-o', label='Greedy',linewidth=2)
plt.plot(x, optimal_execution_times, '-o', label='Optimal',linewidth=2)

plt.xlabel('Number of EVs')
plt.ylabel('Execution time (ms)')


plt.legend()

plt.show()
# plt.savefig('execution_times.png')