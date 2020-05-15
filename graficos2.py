import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import os
import glob
import operator
import argparse
import pandas as pd

parser = argparse.ArgumentParser(description='Script to make graphs for dash migration simulation')
parser.add_argument('--segmentfile','-seg',default="segmentSizesBigBuck.txt", type=str,help='Name of segmentfile used.Default is segmentSizesBigBuck1A.txt')
parser.add_argument('--adaptAlgo','-Adpt',default="festive", type=str,help='Name of adaptation algorithm used.Default is festive, possible values are: festive, panda, tobasco')
parser.add_argument('--Clients','-c', type=int,help='Number of Clients in the simulation')
#parser.add_argument('--Politica','-p', type=int,help='Politica used in the simulation')
parser.add_argument('--runs','-r', type=int,default=1,help='Number of simulations to make the graphs. Default is 1')
args = parser.parse_args()
if args.adaptAlgo!="festive" and args.adaptAlgo!="panda" and args.adaptAlgo!="tobasco":
    parser.error("Wrong adaptation algorithm")
if args.runs <= 0 :
    parser.error("Invalid number of runs")

runs=args.runs
segmentfile=args.segmentfile
adaptAlgo=args.adaptAlgo
numberOfClients=args.Clients
#politica=args.Politica
MeansTotals=[]
MeansBW=[]
throughtputTotals=[]
timeTotals=[]
MMEsTotals=[]
qualityLevelTotals=[]
StallsTotals=[]
RebuffersTotals=[]
bitSwitchtotals=[]
bitSwitchUptotals=[]
bitSwitchDowntotals=[]
bitSwitchtotalsConfInt=[]
bitSwitchUptotalsConfInt=[]
bitSwitchDowntotalsConfInt=[]
ClientsTotals=[]
QualityMeanTotal=[]
fairness=[]

colors=['dimgray', 'gray', 'darkgray','silver','lightgrey']
labels=['Fog4Video','Greedy','Random']

def main():
  print('Beginning')
  segfile='src/dash-migration/dash/{seg}'.format(seg=segmentfile)
  file = open(segfile,"r")
  collums= file.readline().split(" ")
  numSegments=len(collums)-1
  #os.chdir('..')
  folder='dash-log-files/{algo}/{num}'.format(algo=adaptAlgo,num=numberOfClients)
  folders=os.listdir(folder)
  os.chdir(folder)
  folders.sort(key=operator.itemgetter(0))
  aux=[]
  for i in folders:
    if i.isdigit():
      aux.append(i)
  folders=aux
  #print(folders)
  for i in folders:
    #folder='dash-log-files/{algo}/{num}/{pol}'.format(algo=adaptAlgo,num=numberOfClients,pol=i)
    print('------Politica ',i,'------')
    os.chdir(i)
    #bufferUnderrunGraphs()
    #throughputGraphs(numSegments)
    qualityGraphs(numSegments)
    throughtputServer()
    StallsGraphs()
    RebufferGraphs()
    os.chdir('..')
  graphtotals(numSegments)
  print('Finished')
  #print(os.getcwd())
  #print(os.listdir())

###################
# Buffer Underrun 
###################
def bufferUnderrunGraphs():
  files= '*sim{simu}_*bufferUnderrunLog*'.format(simu=simulation)
  bufferUnderrunFiles = glob.glob(files)
  #print(bufferUnderrunFiles)
  S1timeTotal=[]
  S2timeTotal=[]
  S3timeTotal=[]
  j=0
  while(j<len(bufferUnderrunFiles)):
    #print(j)
    name = bufferUnderrunFiles[j]
    file = open(name,"r")
    next(file)
    Buffer_Underrun_Total_Time=[]
    for line in file:
      fields = line.split(";")
      #print(fields)
      if(j!=0):
        timeTotal.append(float(fields[3])+timeTotal[len(timeTotal)-1])
      else:
        timeTotal.append(float(fields[3]))
    if j==0 and len(timeTotal)==0 :
      timeTotal.append(0)
    file.close()
    j+=1
  
  plt.plot(totalUnderruns,timeTotal , label='linear')
  plt.xlabel('Buffer Underrun')
  plt.ylabel('Total Time')
  plt.title("Buffer Underrun Total Duration Time")
  save = 'BufferUnderrunTotalTime.pdf'
  plt.savefig(save)
  plt.close()

  S1Quality=np.zeros(numSegments)
  S2Quality=np.zeros(numSegments)
  S3Quality=np.zeros(numSegments)
  S1Clients=np.zeros(numSegments)
  S2Clients=np.zeros(numSegments)
  S3Clients=np.zeros(numSegments)
  j=0
  while(j<len(playbackFiles)):
    name = playbackFiles[j]
    file = open(name,"r")
    next(file)
    segment=[]
    qualityLevel=[]
    Server=[]
    for line in file:
      fields = line.split(";")
      segment.append(float(fields[0]))
      qualityLevel.append(float(fields[2]))
      Server.append(str(fields[3]))
    file.close()

    i=0
    for x1, x2, y1,y2 in zip(segment, segment[1:], qualityLevel, qualityLevel[1:]):
      if str(Server[i])=="1.0.0.1":
        S1Quality[i]=S1Quality[i]+y1
        S1Clients[i]=S1Clients[i]+1
      elif str(Server[i])=='2.0.0.1' :
        S2Quality[i]=S2Quality[i]+y1
        S2Clients[i]=S2Clients[i]+1
      else:
        S3Quality[i]=S3Quality[i]+y1
        S3Clients[i]=S3Clients[i]+1
      i+=1
    j+=1

'''
  Buffer_Underrun_Started_At.insert(0,0.0)
  Buffer_Underrun_Total_Time.insert(0,0.0)
  y1 = np.arange(len(Buffer_Underrun_Started_At))
  plt.step(Buffer_Underrun_Started_At, y1, where= 'post',label='')
  plt.plot(Buffer_Underrun_Started_At, y1, 'C0o', alpha=0.5)
  plt.xlabel('Segundos')
  plt.ylabel('Estouros')
  plt.title("Numero de estouros de buffer")
  save = 'sim{simu}_cl{iter}_NumbersOfBufferUnderrun.pdf'.format(simu=simulation, iter=j)
  plt.savefig(save)
  plt.close()
  plt.plot(Buffer_Underrun_Started_At,Buffer_Underrun_Total_Time , label='linear')
  plt.xlabel('Segundos')
  plt.ylabel('Tempo Total')
  plt.title("Buffer Underrun Total Duration Time")
  save = 'sim{simu}_cl{iter}_BufferUnderrunDurationTime.pdf'.format(simu=simulation, iter=j)
  plt.savefig(save)
  plt.close()
'''

