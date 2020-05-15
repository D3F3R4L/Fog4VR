import os
import sys
import multiprocessing as mp
import numpy as np
import argparse
import time

NumCores=os.cpu_count()
parser = argparse.ArgumentParser(description='Script to run multiple simulations with NS3 scripts, and balence the use of cores on CPU to always left some free cores. Example python3 src/dash-migration/Run.py dash-migration-v2 -i simulationId -s seedValue -r 5 -args politica=1 -args numberOfClients=5 -ug -g src/dash-migration/graficos.py -rargs runs=r -cargs numberOfClients=c')
parser.add_argument('script', type=str,help='The script local to run the script. Ex:scratch/myscript')
parser.add_argument('--arguments','-args',action='append', type=str,help='The arguments used in the script if needed. Ex: NumClientes=30  Type=2')
parser.add_argument('--cores','-c', type=float,default=0.5,help='Percentage of cores that the simulations can use. Default is 0.5')
parser.add_argument('--MaxUse','-m', action='store_true',help='Active max performance and disable balanced use of cores on CPU. Default is false')
parser.add_argument('--runs','-r', type=int,default=1,help='Number of simulations that you like to run. Default is 1')
parser.add_argument('--id','-i', type=str,help='If simulation need a id the number of runs defined you be used, parse the command used in the simulations. Ex: SimulationId')
parser.add_argument('--seed','-s', type=str,help='If simulation need a seed the number of runs defined you be used, parse the command used in the simulations. Ex: SeedNumber')
parser.add_argument('--UseGraph','-ug', action='store_true',help='Set if you want to use a graph script. Default is false')
parser.add_argument('--graph','-g', type=str,help='Set the location and name of the script (Only python supported). Ex: home/myscript.py')
parser.add_argument('--GraphArgs','-gargs',action='append', type=str,help='The arguments used in the graph script if needed (argParse library needed). Ex: Clientes=30  mytype=2')
parser.add_argument('--CopyArgs','-cargs',action='append', type=str,help='The arguments used in the graph script that you be copied from the ns3 script (argParse library needed). Ex: NumClientes=Clients  Type=mytype')
parser.add_argument('--RepeatArgs','-rargs',action='append', type=str,help='The arguments to be reused in the graph script that you be copied from this script (argParse library needed). Ex: runs=NumbersOfRuns  seed=Seed id=Id')
args = parser.parse_args()
if args.cores > 1 or args.cores<0:
    parser.error("Wrong Percentage, use values from 0 to 1")
if args.runs <= 0 :
    parser.error("Invalid number of runs")

		
print(args.arguments)

Cores={}
NumSims=args.runs
MaxLoad=args.cores
MaxCores=int(NumCores*MaxLoad)
script=args.script
gscript=args.graph
if args.arguments!=None:
        for a in args.arguments:
	        script=script+" --"+a
if args.id!=None:
	script=script+" --"+args.id
script = './waf --run="'+script
print(script)
if args.UseGraph:
	if (args.graph==None):
		parser.error("Graph directory not specified")
	else:
		gscript='python3 '+gscript
		if (args.GraphArgs!=None):
			for a in args.GraphArgs:
				aux=a.split('=',1)
				gscript=gscript+" -"+aux[0]+" "+aux[1]
		if (args.CopyArgs!=None):
			for a in args.CopyArgs:
				aux=a.split('=',1)
				for i in args.arguments:
					aux2=i.split('=')
					if (aux2[0]==aux[0]):
						gscript=gscript+" -"+aux[1]+" "+aux2[1]
		if (args.RepeatArgs!=None):
			for a in args.RepeatArgs:
				aux=a.split('=',1)
				if(aux[0]=='runs'):
					aux[0]=str(NumSims)
					gscript=gscript+" -"+aux[1]+" "+aux[0]

print(gscript)
def main():
	for i in range (0,MaxCores):
		var = 'core{num}'.format(num=i)
		Cores[var]=i
		print(Cores)
	j=0
	while j<NumSims:
		freeCores=int(np.ceil(NumCores-os.getloadavg()[0]))
		useCores=int(freeCores*MaxLoad)
		if (useCores+j)>NumSims:
			useCores=NumSims-j
		for i in range(0,useCores):
			Cores[list(Cores)[i]]=mp.Process(target=callFunction, args=(j,script,))
			j+=1
		for i in range(0,useCores):
			time.sleep(2)
			Cores[list(Cores)[i]].start()
		for i in range(0,useCores):
			Cores[list(Cores)[i]].join()
		time.sleep(10)
	if args.UseGraph:
		graph()

def callFunction(num, script):
	if args.id!=None:
		script=script+'={id}'.format(id=num)
	if args.seed!=None:
		script=script+' --'+args.seed+'={id}'.format(id=num)
	
	script=script+'"'
	print(script)
	print('Simulation{id}"'.format(id=num))
	os.system(script)

def graph():
	os.system(gscript)

if __name__=="__main__":
    main()
