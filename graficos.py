import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import os
import glob
import operator
import argparse
import pandas as pd
plt.style.use('seaborn-dark-palette')

parser = argparse.ArgumentParser(description='Script to make graphs for dash migration simulation')
#parser.add_argument('--segmentfile','-seg',default="segmentSizesBigBuck.txt", type=str,help='Name of segmentfile used.Default is segmentSizesBigBuck1A.txt')
parser.add_argument('--adaptAlgo','-Adpt',default="festive", type=str,help='Name of adaptation algorithm used.Default is festive, possible values are: festive, panda, tobasco')
parser.add_argument('--Clients','-c', type=str,help='Number of Clients in the simulation')
#parser.add_argument('--Politica','-p', type=int,help='Politica used in the simulation')
parser.add_argument('--runs','-r', type=int,default=1,help='Number of simulations to make the graphs. Default is 1')
args = parser.parse_args()
if args.adaptAlgo!="festive" and args.adaptAlgo!="panda" and args.adaptAlgo!="tobasco":
    parser.error("Wrong adaptation algorithm")
if args.runs <= 0 :
    parser.error("Invalid number of runs")

runs=args.runs
#segmentfile=args.segmentfile
adaptAlgo=args.adaptAlgo
numberOfClients=args.Clients.split(',')
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
comp=['PLI','Fog4VR','Greedy','Random']
fair=[]
Cost=[]
costConf=[]
playback=[]
migrationConf=[]
migration=[]
buffering=[]
bufferingConf=[]
numberTotal=[]
numberTotalConf=[]
Stalls=[]
StallsConf=[]
Rebuffer=[]
RebufferConf=[]
patterns = [ "/","x", "|" , "-" , "+", "\\" , "o", "O", ".", "*" ]
#colors=['dimgray', 'gray', 'darkgray','silver','lightgrey']
colors=['black','red','blue', 'blueviolet','green','lightsteelblue','limegreen']
markers=['o','s','P','v','*','X','D']

def main():
  print('Beginning')
  numSegments=900
  #os.chdir('..')

  folder='dash-log-files/{algo}/'.format(algo=adaptAlgo)
  os.chdir(folder)
  for k in numberOfClients:
    startTime=[]
    startTimeConf=[]
    totalCost=[]
    totalCostConf=[]
    totalUsage=[]
    StRd=[]
    StRdConf=[]
    fogNumber=[]
    fogNumberConf=[]
    Clients=k
    folder='{num}'.format(num=Clients)
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
      vec, conf=playbackStart()
      startTime.append(vec)
      startTimeConf.append(conf)
      srd,srdConf=StallsRebuffers(k)
      StRd.append(srd)
      StRdConf.append(srdConf)
      resp,conf2,num,numConf=fogStatus()
      totalCost.append(np.sum(resp[0]))
      totalCostConf.append(conf2)
      totalUsage.append(resp[1])
      fogNumber.append(num)
      fogNumberConf.append(numConf)
      os.chdir('..')
    #graphtotals(numSegments)
    barGraph(totalCost ,name='cost.png', ylabel='Total Monetary Cost (USD)',xticks=['MSFog','Guloso','Aleatório'])
    stackedBarGraph(startTime,'start.png',ylabel='playback Start Time (s)',xticks=['MSFog','Guloso','Aleatório'],labels=['Tempo de Migração', 'Tempo de bufferização'])
    barGraph(totalUsage, name='usage.png',xlabel='time(s)')
    barGraph(StRd, name='Stalls.png',xlabel='Stalls')
    playback.append(startTime)
    migrationConf.append([item[0] for item in startTimeConf])
    bufferingConf.append([item[1] for item in startTimeConf])
    migration.append([item[0] for item in startTime])
    buffering.append([item[1] for item in startTime])
    StallsConf.append([item[0] for item in StRdConf])
    RebufferConf.append([item[1] for item in StRdConf])
    Stalls.append([item[0] for item in StRd])
    Rebuffer.append([item[1] for item in StRd])
    Cost.append(totalCost)
    costConf.append(totalCostConf)
    fair.append(totalUsage)
    #fogNumber.pop()
    #fogNumberConf.pop()
    numberTotal.append(fogNumber)
    numberTotalConf.append(fogNumberConf)
    os.chdir('..')
    #print(os.getcwd())
    #print(os.listdir())
  print('custo',costConf)
  barGraph(Cost,costConf,name='cost.pdf',xlabel='Number of Microservices',ylabel='Cost per hour(USD)',xticks=numberOfClients,labels=comp)
  print(playback)
  barGraph(migration,migrationConf,'migration.pdf','Number of Microservices','Migration Time (s)',xticks=numberOfClients,labels=comp)
  barGraph(buffering,bufferingConf,'buffering.pdf','Number of Microservices','buffering Time (s)',xticks=numberOfClients,labels=comp)
  barGraph(Stalls,StallsConf,'Stalls.pdf','Number of Microservices','Number of Stalls',xticks=numberOfClients,labels=comp)
  barGraph(Rebuffer,RebufferConf,'Rebuffers.pdf','Number of Microservices','Rebuffer time (s)',xticks=numberOfClients,labels=comp)
  stackedBarGraph(playback,'start.pdf','Number of Microservices','Playback Start Time (s)',xticks=numberOfClients,labels=['PLI','Fog4VR','Greedy','Random','Cloud','Migration Time', 'buffering Time'])
  plotGraph(fair, 'usage.pdf','Number of Microservices','Load Distribution (Jain Fairness)',xticks=numberOfClients,labels=comp)
  barGraph(numberTotal,numberTotalConf,'number.pdf','Number of Microservices','Microservices on fogs',xticks=numberOfClients,labels=comp)#,'Nuvem'])
  print(fair)
  print(numberTotal)
  print('Finished')