################
# Throughput 
################
def throughputGraphs(numSegments):
  throughputFiles = glob.glob('*throughputLog*')
  S1Throughput=np.zeros(numSegments)
  S2Throughput=np.zeros(numSegments)
  S3Throughput=np.zeros(numSegments)
  S4Throughput=np.zeros(numSegments)
  S1Clients=np.zeros(numSegments)
  S2Clients=np.zeros(numSegments)
  S3Clients=np.zeros(numSegments)
  S4Clients=np.zeros(numSegments)
  j=0
  while(j<len(throughputFiles)):
    name = throughputFiles[j]
    file = open(name,"r")
    next(file)
    Time=[]
    Mbps=[]
    Server=[]
    for line in file:
      fields = line.split(";")
      Time.append(float(fields[0]))
      Mbps.append(float(fields[1]))
      Server.append(str(fields[2]))
    file.close()
    i=0
    for x1, x2, y1,y2 in zip(Time, Time[1:], Mbps, Mbps[1:]):
      if str(Server[i])=="1.0.0.1":
        S1Throughput[i]=S1Throughput[i]+y1
        S1Clients[i]=S1Clients[i]+1
      elif str(Server[i])=='2.0.0.1' or str(Server[i])=='1.0.0.3' :
        S2Throughput[i]=S2Throughput[i]+y1
        S2Clients[i]=S2Clients[i]+1
      elif str(Server[i])=='3.0.0.1' or str(Server[i])=='1.0.0.5':
        S3Throughput[i]=S3Throughput[i]+y1
        S3Clients[i]=S3Clients[i]+1
      else:
        S4Throughput[i]=S4Throughput[i]+y1
        S4Clients[i]=S4Clients[i]+1
      i+=1
    j+=1
  
  x = np.arange(0,2*(len(Time)),2)
  S1Throughput=divisor(S1Throughput,S1Clients)
  S2Throughput=divisor(S2Throughput,S2Clients)
  S3Throughput=divisor(S3Throughput,S3Clients)
  S4Throughput=divisor(S4Throughput,S4Clients)
  plt.plot(x,S1Throughput,color='r')
  plt.plot(x,S2Throughput,color='g')
  plt.plot(x,S3Throughput,color='b')
  plt.plot(x,S4Throughput,color='y')
  plt.xlabel('Seconds')
  plt.ylabel('Mb/s')
  red_line = mlines.Line2D([], [], color='Red',markersize=15, label='Tier-3')
  green_line = mlines.Line2D([], [], color='g',markersize=15, label='Tier-2 EP-2')
  blue_line = mlines.Line2D([], [], color='b',markersize=15, label='Tier-2 EP-1')
  yellow_line = mlines.Line2D([], [], color='y',markersize=15, label='Tier-1')
  plt.legend(title='Enforcement Point',handles=[red_line,green_line,blue_line,yellow_line])
  plt.title("Server Throughput")
  save = 'ServerThroughput.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()

def throughtputServer():
  i=0
  Times=[]
  Throughputs=[]
  MMEs=[]
  TimesAux=[]
  ThroughputsAux=[]
  MMEsAux=[]
  print('Working in throughtputServer...')
  while(i<runs):
    simulation=i
    files= '*throughputServer*sim{simu}_*'.format(simu=simulation)
    throughputFiles = glob.glob(files)
    throughputFiles.sort()
    #print(throughputFiles)
    j=0
    while(j<len(throughputFiles)):
      name = throughputFiles[j]
      file = open(name,"r")
      next(file)
      Time=[]
      Mbps=[]
      MME=[]
      for line in file:
        fields = line.split(";")
        Time.append(float(fields[0]))
        Mbps.append(float(fields[1]))
        MME.append(float(fields[2]))
      TimesAux.append(Time)
      ThroughputsAux.append(Mbps)
      MMEsAux.append(MME)
      j+=1
    i+=1
  for k in range(0,4):
    Times.append(min(TimesAux , key=len))
    timeTotals.append(Times[k])
    aux=ThroughputsAux[k::4]
    for h in range (0,len(aux)):
      aux[h]=aux[h][0:len(Times[k])]
    Throughputs.append(sum(np.array(aux))/runs)
    throughtputTotals.append(Throughputs[k])
    aux=MMEsAux[k::4]
    for h in range (0,len(aux)):
      aux[h]=aux[h][0:len(Times[k])]
    MMEs.append(sum(np.array(aux))/runs)
    MMEsTotals.append(MMEs[k])
  plt.plot(Times[0],Throughputs[0],color='r',ls='--',lw=3)
  plt.plot(Times[1],Throughputs[1],color='g',ls='-.',lw=3)
  plt.plot(Times[2],Throughputs[2],color='b',ls=':',lw=3)
  plt.plot(Times[3],Throughputs[3],color='y',ls='-',lw=1)
  plt.xlabel('Seconds')
  plt.ylabel('Mb/s')
  red_line = mlines.Line2D([], [], color='Red',ls='--',lw=3, label='Tier-3')
  green_line = mlines.Line2D([], [], color='g',ls='-.',lw=3, label='Tier-2 EP-2')
  blue_line = mlines.Line2D([], [], color='b',ls=':',lw=3, label='Tier-2 EP-1')
  yellow_line = mlines.Line2D([], [], color='y',ls='-',lw=2, label='Tier-1')
  plt.legend(title='Enforcement Point',handles=[red_line,green_line,blue_line,yellow_line])
  plt.grid(True,alpha=0.4,linestyle='--')
  plt.title("Server Throughput")
  save = 'ServerThroughput.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()

  plt.plot(Times[0],MMEs[0],color='r')
  plt.plot(Times[1],MMEs[1],color='g')
  plt.plot(Times[2],MMEs[2],color='b')
  plt.plot(Times[3],MMEs[3],color='y')
  plt.xlabel('Seconds')
  plt.ylabel('Mb/s')
  red_line = mlines.Line2D([], [], color='Red',markersize=15, label='Tier-3')
  green_line = mlines.Line2D([], [], color='g',markersize=15, label='Tier-2 EP-2')
  blue_line = mlines.Line2D([], [], color='b',markersize=15, label='Tier-2 EP-1')
  yellow_line = mlines.Line2D([], [], color='y',markersize=15, label='Tier-1')
  plt.legend(title='Enforcement Point',handles=[red_line,green_line,blue_line,yellow_line])
  plt.title("Exponential Moving Average of Server Throughput")
  plt.grid(True,alpha=0.4,linestyle='--')
  save = 'MMEServerThroughput.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  print('ThroughtputServer Done')

