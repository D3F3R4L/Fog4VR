from AnalyticHierarchyProcess import AHP
import glob
import os
import sys
import operator
import csv
import numpy as np
import pandas as pd

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
name='Controller_sim{simu}_Log.csv'.format(simu=simu)
delayfile='delays_sim{simu}_Log.csv'.format(simu=simu)
#delays=[sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6]]
#ip=sys.argv[7]
#T={'1.0.0.1': float(sys.argv[8])/10000,'2.0.0.1': float(sys.argv[9])/20000,'3.0.0.1': float(sys.argv[10])/20000,'4.0.0.1': float(sys.argv[11])/100000}
Servers={}
ServersIP=[]
ahp = AHP (log=True)

def main():
  migrationTime=[]
  os.chdir(folder)
  file=pd.read_csv(delayfile, sep=',',index_col=False, header=None)
  delays=np.array(file)
  concatenarServers(migrationTime,delays)
  #print(Servers)
  ServersScores=ahp.Politica(Servers)
  #A = list(T.keys())
  #B = list(ServersScores.keys())
  #commonKeys = set(A) - (set(A) - set(B))
  #for key in commonKeys:
  #  if(T[key] >= 1 and key!='4.0.0.1'):
  #    del ServersScores[key]
  ServersScores=list(ServersScores.items())
  ServersScores.sort(key=operator.itemgetter(1),reverse=False)
  #print(ServersScores)
  Choice = ServersIP.index(ServersScores[0][0])
  print(Choice,migrationTime[Choice])
  #print(list(sum(ServersScores,())))
  #if len(ServersScores)>0:
  #  x = list(sum(ServersScores, ()))
  #  print(' '.join(x[0::2]))
  #else:
  #  print(5)
  '''
  if (ServersScores[2][1]>0.5):
    if (ServersScores[1][1]>0.5):
      if (ServersScores[0][1]>0.5):
        print(ServersScores[2][0],ServersScores[1][0],ServersScores[0][0])
      else:
        print(ServersScores[2][0],ServersScores[1][0])
    else:
      print(ServersScores[2][0])
  else:
    print(5)
  
  #print(ServersScores[2][0],ServersScores[1][0],ServersScores[0][0])
  ServersScores.sort(key=operator.itemgetter(0))
  line=[str(ServersScores[0][1]),str(ServersScores[1][1]),str(ServersScores[2][1])]
  csv.register_dialect('myDialect',delimiter = ';',quoting=csv.QUOTE_NONE,skipinitialspace=True)
  file='sim{simu}_ServerScores.csv'.format(simu=simu)
  with open(file, 'a') as writeFile:
    writer = csv.writer(writeFile, dialect='myDialect')
    writer.writerow(line)
  writeFile.close()'''

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
      memoryUsage.append(size/freeMemory[i])
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
      Servers[ServerIP] = [latency[i],migrationTime[i],memoryUsage[i]]
    #Servers[ServerIP] = [StallValues[i],RebufferValues[i],ThroughputValues[i],delays[i]]
  return Servers

if __name__=="__main__":
    main()