def playbackStart():
  i=0
  migrationTimeMean=[]
  bufferingTimeMean=[]
  while i<runs:
    j=0
    simulation=i
    files= '*sim{simu}_*downloadLog*'.format(simu=simulation)
    files=glob.glob(files)
    migrationTime=[]
    bufferingTime=[]
    while j<len(files):
      name=files[j]
      file = open(name,"r")
      next(file)
      line=file.readline()
      fields=line.split(";")
      if (len(fields)>=2):
        end=float(fields[3])
        mid=float(fields[2])
        begin=float(fields[1])
        migrationTime.append(mid-begin)
        bufferingTime.append(end-mid)
      j+=1
    migrationTimeMean.append(np.mean(migrationTime))
    bufferingTimeMean.append(np.mean(bufferingTime))
    i+=1
  vec=[]
  conf=[]
  vec.append(np.mean(migrationTimeMean))
  conf.append(np.std(migrationTimeMean))
  vec.append(np.mean(bufferingTimeMean))
  conf.append(np.std(bufferingTimeMean))
  stackedBarGraph(vec,'play.pdf')
  return vec,conf

def StallsRebuffers(num):
  i=0
  StMean=[]
  RdMean=[]
  while i<runs:
    j=0
    simulation=i
    files= '*sim{simu}_*bufferUnderrunLog*'.format(simu=simulation)
    files=glob.glob(files)
    St=[]
    Rd=[]
    while j<len(files):
      name=files[j]
      file=pd.read_csv(name, sep=';',index_col=False)
      duration=np.array(file['Buffer_Underrun_Duration'])
      St.append(len(duration))
      Rd.append(np.sum(duration))  
      j+=1
    StMean.append(np.mean(St)/int(num))
    RdMean.append(np.nanmean(Rd)/int(num))
    i+=1
  vec=[]
  Conf=[]
  print(np.mean(StMean))
  print(np.mean(RdMean))
  vec.append(np.mean(StMean))
  Conf.append(np.std(StMean))
  vec.append(np.mean(RdMean))
  Conf.append(np.std(RdMean))
  #stackedBarGraph(vec,'strd.pdf')
  return vec,Conf

