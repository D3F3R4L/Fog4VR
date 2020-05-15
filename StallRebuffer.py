import glob
import numpy as np
import sys
import os

folder=sys.argv[1]
simulation=sys.argv[2]
#pol=sys.argv[3]

def main():
  os.chdir(folder)
  #folder='dash-log-files/{algo}/{num}/{pol}'.format(algo=adaptAlgo,num=numberOfClients,pol=pol)
  resp=bufferUnderrunGraphs()
  print(resp[0],resp[1],resp[2],resp[3],resp[4],resp[5],resp[6],resp[7])

###################
# Buffer Underrun 
###################
def bufferUnderrunGraphs():
  files= '*sim{simu}_*bufferUnderrunLog*'.format(simu=simulation)
  bufferUnderrunFiles = glob.glob(files)
  #print(bufferUnderrunFiles)
  S1timeTotal=0
  S2timeTotal=0
  S3timeTotal=0
  CloudtimeTotal=0
  S1Nstalls=0
  S2Nstalls=0
  S3Nstalls=0
  CloudNstalls=0
  S1Clients=0
  S2Clients=0
  S3Clients=0
  CloudClients=0
  j=0
  while(j<len(bufferUnderrunFiles)):
    S1Client=True
    S2Client=True
    S3Client=True
    CloudClient=True
    name = bufferUnderrunFiles[j]
    with open(name) as f:
      data = f.readlines()
    for i in range(1,len(data)):
      fields = data[i].split(";")
      #print(fields)
      if len(fields)>=5:
        if str(fields[0])=="1.0.0.1":
          if S1Client:
            S1Clients+=1
            S1Client=False
          S1Nstalls+=1
          S1timeTotal+=float(fields[3])
        elif str(fields[0])=='2.0.0.1' or str(fields[0])=="1.0.0.3" :
          if S2Client:
            S2Clients+=1
            S2Client=False
          S2Nstalls+=1
          S2timeTotal+=float(fields[3])
        elif str(fields[0])=='3.0.0.1' or str(fields[0])=="1.0.0.5":
          if S3Client:
            S3Clients+=1
            S3Client=False
          S3Nstalls+=1
          S3timeTotal+=float(fields[3])
        else:
          if CloudClient:
            CloudClients+=1
            CloudClient=False
          CloudNstalls+=1
          CloudtimeTotal+=float(fields[3])
    f.close()
    j+=1
  #S1Nstalls=dividir(S1Nstalls,S1Clients)
  #S2Nstalls=dividir(S2Nstalls,S2Clients)
  #S3Nstalls=dividir(S3Nstalls,S3Clients)
  #CloudNstalls=dividir(CloudNstalls,CloudClients)
  #S1timeTotal=dividir(S1timeTotal,S1Clients)
  #S2timeTotal=dividir(S2timeTotal,S2Clients)
  #S3timeTotal=dividir(S3timeTotal,S3Clients)
  #CloudtimeTotal=dividir(CloudtimeTotal,CloudClients)
  return S1Nstalls,S1timeTotal,S2Nstalls,S2timeTotal,S3Nstalls,S3timeTotal,CloudNstalls,CloudtimeTotal

def dividir(a,b):
  if b==0:
    return 0
  else:
    return a/b

if __name__=="__main__":
    main()