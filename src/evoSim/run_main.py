#  Project: Evo-Sim
#  Developed by: Irina Danes

import os

times = ["00"]

for time in times:
    print('running ' + time)
    cmd = "java -cp \".:../lib/com.google.ortools.jar:../lib/gson-2.8.0.jar\" ev_project/Main 1 5000 2020-01-16 " + time + ":00:00"

    returned_value = os.system(cmd)
    print('returned value:', returned_value)