def fogStatus():
  i=0
  priceMean=[]
  usageMean=[]
  numberSum=[]
  while i<runs:
    j=0
    simulation=i
    files= '*throughputServer*sim{simu}_*'.format(simu=simulation)
    files=glob.glob(files)
    files.sort()
    price=[]
    usage=[]
    number=[]
    while j<len(files):
      use=[]
      name=files[j]
      file=pd.read_csv(name, sep=';',index_col=False)
      onOff=np.array(file['OnOff'])
      cost=np.array(file['Cost'])
      content=np.array(file['AllocatedContent']).astype(str)
      cost=onOff*cost
      #if (j<=1 or j==5 or j==9):
      #  onOff=onOff*0.000085
      #elif ((j<=8 and j>=6) or j==2 or j==4):
      #  onOff=onOff*0.00017
      #else:
      #  onOff=onOff*0.00034
      if(name!='throughputServer_sim{simu}_2.0.14.1_Log.csv'.format(simu=simulation)):
        val=content[60].split("/")
        #val=list(set(val))
        val = [x for x in val if str(x) != 'nan']
        number.append(len(val))
      price.append(np.sum(cost))
      freeMemory=np.array(file['FreeMemory'])
      totalMemory=np.array(file['TotalMemory'])
      per=np.divide(totalMemory,freeMemory)
      per=1-per
      #per=per*100
      usage.append(np.mean(per))
      #for i in range (0,len(freeMemory)):
      #  per=freeMemory[i]/totalMemory[i]
      #  diff= 1-per
      #  use.append(diff*100)
      #content=np.array(file['AllocatedContent'])
      #address=np.array(file['ServerAddress'])
      #ip=address[0]
      j+=1
    fair= pow(np.sum(usage),2)/(len(usage)*(np.sum(np.power(usage,2))))
    usageMean.append(fair)
    priceMean.append(30*np.sum(price))
    numberSum.append(np.sum(number))
    i+=1
  vec=[]
  conf=[]
  num=[]
  numConf=[]
  num.append(np.nanmean(numberSum))
  numConf.append(np.std(numberSum))
  vec.append(np.mean(priceMean))
  conf.append(np.std(priceMean))
  #barGraph(vec,'cost.pdf')
  vec.append(np.mean(usageMean))
  #barGraph([vec[1]],'usage.pdf')
  return vec,conf,num,numConf


def barGraph(vec,conf=[],name='',xlabel='',ylabel='',xticks=[],title='',labels=[]):
  vec=np.asarray(vec)
  conf=np.asarray(conf)
  shapes=vec.shape
  if conf.shape!=shapes:
    conf=np.zeros(shapes)
  else:
    conf=((1.96*conf)/np.sqrt(33))
  tam=shapes[0]

  if len(shapes)>1:
    tam2=shapes[1]
  else:
    tam2=0
  fig,ax =plt.subplots()
  ind = np.arange(0.0,tam/2,0.5).astype(float)
  if len(xticks)<1: 
    xticks=ind
  width = 0.1
  legend=[]
  #p1,=plt.plot(x,cost[0],color='b',ls='--',lw=1, label='Fog4Video')
  #p2,=plt.plot(x,cost[1],color='orange',ls='-.',lw=1, label='Greedy')
  #p3,=plt.plot(x,cost[2],color='green',ls=':',lw=1, label='Random')
  if tam2==0:
    for i in range (0, int(tam)):
      ax.bar(ind[i], vec[i], width,yerr=conf[i],color='grey',ecolor='black', hatch=patterns[i])
  else:
    for i in range (0, int(tam)):
      for j in range (0, int(tam2)):
        ax.bar(ind[i]+(j*width), vec[i][j], width,yerr=conf[i][j], color=colors[j],ecolor='black', hatch=patterns[j])
        if (i==0 and len(labels)==tam2):
            legend.append(mpatches.Patch(facecolor=colors[j],hatch=patterns[j],label=labels[j]))
  if tam2==0:
    ax.set_xticks(ind)
  else:
    ax.set_xticks(ind+((tam2-1)*width)/2)
  ax.set_xticklabels(xticks,fontsize=18)
  plt.xlabel(xlabel,fontsize=18)
  plt.ylabel(ylabel,fontsize=18)
  plt.xticks(fontsize=16)
  plt.yticks(fontsize=16)
  #plt.xlim((1,300))
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
           ncol=4, mode="expand", borderaxespad=0.,fontsize='medium',title=title,handles=legend,fancybox=True, shadow=True)
  plt.grid(True,alpha=0.4,axis='y',linestyle='--')
  plt.savefig(name,figsize=(4000,4000),bbox_inches="tight",dpi=300)
  plt.close()

