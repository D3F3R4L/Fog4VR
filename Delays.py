import pandas as pd
import sys
import numpy as np

folder=sys.argv[1]
simu=sys.argv[2]
delays= np.zeros((10,10))
j=0
k=0
for i in range(3, len(sys.argv)):
	if j>=10:
		j=0
		k+=1
	aux=list(sys.argv[i])
	aux=aux[:-10]
	aux.pop(0)
	delay = ''.join(aux)
	delay = float(delay)/2
	delays[k][j]=delay;
	j+=1
print(delays)
name='delays_sim{simu}_Log.csv'.format(simu=simu)
pd.DataFrame(delays).to_csv(folder+name, header=None, index=None)