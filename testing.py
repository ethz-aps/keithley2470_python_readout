from keithley_k2470 import KeithleyK2470
from configobj import ConfigObj
from time import sleep

import matplotlib
matplotlib.use('TKAgg')
from matplotlib import pyplot as plt
plt.ion()


config = ConfigObj('config.ini')['KeithleyK2470']
k = KeithleyK2470(config)
k.configure()

k.toggleOutput(on=True)
k.setBias(10)
sleep(5)

results = []
for i in range(10000):
	if i%100 == 0:
		print(i)
	curr = k.getCurrent()[0]*10**9 #nA
	results.append(curr)
	#print(f"Current: {curr:.2f} nA")


plt.hist(results, bins=100)
plt.show()

k.toggleOutput(on=False)
k.close()