###################
# Playback Quality 
###################
def qualityGraphs(numSegments):
  k=0
  print('Working in QualityGraphs...')
  bestScore=-1
  worstScore=10000000
  Means=[]
  MeansSV=[]
  bestClientQuality=[]
  bestClientServer=[]
  worstClientQuality=[]
  worstClientServer=[]
  S1QualityMean=[]
  S2QualityMean=[]
  S3QualityMean=[]
  S4QualityMean=[]
  S1ClientsMean=[]
  S2ClientsMean=[]
  S3ClientsMean=[]
  S4ClientsMean=[]
  bitSwitchMean=[]
  bitSwitchUpMean=[]
  bitSwitchDownMean=[]
  QualityMean=[]
  while k<runs:
    simulation=k
    bitSwitch=0
    bitSwitchUp=0
    bitSwitchDown=0
    files= '*sim{simu}_*playbackLog*'.format(simu=simulation)
    playbackFiles = glob.glob(files)
    S1Quality=np.zeros(numSegments)
    S2Quality=np.zeros(numSegments)
    S3Quality=np.zeros(numSegments)
    S4Quality=np.zeros(numSegments)
    S1Clients=np.zeros(numSegments)
    S2Clients=np.zeros(numSegments)
    S3Clients=np.zeros(numSegments)
    S4Clients=np.zeros(numSegments)
    j=0
    while(j<len(playbackFiles)):
      name = playbackFiles[j]
      file = open(name,"r")
      next(file)
      segment=[]
      qualityLevel=[]
      Server=[]
      for line in file:
        fields = line.split(";")
        segment.append(float(fields[0]))
        qualityLevel.append(float(fields[2]))
        Server.append(str(fields[3]))
      file.close()
      ClientScore=sum(qualityLevel)

      if(ClientScore>bestScore):
        print('best: ', name)
        bestScore=ClientScore
        bestClientQuality=qualityLevel
        bestClientServer=Server
      elif(ClientScore<worstScore):
        print('Worst: ',name)
        worstScore=ClientScore
        worstClientQuality=qualityLevel
        worstClientServer=Server

      i=0
      for x1, x2, y1,y2 in zip(segment, segment[1:], qualityLevel, qualityLevel[1:]):
        if str(Server[i])=="1.0.0.1":
          S1Quality[i]=S1Quality[i]+y1
          S1Clients[i]=S1Clients[i]+1
        elif str(Server[i])=='2.0.0.1' or str(Server[i])=='1.0.0.3' :
          S2Quality[i]=S2Quality[i]+y1
          S2Clients[i]=S2Clients[i]+1
        elif str(Server[i])=='3.0.0.1' or str(Server[i])=='1.0.0.5':
          S3Quality[i]=S3Quality[i]+y1
          S3Clients[i]=S3Clients[i]+1
        else:
          S4Quality[i]=S4Quality[i]+y1
          S4Clients[i]=S4Clients[i]+1
        i+=1
      for l in range (0,len(qualityLevel)):
        if l!=0:
          if (qualityLevel[l]!=qualityLevel[l-1]):
            bitSwitch+=1
            if (qualityLevel[l]>qualityLevel[l-1]):
              bitSwitchUp+=1
            else:
              bitSwitchDown+=1
      j+=1
    #print(np.sum([S1Quality,S2Quality,S3Quality,S4Quality],0))
    QualityMean.append(np.sum([S1Quality,S2Quality,S3Quality,S4Quality],0)/18)
    #print(QualityMean)
    S1Quality=divisor(S1Quality,S1Clients)
    S2Quality=divisor(S2Quality,S2Clients)
    S3Quality=divisor(S3Quality,S3Clients)
    S4Quality=divisor(S4Quality,S4Clients)
    S1QualityMean.append(toBitrate(S1Quality))
    S2QualityMean.append(toBitrate(S2Quality))
    S3QualityMean.append(toBitrate(S3Quality))
    S4QualityMean.append(toBitrate(S4Quality))
    S1ClientsMean.append(S1Clients)
    S2ClientsMean.append(S2Clients)
    S3ClientsMean.append(S3Clients)
    S4ClientsMean.append(S4Clients)
    bitSwitchMean.append(bitSwitch/18)
    bitSwitchUpMean.append(bitSwitchUp/18)
    bitSwitchDownMean.append(bitSwitchDown/18)
    k+=1
  QualityMeanTotal.append(toBitrate(np.mean(QualityMean,0)))
  #print(QualityMeanTotal)
  worstClientQuality=toBitrate(worstClientQuality)
  bestClientQuality=toBitrate(bestClientQuality)
  S1QualityMean=np.mean(S1QualityMean,axis=0)
  S2QualityMean=np.mean(S2QualityMean,axis=0)
  S3QualityMean=np.mean(S3QualityMean,axis=0)
  S4QualityMean=np.mean(S4QualityMean,axis=0)
  S1ClientsMean=np.mean(S1ClientsMean,axis=0)
  S2ClientsMean=np.mean(S2ClientsMean,axis=0)
  S3ClientsMean=np.mean(S3ClientsMean,axis=0)
  S4ClientsMean=np.mean(S4ClientsMean,axis=0)
  bitSwitchtotals.append(np.mean(bitSwitchMean))
  bitSwitchUptotals.append(np.mean(bitSwitchUpMean))
  bitSwitchDowntotals.append(np.mean(bitSwitchDownMean))
  bitSwitchtotalsConfInt.append((1.96*(np.std(bitSwitchMean)/np.sqrt(runs))))
  bitSwitchUptotalsConfInt.append((1.96*(np.std(bitSwitchUpMean)/np.sqrt(runs))))
  bitSwitchDowntotalsConfInt.append((1.96*(np.std(bitSwitchDownMean)/np.sqrt(runs))))
  qualityLevelTotals.append(S1QualityMean)
  qualityLevelTotals.append(S2QualityMean)
  qualityLevelTotals.append(S3QualityMean)
  qualityLevelTotals.append(S4QualityMean)
  x=np.arange(0,numSegments)
  fig,ax =plt.subplots()
  p1,=plt.plot(x,S1QualityMean,color='r',markersize=15, label='Tier-3')
  p2,=plt.plot(x,S2QualityMean,color='g',markersize=15, label='Tier-2 EP-2')
  p3,=plt.plot(x,S3QualityMean,color='b',markersize=15, label='Tier-2 EP-1')
  p4,=plt.plot(x,S4QualityMean,color='y',markersize=15, label='Tier-1')
  plt.xlabel('Chunks')
  plt.ylabel('Video bitrate(Kbps)')
  MeansSV.append(int(np.mean(S1QualityMean)))
  MeansSV.append(int(np.mean(S2QualityMean)))
  MeansSV.append(int(np.mean(S3QualityMean)))
  MeansSV.append(int(np.mean(S4QualityMean)))
  MeansTotals.append(MeansSV)
  red_line = mlines.Line2D([], [], color='r',markersize=15, label='{mean} Kbps'.format(mean=MeansSV[0]))
  green_line = mlines.Line2D([], [], color='g',markersize=15, label='{mean} Kbps'.format(mean=MeansSV[1]))
  blue_line = mlines.Line2D([], [], color='b',markersize=15, label='{mean} Kbps'.format(mean=MeansSV[2]))
  yellow_line = mlines.Line2D([], [], color='y',markersize=15, label='{mean} Kbps'.format(mean=MeansSV[3]))
  plt.yticks( [0,400,650,1000,1500,2250,3400,4700,6000], ('0','400', '650', '1000', '1500', '2250','3400','4700','6000') )
  l1=plt.legend(title='Enforcement Point',handles=[p1,p2,p3,p4],bbox_to_anchor=(1.04,1), loc="upper left",fancybox=True, shadow=True)
  plt.title("Video Bitrate")
  plt.legend(title='Bitrate Average',handles=[red_line,green_line,blue_line,yellow_line],bbox_to_anchor=(1.04,0.5), loc="center left",fancybox=True, shadow=True)
  plt.grid(True,alpha=0.4,linestyle='--')
  ax.add_artist(l1)
  save = 'qualityLevel.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  
  i=0
  fig,ax =plt.subplots()
  p1,=plt.plot([],[],color='r',markersize=15, label='Tier-3')
  p2,=plt.plot([],[],color='g',markersize=15, label='Tier-2 EP-2')
  p3,=plt.plot([],[],color='b',markersize=15, label='Tier-2 EP-1')
  p4,=plt.plot([],[],color='y',markersize=15, label='Tier-1')
  for x1, x2, y1,y2 in zip(x, x[1:], bestClientQuality, bestClientQuality[1:]):
    if str(bestClientServer[i])=="1.0.0.1":
      plt.plot([x1, x2], [y1, y2], 'r')
    elif str(bestClientServer[i])=="2.0.0.1":
      plt.plot([x1, x2], [y1, y2], 'g')
    elif(str(bestClientServer[i])=="3.0.0.1"):
      plt.plot([x1, x2], [y1, y2], 'b')
    else:
      plt.plot([x1, x2], [y1, y2], 'y')
    i+=1
  #print(bestClientQuality)
  Means.append(int(np.mean(bestClientQuality)))
  red_line = mlines.Line2D([], [], color='black',markersize=15, label='{mean} Kbps'.format(mean=Means[0]))
  plt.yticks( [0,400,650,1000,1500,2250,3400,4700,6000], ('0','400', '650', '1000', '1500', '2250','3400','4700','6000') )
  l1=plt.legend(title='Enforcement Point',handles=[p1,p2,p3,p4],bbox_to_anchor=(1.04,1), loc="upper left",fancybox=True, shadow=True)
  ax.add_artist(l1)
  plt.grid(True,alpha=0.4,linestyle='--')
  plt.xlabel('Chunks')
  plt.ylabel('Video bitrate(Kbps)')
  plt.legend(title='Bitrate Average',handles=[red_line],bbox_to_anchor=(1.04,0.5), loc="center left",fancybox=True, shadow=True)
  plt.title("Video Bitrate Best Client")
  save = 'qualityLevelBestClient.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()

  i=0
  fig,ax =plt.subplots()
  p1,=plt.plot([],[],color='r',markersize=15, label='Tier-3')
  p2,=plt.plot([],[],color='g',markersize=15, label='Tier-2 EP-2')
  p3,=plt.plot([],[],color='b',markersize=15, label='Tier-2 EP-1')
  p4,=plt.plot([],[],color='y',markersize=15, label='Tier-1')
  for x1, x2, y1,y2 in zip(x, x[1:], worstClientQuality, worstClientQuality[1:]):
    if str(worstClientServer[i])=="1.0.0.1":
      plt.plot([x1, x2], [y1, y2], 'r')
    elif str(worstClientServer[i])=="2.0.0.1":
      plt.plot([x1, x2], [y1, y2], 'g')
    elif(str(worstClientServer[i])=="3.0.0.1"):
      plt.plot([x1, x2], [y1, y2], 'b')
    else:
      plt.plot([x1, x2], [y1, y2], 'y')
    i+=1
  Means.append(int(np.mean(worstClientQuality)))
  if np.isnan(Means[1]):
    Means[1]=np.nan_to_num(Means[1])
  MeansBW.append(Means)
  red_line = mlines.Line2D([], [], color='black',markersize=15, label='{mean} Kbps'.format(mean=Means[1]))
  plt.yticks( [0,400,650,1000,1500,2250,3400,4700,6000], ('0','400', '650', '1000', '1500', '2250','3400','4700','6000') )
  l1=plt.legend(title='Enforcement Point',handles=[p1,p2,p3,p4],bbox_to_anchor=(1.04,1), loc="upper left",fancybox=True, shadow=True)
  ax.add_artist(l1)
  plt.grid(True,alpha=0.4,linestyle='--')
  plt.xlabel('Segments')
  plt.ylabel('Video bitrate(Kbps)')
  plt.legend(title='Bitrate Average',handles=[red_line],bbox_to_anchor=(1.04,0.5), loc="center left",fancybox=True, shadow=True)
  plt.title("Video Bitrate Worst Client")
  save = 'qualityLevelWorstClient.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()

  red_line = mlines.Line2D([], [], color='dimgray',markersize=15, label='Tier-3',lw=10)
  green_line = mlines.Line2D([], [], color='gray',markersize=15, label='Tier-2 EP-2',lw=10)
  blue_line = mlines.Line2D([], [], color='darkgray',markersize=15, label='Tier-2 EP-1',lw=10)
  yellow_line = mlines.Line2D([], [], color='gainsboro',markersize=15,label='Tier-1',lw=10)
  width = 0.6
  fig,ax =plt.subplots()
  new_x = [i for i in x]
  p1 = plt.bar(new_x, S1ClientsMean, width=3,color='dimgray',align='edge')
  p2 = plt.bar(new_x, S2ClientsMean, width=3,bottom=S1ClientsMean,color='gray',align='edge')
  p3 = plt.bar(new_x, S3ClientsMean, width=3,bottom=np.array(S1ClientsMean)+np.array(S2ClientsMean),color='darkgray',align='edge')
  p4 = plt.bar(new_x, S4ClientsMean, width=3,bottom=np.array(S1ClientsMean)+np.array(S2ClientsMean)+np.array(S3ClientsMean),color='gainsboro',align='edge')
  xmajor_ticks = np.arange(0, (numSegments+1), 30)
  #xminor_ticks = np.arange(0, (numSegments+1), 1)
  ymajor_ticks = np.arange(0, (S1ClientsMean[0]+S2ClientsMean[0]+S3ClientsMean[0]+S4ClientsMean[0]+1), 5)
  #yminor_ticks = np.arange(0, (S1ClientsMean[0]+S2ClientsMean[0]+S3ClientsMean[0]+S4ClientsMean[0]+1), 1)
  ax.set_xticks(xmajor_ticks)
  #ax.set_xticks(xminor_ticks, minor=True)
  ax.set_yticks(ymajor_ticks)
  #ax.set_yticks(yminor_ticks, minor=True)
  ax.set_xlim(0, numSegments)
  ax.set_ylim(0, (S1ClientsMean[0]+S2ClientsMean[0]+S3ClientsMean[0]+S4ClientsMean[0]+1))
  #plt.xticks(rotation=45,fontsize=10)
  #plt.yticks(fontsize=10)
  ax.grid(which='both',alpha=0.4,linestyle='--')
  plt.xlabel('Chunks',fontsize=14)
  plt.ylabel('Clients per Server Average', fontsize=14)
  plt.legend(handles=[red_line,green_line,blue_line,yellow_line],bbox_to_anchor=(0.5, 1.3),loc='upper center', fontsize=14,ncol=4,fancybox=True, shadow=True)
  save = 'clientsPerServer.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  fair=[]
  fair.append(np.mean(S1ClientsMean)/10)
  fair.append(np.mean(S2ClientsMean)/10)
  fair.append(np.mean(S3ClientsMean)/10)
  fair.append(np.mean(S4ClientsMean)/10)
  fairness.append(pow(np.sum(fair),2)/(len(fair)*(np.sum(np.power(fair,2)))))
  ClientsTotals.append([S1ClientsMean,S2ClientsMean,S3ClientsMean,S4ClientsMean])
  print('QualityGraphs Done')

