
import numpy as np

import math

Limiares=[200,-1,2,2,1]

class guloso():

    def __init__(self, log=False):
        self.log = log

    def mudarFog(self, fog, Fogs):
        s = [x for x in Fogs if x not in fog]
        for i in s: #list(reversed(s)):
            mudar = False
            parametro = np.array(Fogs[i]).flat
            n=parametro[4]
            if n==0:
                n=1
            #if (parametro[0] > Limiares[0] or (parametro[1]/n)<(Limiares[1]/n) or parametro[2] > Limiares[2] or parametro[3] > Limiares[3] or n<Limiares[4]):
            #if (parametro[0] < Limiares[0]):
            if (parametro[0] < Limiares[0] and parametro[4]<1):
                mudar = True
            else:
                mudar = False
            if (mudar == True):
                return i
        return fog

    def atualizarFogsEntrada(self, fogs):
        mudar=False
        parametro =  np.array(fogs[server]).flat
        #n=parametro[4]
        #if n==0:
        #        n=1
        #if (parametro[0] > Limiares[0] or (parametro[1]/n)<(Limiares[1]/n) or parametro[2] > Limiares[2] or parametro[3] > Limiares[3] or n>Limiares[4]):
        #if (client[0]<Limiares[1] or client[1]>=Limiares[2] or client[2]>=Limiares[3]):
        if (parametro[0]>Limiares[0] or parametro[4]>Limiares[4]):
            mudar = True
        if (mudar == True):
            return self.mudarFog(server, fogs)
        else:
            return server

    def Politica(self, matrizesdepreferencias):
        ip=ip
        return self.atualizarFogsEntrada(matrizesdepreferencias)
