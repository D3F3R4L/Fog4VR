import glob
import os
import sys
import operator
import csv
import random
import numpy as np
import pandas as pd
from docplex.mp.model import Model

#delays = np.array([
#            [   1, 10.5,   11,   13, 22.5, 15.5,   22,   17, 27.5, 21.5],
#            [10.5,    1, 21.5, 23.5, 10.5,    5, 31.5, 27.5,   17,   11],
#            [  11, 21.5,    1,   24,   34, 26.5,   10,   16,    7, 12.5],
#            [  13, 23.5,   24,    1,    5,    7,   10,    4, 11.5,   13],
#            [  21, 10.5,  2.5,    5,    1, 15.5, 12.5,    9,  6.5,   10],
#            [15.5,    5, 26.5,    7, 15.5,    1,   17,   11,  9.5,    6],
#            [  21, 31.5,   10,   10, 12.5,   17,    1,    6,  9.5,   13],
#            [  17, 27.5,   16,    4,    9,   11,    6,    1,  3.5,    7],
#            [27.5,   17,    9, 11.5,  6.5,  9.5,  9.5,  3.5,    1,  3.5],
#            [21.5,   11, 12.5,   13,   10,    6,   13,    7,  3.5,    1]
#])

TCPWindow=8388608

folder=sys.argv[1]
simu=sys.argv[2]
size=float(sys.argv[3])
pos=int(sys.argv[4])
contentId=sys.argv[5]
Id=sys.argv[6]
name='Controller_sim{simu}_Log.csv'.format(simu=simu)
delayfile='delays_sim{simu}_Log.csv'.format(simu=simu)
Servers={}
ServersIP=[]
#client=[float(sys.argv[13]),int(sys.argv[14]),float(sys.argv[15])]
#T=[float(sys.argv[16])/10000, float(sys.argv[17])/20000,float(sys.argv[18])/20000,float(sys.argv[19])/100000]
#Tp=float(sys.argv[13])
#St= int(sys.argv[14])
#Rb= float(sys.argv[15])

def main():
  migrationTime=[]
  os.chdir(folder)
  file=pd.read_csv(delayfile, sep=',',index_col=False, header=None)
  delays=np.array(file)
  concatenarServers(migrationTime,delays)
  selecionado=pli()
  Choice = ServersIP.index(selecionado)
  print(Choice,migrationTime[Choice])

def concatenarServers(migrationTime,delays):
  totalMemory=[]
  freeMemory=[]
  memoryUsage=[]
  hasContent=[]
  band=[]
  latency=[]
  file = open(name,"r")
  next(file)
  i=0
  for line in file:
    fields = line.split(";")
    if(float(fields[2])>=size):
      totalMemory.append(float(fields[1]))
      freeMemory.append(float(fields[2]))
      ServersIP.append(fields[3])
      contents=fields[4].split("/")
      band.append(len(contents))
      if contentId in contents:
        hasContent.append(i)
      time=delays[pos][i]
      latency.append(time)
      memoryUsage.append(freeMemory[i]-size)
    i+=1

  for i in range(0,len(ServersIP)):
    if i in hasContent:
      migrationTime.append(0)
    else:
      times=[]
      for j in hasContent:
        times.append(delays[pos][j])
      if len(times)==0:
        times.append(delays[i][7])
      maxThroughput=(TCPWindow/(min(times)*1000))/8
      if maxThroughput > 120:
        maxThroughput=120
      time=size/maxThroughput
      migrationTime.append(time)
  #print(latency)
  #print(migrationTime)
  #print(memoryUsage)
  migrationTime = np.asarray(migrationTime)
  memoryUsage = np.asarray(memoryUsage)
  latency = (latency - min(latency)) / (max(latency) - min(latency))
  #print(latency)
  migrationTime = (migrationTime - min(migrationTime)) / (max(migrationTime) - min(migrationTime))
  #print(migrationTime)
  if max(memoryUsage) == min(memoryUsage):
    memoryUsage= memoryUsage*0
  else:
    memoryUsage = (memoryUsage - min(memoryUsage)) / (max(memoryUsage) - min(memoryUsage))
  #print(memoryUsage)
  for i in range(0,len(ServersIP)):
    ServerIP = ServersIP[i]
    if (band[i]<10):
    #  print('Delays: ',delays)
    #  print('ThroughputValues: ',ThroughputValues)
    #  print('Stalls: ',StallValues)
    #  print('Rebuffers: ',RebufferValues)
      Servers[ServerIP] = [latency[i],migrationTime[i],memoryUsage[i],band[i]]
    #Servers[ServerIP] = [StallValues[i],RebufferValues[i],ThroughputValues[i],delays[i]]
  return Servers

def pli():
  model = Model("PLI")
  l=folder.split("/")
  r=range(1,11)
  fogs=list(Servers.keys())#[0,0,0,0,0,0,0,0,0,0]
  x=model.binary_var_list(fogs)
  model.minimize(model.sum((Servers[fog][0]+Servers[fog][1]+Servers[fog][2])*x[k] for k,fog in enumerate(Servers.keys())))

  for i in x:
    model.add_constraint(model.sum(x) == 1)
  for j in Servers.keys():
    #model.add_constraint(Servers[j][2] >= 0)
    model.add_constraint(Servers[j][3] < 10)

  #model.print_information()
  if not model.solve():
    print('*** Problem has no solution')
  else:
    for index, dvar in enumerate(model.solution.iter_variables()):
        resp=dvar.to_string()
    return resp
  #l=folder.split("/")
  #os.chdir('..')
  #os.chdir('..')
  #os.chdir('..')
  #os.chdir('..')
  #os.chdir(os.path.dirname(__file__))
  #doc='res{num}_{simu}.csv'.format(simu=simu,num=l[2])
  #file=pd.read_csv(doc, sep=',',index_col=False,header=None)
  #Line=np.array(file.iloc[int(Id)])
  #resp=list(Line).index(1)
  #return resp


if __name__=="__main__":
    main()