def divisor(vet1,vet2):
  j=0
  resp=[]
  while j<len(vet1):
    if vet2[j]==0:
      resp.append(-1)
    else:
      resp.append(vet1[j]/vet2[j])
    j+=1
  return resp

def StallsGraphs():
  k=0
  collums=[]
  print('Working in StallLog...')
  while(k<runs):
    simulation=k
    files= '*sim{simu}_*StallLog*'.format(simu=simulation)
    StallFile = glob.glob(files)
    j=0
    while(j<len(StallFile)):
      name = StallFile[j]
      with open(name) as f:
        data = f.readlines()
      fields = data[-1].split(";")
      collums.append(fields)
      j+=1
    k+=1
  barGraphs(collums,'Stalls')  
  print('StallLog Done')

def RebufferGraphs():
  k=0
  collums=[]
  print('Working in RebufferLog...')
  while (k<runs):
    simulation=k
    files= '*sim{simu}_*RebufferLog*'.format(simu=simulation)
    RebufferFile = glob.glob(files)
    j=0
    while(j<len(RebufferFile)):
      name = RebufferFile[j]
      with open(name) as f:
        data = f.readlines()
      fields = data[-1].split(";")
      collums.append(fields)
      j+=1
    k+=1
  barGraphs(collums,'Rebuffer')
  print('RebufferLog Done')