def stackedBarGraph(vec,name,xlabel='',ylabel='',xticks=[],title='',labels=[]):
  patterns = [ "/","*","x", "|" , "-" , "+", "\\" , "o", "O", "."]
  vec=np.asarray(vec)
  shapes=vec.shape
  tam=shapes[0]/2
  legend=[]
  if len(shapes)==2:
    tam2=shapes[1]/2
    tam3=0
  elif len(shapes)==3:
    tam2=shapes[1]
    tam3=shapes[2]/2
  else:
    tam2=0
    tam3=0
  fig,ax =plt.subplots()
  ind = np.arange(0.0,tam,0.5).astype(float)
  if len(xticks)<1: 
    xticks=ind
  width = 0.1
  if tam2==0:
    for i in range (0, int(tam)):
      ax.bar(ind[i], vec[i], width, color='grey',ecolor='black', hatch=patterns[i])
      ax.bar(ind[i], vec[i+1], width,bottom = vec[i], color='grey',ecolor='black', hatch=patterns[i+1])
  elif tam2==shapes[1]/2:
    for i in range (0, int(tam*2)):
      for j in range(0,int(tam2)):
        ax.bar(ind[i], vec[i][j], width, color='grey',ecolor='black', hatch=patterns[j])
        ax.bar(ind[i], vec[i][j+1], width,bottom = vec[i][j], color='grey',ecolor='black', hatch=patterns[j+1])
    if len(labels)/2==tam2:
      for j in range(0,int(tam2*2)): 
        legend.append(mpatches.Patch(facecolor='grey',hatch=patterns[j], label=labels[j]))
  else:
    for i in range (0, int(tam*2)):
      for j in range(0,int(tam2)):
        for k in range(0, int(tam3)):
          ax.bar(ind[i]+(j*width), vec[i][j][k], width, color=colors[j],ecolor='black', hatch=patterns[k])
          ax.bar(ind[i]+(j*width), vec[i][j][k+1], width,bottom = vec[i][j][k], color=colors[j],ecolor='black', hatch=patterns[k+1])
          if (i==0):
            legend.append(mpatches.Patch(color=colors[j], label=labels[j]))
    if len(labels)>=tam2:
      for j in range(0,int(tam3*2)): 
        legend.append(mpatches.Patch(facecolor='grey',hatch=patterns[j], label=labels[tam2+j]))
  if tam3==0:
    ax.set_xticks(ind)
  else:
    ax.set_xticks(ind+((tam2-1)*width)/2)
  ax.set_xticklabels(xticks,fontsize=18)
  plt.xlabel(xlabel,fontsize=18)
  plt.ylabel(ylabel,fontsize=18)
  plt.xticks(fontsize=16)
  plt.yticks(fontsize=16)
  #plt.xlim((1,300))
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
           ncol=3, mode="expand", borderaxespad=0.,fontsize='medium',title=title,handles=legend,fancybox=True, shadow=True)
  plt.grid(True,alpha=0.4,axis='y',linestyle='--')
  plt.savefig(name,figsize=(4000,4000),bbox_inches="tight",dpi=300)
  plt.close()