def barGraphs(collums, graph):
  default=[[],[],[],[]]
  defaultMSE=[]
  defaultMean=[]
  MME=[[],[],[],[]]
  MMEMSE=[]
  MMEMean=[]
  l=1
  k=0
  while (k<runs):
    while(l<len(collums[k])-1):
      if (l%2!=0):
      	default[int((l/2)-0.5)].append(float(collums[k][l]))
      else:
        MME[int((l/2)-1)].append(float(collums[k][l]))
      l+=1
    l=1
    k+=1
  for i in range(0,4):
  	defaultMean.append(np.mean(default[i]))
  	defaultMSE.append(np.std(default[i]))
  	MMEMean.append(np.mean(MME[i]))
  	MMEMSE.append(np.std(MME[i]))
  ind = np.arange(len(default))
  width = 0.4  
  fig, ax = plt.subplots()
  rects1 = ax.bar(ind - width/2, defaultMean, width, yerr=defaultMSE,label='Media')
  rects2 = ax.bar(ind + width/2, MMEMean, width, yerr=MMEMSE,label='MME')
  if (graph=='Stalls'):
    StallsTotals.append(defaultMean)
    ax.set_ylabel('Quantity')
    ax.set_title('Number of Stalls per Server')
    ax.set_xticks(ind)
    ax.set_xticklabels(('Tier-3', 'Tier-2 EP-2', 'Tier-2 EP-1', 'Tier-1'))
    ax.legend()
    save = 'Stalls.pdf'
  else:
    RebuffersTotals.append(defaultMean)
    ax.set_ylabel('Seconds')
    ax.set_title('Rebuffers duration per Server')
    ax.set_xticks(ind)
    ax.set_xticklabels(('Tier-3', 'Tier-2 EP-2', 'Tier-2 EP-1', 'Tier-1'))
    ax.legend()
    save = 'Rebuffers.pdf'
  
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()

def graphtotals(numSegments):
  print('Working in Comparation Graphs...')
  print('Throughputs Comparation...')
  for i in range (0,4):
    plt.plot(timeTotals[i],throughtputTotals[i],color='r',ls='--',lw=2)
    plt.plot(timeTotals[i+4],throughtputTotals[i+4],color='g',ls='-.',lw=2)
    plt.plot(timeTotals[i+8],throughtputTotals[i+8],color='b',ls=':',lw=2)
    plt.xlabel('Seconds')
    plt.ylabel('Throughput (Mb/s)')
    red_line = mlines.Line2D([], [], color='Red',markersize=15, label='Fog4Video')
    green_line = mlines.Line2D([], [], color='g',markersize=15, label='Greedy')
    blue_line = mlines.Line2D([], [], color='b',markersize=15, label='Random')
    plt.legend(handles=[red_line,green_line,blue_line])
    name='Tier-2 EP-{pol}'.format(pol=(i+1))
    if i==3:
      name='Tier-1'
    if i==0:
      save= 'Tier-3'
    plt.grid(True,alpha=0.4,linestyle='--')
    plt.title(name)
    plt.savefig(name,bbox_inches="tight",dpi=300)
    plt.close()
  print('Throughputs Comparation done')
  print('Throughputs MME Comparation...')
  for i in range (0,4):
    plt.plot(timeTotals[i],MMEsTotals[i],color='r',ls='--',lw=2)
    plt.plot(timeTotals[i+4],MMEsTotals[i+4],color='g',ls='-.',lw=2)
    plt.plot(timeTotals[i+8],MMEsTotals[i+8],color='b',ls=':',lw=2)
    plt.xlabel('Seconds')
    plt.ylabel('Throughput (Mb/s)')
    red_line = mlines.Line2D([], [], color='Red',markersize=15, label='Fog4Video')
    green_line = mlines.Line2D([], [], color='g',markersize=15, label='Greedy')
    blue_line = mlines.Line2D([], [], color='b',markersize=15, label='Random')
    plt.legend(handles=[red_line,green_line,blue_line])
    name='EMA of Tier-2 EP-{pol}'.format(pol=(i+1))
    if i==3:
      name='EMA of Tier-1'
    if i==0:
      save= 'EMA of Tier-3'
    plt.grid(True,alpha=0.4,linestyle='--')
    plt.title(name)
    plt.savefig(name,bbox_inches="tight",dpi=300)
    plt.close()
  print('Throughputs MME Comparation done')
  print('Bitrate Comparation...')
  for i in range (0,4):
    x=np.arange(0,numSegments)
    fig,ax =plt.subplots()
    p1,=plt.plot(x,qualityLevelTotals[i],color='r',ls='--',lw=3, label='Fog4Video')
    p2,=plt.plot(x,qualityLevelTotals[i+4],color='g',ls='-.',lw=3, label='Greedy')
    p3,=plt.plot(x,qualityLevelTotals[i+8],color='b',ls=':',lw=3, label='Random')
    plt.xlabel('Chunks')
    plt.ylabel('Video bitrate(Kbps)')
    red_line = mlines.Line2D([], [], color='r',markersize=15, label='Tier-3')
    green_line = mlines.Line2D([], [], color='g',markersize=15, label='Tier-2 EP-2')
    blue_line = mlines.Line2D([], [], color='b',markersize=15, label='Tier-2 EP-1')
    yellow_line = mlines.Line2D([], [], color='y',markersize=15, label='Tier-1')
    plt.yticks( [0,400,650,1000,1500,2250,3400,4700,6000], ('0','400', '650', '1000', '1500', '2250','3400','4700','6000') )
    l1=plt.legend(handles=[p1,p2,p3],bbox_to_anchor=(1.04,1), loc="upper left",fancybox=True, shadow=True)
    save = 'Tier-2 EP-{pol}'.format(pol=(i+1))
    if i==3:
      save = 'Tier-1'
    if i==0:
      save= 'Tier-3'
    plt.title(save)
    #plt.legend(title='Enforcement Point',handles=[red_line,green_line,blue_line,yellow_line],bbox_to_anchor=(1.04,0.5), loc="center left",fancybox=True, shadow=True)
    plt.grid(True,alpha=0.4,linestyle='--')
    ax.add_artist(l1)
    plt.savefig(save,bbox_inches="tight",dpi=300)
    plt.close()
  print('Bitrate Comparation done')
  print('Stalls Comparation...')
  ind = np.arange(4)
  width = 0.2
  fig, ax = plt.subplots()
  rects1 = ax.bar(ind - width, StallsTotals[0], width,color=colors[0],label='Fog4Video')
  rects2 = ax.bar(ind, StallsTotals[1], width,color=colors[2],label='Greedy')
  rects3 = ax.bar(ind + width, StallsTotals[2], width,color=colors[4],label='Random')
  ax.set_ylabel('Number of Stall Events')
  ax.set_xticks(ind)
  ax.set_xticklabels(('Tier-3', 'Tier-2 EP-2', 'Tier-2 EP-1', 'Tier-1'))
  ax.legend()
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
           ncol=3, mode="expand", borderaxespad=0.,fontsize='medium',fancybox=True, shadow=True)
  plt.grid(True,axis='y',alpha=0.4,linestyle='--')
  save = 'StallsTotals.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  print('Stalls Comparation done')
  print('Rebuffers Comparation...')
  ind = np.arange(4)
  width = 0.2  
  fig, ax = plt.subplots()
  rects1 = ax.bar(ind - width, RebuffersTotals[0], width,color=colors[0],label='Fog4Video')
  rects2 = ax.bar(ind, RebuffersTotals[1], width,color=colors[2],label='Greedy')
  rects3 = ax.bar(ind + width, RebuffersTotals[2], width,color=colors[4],label='Random')
  ax.set_ylabel('Stall Duration (Seconds)')
  ax.set_xticks(ind)
  ax.set_xticklabels(('Tier-3', 'Tier-2 EP-2', 'Tier-2 EP-1', 'Tier-1'))
  ax.legend()
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
           ncol=3, mode="expand", borderaxespad=0.,fontsize='medium',fancybox=True, shadow=True)
  plt.grid(True,axis='y',alpha=0.4,linestyle='--')
  save = 'RebuffersTotals.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  print('Rebuffers Comparation done')
  print('Clients Comparation...')
  ind = np.arange(4)
  width = 0.2
  fig, ax = plt.subplots()
  rects1 = ax.bar(ind - width, MeansTotals[0], width,label='Fog4Video')
  rects2 = ax.bar(ind, MeansTotals[1], width,label='Greedy')
  rects3 = ax.bar(ind + width, MeansTotals[2], width,label='Random')
  ax.set_ylabel('Bitrate Average (Kbps)')
  ax.set_xticks(ind)
  ax.set_xticklabels(('Tier-3', 'Tier-2 EP-2', 'Tier-2 EP-1', 'Tier-1'))
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
           ncol=3, mode="expand", borderaxespad=0.,fontsize='medium',fancybox=True, shadow=True)
  ax.legend()
  plt.grid(True,axis='y',alpha=0.4,linestyle='--')
  save = 'BitrateTotals.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  ind = np.arange(2)
  width = 0.2
  fig, ax = plt.subplots()
  rects1 = ax.bar(ind - width, MeansBW[0], width,label='Fog4Video')
  rects2 = ax.bar(ind, MeansBW[1], width,label='Greedy')
  rects3 = ax.bar(ind + width, MeansBW[2], width,label='Random')
  ax.set_ylabel('Bitrate Average (Kbps)')
  ax.set_xticks(ind)
  ax.set_xticklabels(('Best Client', 'Worst Client'))
  ax.legend()
  plt.yticks( [0,400,650,1000,1500,2250,3400,4700,6000], ('0','400', '650', '1000', '1500', '2250','3400','4700','6000') )
  plt.grid(True,axis='y',alpha=0.4,linestyle='--')
  save = 'BestWorstTotals.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  print('Clients Comparation done.')
  
  print('Stalls per Clients Comparation')
  ind = np.arange(0.0,1.5,0.5)
  width = 0.2
  fig, ax = plt.subplots()
  aux=[np.sum(StallsTotals[0])/40,np.sum(StallsTotals[1])/40,np.sum(StallsTotals[2])/40]
  print(aux)
  confInt=[1.96*(np.std(StallsTotals[0])/np.sqrt(runs)/40),1.96*(np.std(StallsTotals[1])/np.sqrt(runs)/40),1.96*(np.std(StallsTotals[2])/np.sqrt(runs))/40]
  print(confInt)
  for i in range (0,len(aux)):
    rects1 = ax.bar(ind[i], aux[i],width,yerr=confInt[i],label=labels[i],color=colors[2*i])
  #rects1 = ax.bar(ind, aux,width,yerr=confInt,color=(('dimgray'),('darkgray'),('lightgrey')))
  #rects1 = ax.bar(ind, np.sum(StallsTotals[0]),width,yerr=(1.96*(np.std(StallsTotals[0])/np.sqrt(runs))),label='Fog4Video')
  #rects2 = ax.bar(ind, np.sum(StallsTotals[1]), width,yerr=(1.96*(np.std(StallsTotals[1])/np.sqrt(runs))),label='Greedy')
  #rects3 = ax.bar(ind, np.sum(StallsTotals[2]),width,yerr=(1.96*(np.std(StallsTotals[2])/np.sqrt(runs))),label='Random')
  ax.set_ylabel('Number of Stall Events')
  ax.set_xticks(ind)
  ax.set_xticklabels(('Fog4Video', 'Greedy', 'Random'))
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
           ncol=3, mode="expand", borderaxespad=0.,fontsize='medium',fancybox=True, shadow=True)
  #ax.legend()
  plt.grid(True,axis='y',alpha=0.4,linestyle='--')
  save = 'StallsTotal.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  print('Stalls per Clients Done')

  print('Fairness Comparation')
  ind = np.arange(0.0,1.5,0.5)
  width = 0.2
  fig, ax = plt.subplots()
  #aux=[np.sum(fairness[0])/40,np.sum(fairness[1])/40,np.sum(fairness[2])/40]
  #print(aux)
  #confInt=[1.96*(np.std(StallsTotals[0])/np.sqrt(runs)/40),1.96*(np.std(StallsTotals[1])/np.sqrt(runs)/40),1.96*(np.std(StallsTotals[2])/np.sqrt(runs))/40]
  #print(confInt)
  for i in range (0,len(fairness)):
    rects1 = ax.bar(ind[i], fairness[i],width,label=labels[i],color=colors[2*i])
  #rects1 = ax.bar(ind, aux,width,yerr=confInt,color=(('dimgray'),('darkgray'),('lightgrey')))
  #rects1 = ax.bar(ind, np.sum(StallsTotals[0]),width,yerr=(1.96*(np.std(StallsTotals[0])/np.sqrt(runs))),label='Fog4Video')
  #rects2 = ax.bar(ind, np.sum(StallsTotals[1]), width,yerr=(1.96*(np.std(StallsTotals[1])/np.sqrt(runs))),label='Greedy')
  #rects3 = ax.bar(ind, np.sum(StallsTotals[2]),width,yerr=(1.96*(np.std(StallsTotals[2])/np.sqrt(runs))),label='Random')
  ax.set_ylabel('Fairness Index')
  ax.set_xticks(ind)
  ax.set_xticklabels(('Fog4Video', 'Greedy', 'Random'))
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
           ncol=3, mode="expand", borderaxespad=0.,fontsize='medium',fancybox=True, shadow=True)
  #ax.legend()
  plt.grid(True,axis='y',alpha=0.4,linestyle='--')
  save = 'Fairness.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  print('Fairness Done')

  print('Rebuffers per Clients Comparation')
  ind = np.arange(0.0,1.5,0.5)
  width = 0.2  
  fig, ax = plt.subplots()
  aux=[np.sum(RebuffersTotals[0])/40,np.sum(RebuffersTotals[1])/40,np.sum(RebuffersTotals[2])/40]
  print(aux)
  confInt=[1.96*(np.std(RebuffersTotals[0])/np.sqrt(40)/40),1.96*(np.std(RebuffersTotals[1])/np.sqrt(40)/40),1.96*(np.std(RebuffersTotals[2])/np.sqrt(40))/40]
  print(confInt)
  for i in range (0,len(aux)):
    rects1 = ax.bar(ind[i], aux[i],width,yerr=confInt[i],label=labels[i],color=colors[2*i])
  #rects1 = ax.bar(ind, aux,width,yerr=confInt,color=(('dimgray'),('darkgray'),('lightgrey')))
  #rects1 = ax.bar(ind - width, np.sum(RebuffersTotals[0]),width,yerr=(1.96*(np.std(RebuffersTotals[0])/np.sqrt(runs))),label='Fog4Video')
  #rects2 = ax.bar(ind, np.sum(RebuffersTotals[1]), width,yerr=(1.96*(np.std(RebuffersTotals[1])/np.sqrt(runs))),label='Greedy')
  #rects3 = ax.bar(ind + width, np.sum(RebuffersTotals[2]),width,yerr=(1.96*(np.std(RebuffersTotals[2])/np.sqrt(runs))),label='Random')
  ax.set_ylabel('Stall Duration (Seconds)')
  ax.set_xticks(ind)
  ax.set_xticklabels(('Fog4Video', 'Greedy', 'Random'))
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
           ncol=3, mode="expand", borderaxespad=0.,fontsize='medium',fancybox=True, shadow=True)
  #ax.legend()
  plt.grid(True,axis='y',alpha=0.4,linestyle='--')
  save = 'RebuffersTotal.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  print('Rebuffers per Clients Done')

  print('Bitrate Switch Comparation')
  ind = np.arange(3)
  width = 0.2  
  fig, ax = plt.subplots()
  #aux=[np.sum(RebuffersTotals[0])/40,np.sum(RebuffersTotals[1])/40,np.sum(RebuffersTotals[2])/40]
  #confInt=[1.96*(np.std(RebuffersTotals[0])/np.sqrt(33)/40),1.96*(np.std(RebuffersTotals[1])/np.sqrt(33)/40),1.96*(np.std(RebuffersTotals[2])/np.sqrt(33))/40]
  #rects1 = ax.bar(ind, aux,width,yerr=confInt,color=(('tab:blue'),('tab:orange'),('tab:green')))
  rects1 = ax.bar(ind - width, [bitSwitchDowntotals[0],bitSwitchUptotals[0],bitSwitchtotals[0]],width,yerr=[bitSwitchDowntotalsConfInt[0],bitSwitchUptotalsConfInt[0],bitSwitchtotalsConfInt[0]],label='Fog4Video')
  rects2 = ax.bar(ind, [bitSwitchDowntotals[1],bitSwitchUptotals[1],bitSwitchtotals[1]], width,yerr=[bitSwitchDowntotalsConfInt[1],bitSwitchUptotalsConfInt[1],bitSwitchtotalsConfInt[1]],label='Greedy')
  rects3 = ax.bar(ind + width, [bitSwitchDowntotals[2],bitSwitchUptotals[2],bitSwitchtotals[2]],width,yerr=[bitSwitchDowntotalsConfInt[2],bitSwitchUptotalsConfInt[2],bitSwitchtotalsConfInt[2]],label='Random')
  ax.set_ylabel('Bitrate Switch')
  ax.set_xticks(ind)
  ax.set_xticklabels(('Downgrade', 'Upgrade', 'Total'))
  ax.legend()
  plt.grid(True,axis='y',alpha=0.4,linestyle='--')
  save = 'BitrateSwitchs.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  print('Bitrate Switch Done')

  print('Cost Comparation')
  #print(ClientsTotals)
  cost=[]
  for i in range (0,3):
    costSum=[]
    for j in range (0,4):
      aux=[]
      for k in range (0,len(ClientsTotals[i][j])):
        if j==0:
          aux.append(ClientsTotals[i][j][k]*0.42408)
        elif j==3:
          aux.append(ClientsTotals[i][j][k]*0.07272)
        else:
          aux.append(ClientsTotals[i][j][k]*0.22896)
      costSum.append(aux)
    cost.append(np.sum(costSum,0))
  for i in range (0, len(cost)):
    cost[i][-1]=cost[i][-2]
    cost[i]=np.delete(cost[i],0)
  x=np.arange(1,numSegments)
  fig,ax =plt.subplots()
  ind = np.arange(0.0,1.5,0.5)
  width = 0.2
  aux=[np.mean(cost[0])/6,np.mean(cost[1])/6,np.mean(cost[2])/6]
  confInt=[(1.96*(np.std((cost[0]))/np.sqrt(runs)))/6,(1.96*(np.std((cost[1]))/np.sqrt(runs)))/6,(1.96*(np.std((cost[2]))/np.sqrt(runs)))/6]
  #p1,=plt.plot(x,cost[0],color='b',ls='--',lw=1, label='Fog4Video')
  #p2,=plt.plot(x,cost[1],color='orange',ls='-.',lw=1, label='Greedy')
  #p3,=plt.plot(x,cost[2],color='green',ls=':',lw=1, label='Random')
  for i in range (0,len(aux)):
    rects1 = ax.bar(ind[i], aux[i],width,yerr=confInt[i],label=labels[i],color=colors[2*i])
  #rects1 = ax.bar(ind, ,width,yerr=,color=(('dimgray'),('darkgray'),('lightgrey')))#color=(('tab:blue'),('tab:orange'),('tab:green')))
  ax.set_xticks(ind)
  ax.set_xticklabels(('Fog4Video', 'Greedy', 'Random'))
  #plt.xlabel('Chunks')
  plt.ylabel('Monetary Cost per hour (U$)')
  print(np.mean(cost[0]),np.mean(cost[1]),np.mean(cost[2]))
  print((1.96*(np.std((cost[0]))/np.sqrt(runs))),(1.96*(np.std((cost[1]))/np.sqrt(runs))),(1.96*(np.std((cost[2]))/np.sqrt(runs))))
  #plt.xlim((1,300))
  #plt.legend(fancybox=True, shadow=True)
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
           ncol=3, mode="expand", borderaxespad=0.,fontsize='medium',fancybox=True, shadow=True)
  plt.grid(True,alpha=0.4,axis='y',linestyle='--')
  plt.savefig('Cost.pdf',bbox_inches="tight",dpi=300)
  plt.close()
  print('Cost Comparation Done')

  print('Bitrate Comparation')
  bitrateMean=[]
  confInts=[]
  '''for i in range (0,3):
    #aux=np.sum(qualityLevelTotals[4*i:((4*i)+3)],0)
    aux=QualityMeanTotal[i]
    aux[-1]=aux[-2]
    print(aux)
    bitrateMean.append([np.mean(aux[0:20]),np.mean(aux),np.mean(aux[-21:-1])])'''
  for i in range (0,3):
    os.chdir(str(i))
    files= '*playbackLog*'
    throughputFiles = glob.glob(files)
    throughputFiles.sort()
    begin=[]
    mean=[]
    final=[]
    for j in range (0,len(throughputFiles)):
      name = throughputFiles[j]
      df = pd.read_csv(name, sep=';',index_col=False)
      bitrate = df['Quality_Level']
      bitrate = toBitrate(bitrate)
      begin.append(np.mean(bitrate[0:20]))
      mean.append(bitrate.mean(axis=0))
      final.append(np.mean(bitrate[-21:-1]))
    bitrateMean.append([np.mean(begin),np.mean(mean),np.mean(final)])
    confInts.append([(1.96*(np.std(begin)/np.sqrt(60))),(1.96*(np.std(mean)/np.sqrt(60))),(1.96*(np.std(final)/np.sqrt(60)))])
    os.chdir('..')
  ind = np.arange(3)
  width = 0.2
  fig, ax = plt.subplots()
  rects1 = ax.bar(ind - width, bitrateMean[0], width,yerr=confInts[0],color=colors[0],label='Fog4Video')
  rects2 = ax.bar(ind, bitrateMean[1], width,yerr=confInts[1],color=colors[2],label='Greedy')
  rects3 = ax.bar(ind + width, bitrateMean[2], width,yerr=confInts[2],color=colors[4],label='Random')
  print(bitrateMean[0])
  print(bitrateMean[1])
  print(bitrateMean[2])
  print(confInts[0])
  print(confInts[1])
  print(confInts[2])
  ax.set_ylabel('Bitrate (Kbps)')
  ax.set_xticks(ind)
  ax.set_xticklabels(('Initial Bitrate', 'Bitrate Average', 'Final Bitrate'))
  ax.legend(loc='upper left')
  plt.grid(True,axis='y',alpha=0.4,linestyle='--')
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
           ncol=3, mode="expand", borderaxespad=0.,fontsize='medium',fancybox=True, shadow=True)
  #plt.yticks( [0,400,650,1000,1500,2250,3400,4700,6000], ('0','400', '650', '1000', '1500', '2250','3400','4700','6000') )
  save = 'BitrateMean.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  print('Bitrate Comparation Done')

  print('Bitrate Comparation Boxplot')
  bitrates=[[],[],[]]
  for i in range (0,3):
    os.chdir(str(i))
    files= '*playbackLog*'
    throughputFiles = glob.glob(files)
    throughputFiles.sort()
    for j in range (0,len(throughputFiles)):
      name = throughputFiles[j]
      df = pd.read_csv(name, sep=';',index_col=False)
      bitrate = df['Quality_Level']
      bitrates[i].append(bitrate.mean(axis=0))
    bitrates[i]=toBitrate(bitrates[i])
    os.chdir('..')
  fig, ax = plt.subplots()
  pos = np.array(range(len(bitrates))) + 1
  #medians = [np.mean(bitrates[0]), np.mean(bitrates[1]),np.mean(bitrates[2])]
  #conf_intervals=[(1.96*(np.std(bitrates[0])/np.sqrt(33))),(1.96*(np.std(bitrates[1])/np.sqrt(33))),(1.96*(np.std(bitrates[2])/np.sqrt(33)))]
  #conf_intervals = [(medians[0]+conf_intervals[0],medians[0]-conf_intervals[0]),(medians[1]+conf_intervals[1],medians[1]-conf_intervals[1]),(medians[2]+conf_intervals[2],medians[2]-conf_intervals[2])]
  #print(conf_intervals)
  #print(medians)
  #bp = ax.boxplot(bitrates, positions=pos,notch=1,conf_intervals=conf_intervals,usermedians=medians) #bootstrap=5000,usermedians=medians,conf_intervals=conf_intervals
  bp = ax.boxplot(bitrates, positions=pos,notch=1,bootstrap=1000,showmeans=True,meanline=True)
  ax.set_xlabel('Mechanism')
  ax.set_ylabel('Bitrate (Kbps)')
  ax.set_xticklabels(('Fog4Video', 'Greedy', 'Random'))
  plt.setp(bp['whiskers'], color='k', linestyle='-')
  plt.setp(bp['fliers'], markersize=3.0)
  plt.grid(True,axis='y',alpha=0.4,linestyle='--')
  save = 'Boxplot.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  print('Bitrate Comparation Boxplot Done')

  time=0
  cl=0
  time2=0
  cl2=0
  os.chdir(str(0))
  files= '*bufferUnderrunLog*'
  throughputFiles = glob.glob(files)
  throughputFiles.sort()
  for j in range (0,len(throughputFiles)):
    name = throughputFiles[j]
    df = pd.read_csv(name, sep=';',index_col=False)
    bitrate = np.array(df['Buffer_Underrun_Duration'])
    if len(bitrate)==1:
      time+=bitrate
      cl+=1
    if len(bitrate)>1:
      time2+=np.sum(bitrate)
      cl2+=1
  print(time,cl)
  print(time2,cl2)
  os.chdir('..')
  '''
  bitrateMean=[]
  for i in range (0,3):
    aux=QualityMeanTotal[i]
    aux[-1]=aux[-2]
    print(aux)
    bitrateMean.append([np.mean(aux[0:20]),np.mean(aux),np.mean(aux[-21:-1])])
  ind = np.arange(3)
  width = 0.2
  fig, ax = plt.subplots()
  rects1 = ax.bar(ind - width, bitrateMean[0], width,label='Fog4Video')
  rects2 = ax.bar(ind, bitrateMean[1], width,label='Greedy')
  rects3 = ax.bar(ind + width, bitrateMean[2], width,label='Random')
  ax.set_ylabel('Bitrate Average (Kbps)')
  ax.set_xticks(ind)
  ax.set_xticklabels(('Initial Bitrate', 'Bitrate Average', 'Final Bitrate'))
  ax.legend()
  plt.grid(True,axis='y',alpha=0.4,linestyle='--')
  save = 'BitrateMean.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  print('Bitrate Comparation Boxplot Done')'''

  print('Graphs Comparation done.')

def toBitrate(vet):
  for i in range(0,len(vet)):
    if vet[i]==-1:
      vet[i]=0
    elif vet[i]<=1:
      vet[i]=250*vet[i]+400
    elif vet[i]<=2:
      vet[i]=350*(vet[i]-1)+650
    elif vet[i]<=3:
      vet[i]=500*(vet[i]-2)+1000
    elif vet[i]<=4:
      vet[i]=750*(vet[i]-3)+1500
    elif vet[i]<=5:
      vet[i]=1150*(vet[i]-4)+2250
    else:
      vet[i]=1300*(vet[i]-5)+3400
  return vet

if __name__=="__main__":
    main()