def plotGraph(vec,name,xlabel='',ylabel='',xticks=[],title='',labels=[]):
  vec=np.asarray(vec)
  shapes=vec.shape
  tam=shapes[0]
  legend=[]
  if len(shapes)>1:
    tam2=shapes[1]
  else:
    tam2=0
  if tam2==0:
    for i in range(0,int(tam)):
      x = np.arange(0,len(vec[i]))
      plt.plot(x,vec[i],color='grey',marker=markers[i])
  else:
    for i in range(0,int(tam2)):
      for j in range (0, int(tam)):
        toplot = [item[i] for item in vec]
      x = np.arange(0,int(tam))
      plt.plot(x,toplot,color=colors[i],marker=markers[i])
      if len(labels)>=tam2:
        legend.append(mlines.Line2D([], [], color=colors[i],marker=markers[i], label=labels[i]))
  plt.xlabel(xlabel,fontsize=18)
  plt.ylabel(ylabel,fontsize=18)
  if len(xticks)>0:
    plt.xticks(x,xticks,fontsize=16)
  plt.yticks(fontsize=16)
  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
           ncol=4, mode="expand", borderaxespad=0.,fontsize='medium',title=title,handles=legend,fancybox=True, shadow=True)
  #red_line = mlines.Line2D([], [], color='Red',markersize=15, label='Tier-3')
  #green_line = mlines.Line2D([], [], color='g',markersize=15, label='Tier-2 EP-2')
  #blue_line = mlines.Line2D([], [], color='b',markersize=15, label='Tier-2 EP-1')
  #yellow_line = mlines.Line2D([], [], color='y',markersize=15, label='Tier-1')
  #plt.legend(title='Enforcement Point')#,handles=[red_line,green_line,blue_line,yellow_line])
  #plt.title("Server Throughput")
  #save = 'ServerThroughput.pdf'
  plt.grid(True,alpha=0.4,axis='y',linestyle='--')
  plt.savefig(name,figsize=(4000,4000),bbox_inches="tight",dpi=300)
  plt.close()    



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
      elif str(Server[i])=='2.0.0.1' :
        S2Throughput[i]=S2Throughput[i]+y1
        S2Clients[i]=S2Clients[i]+1
      elif str(Server[i])=='3.0.0.1' :
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
        bestScore=ClientScore
        bestClientQuality=qualityLevel
        bestClientServer=Server
      elif(ClientScore<worstScore):
        worstScore=ClientScore
        worstClientQuality=qualityLevel
        worstClientServer=Server

      i=0
      for x1, x2, y1,y2 in zip(segment, segment[1:], qualityLevel, qualityLevel[1:]):
        if str(Server[i])=="1.0.0.1":
          S1Quality[i]=S1Quality[i]+y1
          S1Clients[i]=S1Clients[i]+1
        elif str(Server[i])=='2.0.0.1' :
          S2Quality[i]=S2Quality[i]+y1
          S2Clients[i]=S2Clients[i]+1
        elif str(Server[i])=='3.0.0.1':
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
    QualityMean.append(np.sum([S1Quality,S2Quality,S3Quality,S4Quality],0)/40)
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
    bitSwitchMean.append(bitSwitch/40)
    bitSwitchUpMean.append(bitSwitchUp/40)
    bitSwitchDownMean.append(bitSwitchDown/40)
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

  red_line = mlines.Line2D([], [], color='r',markersize=15, label='Tier-3')
  green_line = mlines.Line2D([], [], color='g',markersize=15, label='Tier-2 EP-2')
  blue_line = mlines.Line2D([], [], color='b',markersize=15, label='Tier-2 EP-1')
  yellow_line = mlines.Line2D([], [], color='y',markersize=15,label='Tier-1')
  width = 0.6
  fig,ax =plt.subplots()
  new_x = [i for i in x]
  p1 = plt.bar(new_x, S1ClientsMean, width=3,color='r',align='edge')
  p2 = plt.bar(new_x, S2ClientsMean, width=3,bottom=S1ClientsMean,color='g',align='edge')
  p3 = plt.bar(new_x, S3ClientsMean, width=3,bottom=np.array(S1ClientsMean)+np.array(S2ClientsMean),color='b',align='edge')
  p4 = plt.bar(new_x, S4ClientsMean, width=3,bottom=np.array(S1ClientsMean)+np.array(S2ClientsMean)+np.array(S3ClientsMean),color='y',align='edge')
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
  plt.xlabel('Chunks',fontsize=16)
  plt.ylabel('Clients per Server Average', fontsize=16)
  plt.legend(handles=[red_line,green_line,blue_line,yellow_line],bbox_to_anchor=(0.5, 1.3),loc='upper center', fontsize=16,ncol=4,fancybox=True, shadow=True)
  save = 'clientsPerServer.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
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
    plt.xlabel('Chunks',fontsize=18)
    plt.ylabel('Video bitrate(Kbps)',fontsize=18)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
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
  rects1 = ax.bar(ind - width, StallsTotals[0], width,label='Fog4Video')
  rects2 = ax.bar(ind, StallsTotals[1], width,label='Greedy')
  rects3 = ax.bar(ind + width, StallsTotals[2], width,label='Random')
  ax.set_ylabel('Number of Stall Events',fontsize=18)
  ax.set_xticks(ind)
  ax.set_xticklabels(('Tier-3', 'Tier-2 EP-2', 'Tier-2 EP-1', 'Tier-1'),fontsize=18)
  ax.legend()
  plt.xticks(fontsize=16)
  plt.yticks(fontsize=16)
  plt.grid(True,axis='y',alpha=0.4,linestyle='--')
  save = 'StallsTotals.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  print('Stalls Comparation done')
  print('Rebuffers Comparation...')
  ind = np.arange(4)
  width = 0.2  
  fig, ax = plt.subplots()
  rects1 = ax.bar(ind - width, RebuffersTotals[0], width,label='Fog4Video')
  rects2 = ax.bar(ind, RebuffersTotals[1], width,label='Greedy')
  rects3 = ax.bar(ind + width, RebuffersTotals[2], width,label='Random')
  ax.set_ylabel('Stall Duration (Seconds)',fontsize=18)
  ax.set_xticks(ind)
  ax.set_xticklabels(('Tier-3', 'Tier-2 EP-2', 'Tier-2 EP-1', 'Tier-1'),fontsize=18)
  ax.legend()
  plt.xticks(fontsize=16)
  plt.yticks(fontsize=16)
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
  ax.set_ylabel('Bitrate Average (Kbps)',fontsize=18)
  ax.set_xticks(ind)
  ax.set_xticklabels(('Tier-3', 'Tier-2 EP-2', 'Tier-2 EP-1', 'Tier-1'),fontsize=18)
  ax.legend()
  plt.xticks(fontsize=16)
  plt.yticks(fontsize=16)
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
  rects1 = ax.bar(ind, aux,width,yerr=confInt,color=(('tab:blue'),('tab:orange'),('tab:green')))
  #rects1 = ax.bar(ind, np.sum(StallsTotals[0]),width,yerr=(1.96*(np.std(StallsTotals[0])/np.sqrt(runs))),label='Fog4Video')
  #rects2 = ax.bar(ind, np.sum(StallsTotals[1]), width,yerr=(1.96*(np.std(StallsTotals[1])/np.sqrt(runs))),label='Greedy')
  #rects3 = ax.bar(ind, np.sum(StallsTotals[2]),width,yerr=(1.96*(np.std(StallsTotals[2])/np.sqrt(runs))),label='Random')
  ax.set_ylabel('Number of Stall Events',fontsize=18)
  ax.set_xticks(ind)
  ax.set_xticklabels(('Fog4Video', 'Greedy', 'Random'),fontsize=18)
  plt.xticks(fontsize=16)
  plt.yticks(fontsize=16)
  #ax.legend()
  plt.grid(True,axis='y',alpha=0.4,linestyle='--')
  save = 'StallsTotal.pdf'
  plt.savefig(save,bbox_inches="tight",dpi=300)
  plt.close()
  print('Stalls per Clients Done')

  print('Rebuffers per Clients Comparation')
  ind = np.arange(0.0,1.5,0.5)
  width = 0.2  
  fig, ax = plt.subplots()
  aux=[np.sum(RebuffersTotals[0])/40,np.sum(RebuffersTotals[1])/40,np.sum(RebuffersTotals[2])/40]
  print(aux)
  confInt=[1.96*(np.std(RebuffersTotals[0])/np.sqrt(runs)/40),1.96*(np.std(RebuffersTotals[1])/np.sqrt(runs)/40),1.96*(np.std(RebuffersTotals[2])/np.sqrt(runs))/40]
  print(confInt)
  rects1 = ax.bar(ind, aux,width,yerr=confInt,color=(('tab:blue'),('tab:orange'),('tab:green')))
  #rects1 = ax.bar(ind - width, np.sum(RebuffersTotals[0]),width,yerr=(1.96*(np.std(RebuffersTotals[0])/np.sqrt(runs))),label='Fog4Video')
  #rects2 = ax.bar(ind, np.sum(RebuffersTotals[1]), width,yerr=(1.96*(np.std(RebuffersTotals[1])/np.sqrt(runs))),label='Greedy')
  #rects3 = ax.bar(ind + width, np.sum(RebuffersTotals[2]),width,yerr=(1.96*(np.std(RebuffersTotals[2])/np.sqrt(runs))),label='Random')
  ax.set_ylabel('Stall Duration (Seconds)',fontsize=18)
  ax.set_xticks(ind)
  ax.set_xticklabels(('Fog4Video', 'Greedy', 'Random'),fontsize=18)
  plt.xticks(fontsize=16)
  plt.yticks(fontsize=16)
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
  #p1,=plt.plot(x,cost[0],color='b',ls='--',lw=1, label='Fog4Video')
  #p2,=plt.plot(x,cost[1],color='orange',ls='-.',lw=1, label='Greedy')
  #p3,=plt.plot(x,cost[2],color='green',ls=':',lw=1, label='Random')
  rects1 = ax.bar(ind, [np.mean(cost[0])/6,np.mean(cost[1])/6,np.mean(cost[2])/6],width,yerr=[(1.96*(np.std((cost[0]))/np.sqrt(runs)))/6,(1.96*(np.std((cost[1]))/np.sqrt(runs)))/6,(1.96*(np.std((cost[2]))/np.sqrt(runs)))/6],color=(('tab:blue'),('tab:orange'),('tab:green')))
  ax.set_xticks(ind)
  ax.set_xticklabels(('Fog4Video', 'Greedy', 'Random'),fontsize=18)
  plt.ylabel('Monetary Cost per hour (U$)',fontsize=18)
  plt.xticks(fontsize=16)
  plt.yticks(fontsize=16)
  print(np.mean(cost[0]),np.mean(cost[1]),np.mean(cost[2]))
  print((1.96*(np.std((cost[0]))/np.sqrt(runs))),(1.96*(np.std((cost[1]))/np.sqrt(runs))),(1.96*(np.std((cost[2]))/np.sqrt(runs))))
  #plt.xlim((1,300))
  #plt.legend(fancybox=True, shadow=True)
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
  rects1 = ax.bar(ind - width, bitrateMean[0], width,yerr=confInts[0],label='Fog4Video')
  rects2 = ax.bar(ind, bitrateMean[1], width,yerr=confInts[1],label='Greedy')
  rects3 = ax.bar(ind + width, bitrateMean[2], width,yerr=confInts[2],label='Random')
  print(bitrateMean[0])
  print(bitrateMean[1])
  print(bitrateMean[2])
  print(confInts[0])
  print(confInts[1])
  print(confInts[2])
  ax.set_ylabel('Bitrate (Kbps)',fontsize=18)
  ax.set_xticks(ind)
  ax.set_xticklabels(('Initial Bitrate', 'Bitrate Average', 'Final Bitrate'),fontsize=18)
  ax.legend(loc='upper left',fontsize=15)
  plt.xticks(fontsize=16)
  plt.yticks(fontsize=16)
  plt.grid(True,axis='y',alpha=0.4,linestyle='--')
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
  ax.set_xlabel('Mechanism',fontsize=18)
  ax.set_ylabel('Bitrate (Kbps)',fontsize=18)
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
