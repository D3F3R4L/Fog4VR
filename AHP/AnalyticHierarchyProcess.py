# coding-UTF-8
import numpy as np
import math


class AHP():

    def __init__(self, log=False):
        self.log = log
        self.soma = [0,0,0,0]

    @staticmethod
    def AutoValor(matriz, precisao, interacao=100, autovetor_anterior=None):
        matriz_quadrada = np.linalg.matrix_power(matriz, 2)
        soma_linhas = np.sum(matriz_quadrada, axis=1)
        soma_coluna = np.sum(soma_linhas, axis=0)
        autovetor_atual = np.divide(soma_linhas, soma_coluna)

        if autovetor_anterior is None:
            autovetor_anterior = np.zeros(matriz.shape[0])

        diferenca = np.subtract(autovetor_atual, autovetor_anterior).round(precisao)
        if not np.any(diferenca):
            return autovetor_atual.round(precisao)

        interacao -= 1
        if interacao > 0:
            return AHP.AutoValor(matriz_quadrada, precisao, interacao, autovetor_atual)
        else:
            return autovetor_atual.round(precisao)

    @staticmethod
    def Consistencia(matriz):
        if matriz.shape[0] and matriz.shape[1] > 2:
            lambda_max = np.real(np.linalg.eigvals(matriz).max())
            ic = (lambda_max - len(matriz)) / (len(matriz) - 1)
            ri = {3: 0.52, 4: 0.89, 5: 1.11, 6: 1.25, 7: 1.35, 8: 1.40, 9: 1.45, 10: 1.49, 11: 1.52, 12: 1.54, 13: 1.50,
                  14: 1.58, 15: 1.59}
            rc = ic / ri[len(matriz)]
        else:
            lambda_max = 0
            ic = 0
            rc = 0

        return lambda_max, ic, rc

    def Influenciacompeso(self, parametro):
        #matriz = np.array([
        #    [   1,    4,  16, 64],
        #    [ 1/4,    1,   4, 16],
        #    [1/16,  1/4,   1,  4],
        #    [1/64, 1/16, 1/4,  1]
        #])
        matriz = np.array([
        [1,    3,   6  ],
        [1/3,  1,   3  ],
        [1/6, 1/3,  1  ]
        ])
        precisao = 10
        peso = AHP.AutoValor(matriz, precisao)
        #print(peso)
        prioridadesGlobais = {}
        parametros = []
        #self.soma=[0,0,0,0]
        for idfog in parametro:
            influ = [0, 0, 0]
            parametros = np.array(parametro[idfog]).flat
            for i in range(0, 3):
                influ[i]=parametros[i] * peso[i]
                #self.soma[i] += influ[i]
            prioridadesGlobais[idfog] = sum(influ)
        #print(prioridadesGlobais)
        return prioridadesGlobais

    def Normaliza(self, parametro):
        dicionarionorma = {}
        for idfog in parametro:
            parametros = np.array(parametro[idfog]).flat
            normaliza = [0, 0, 0]
            for i in range(0, 3):
                if (self.soma[i]==0):
                    normaliza[i]=0
                else:
                    normaliza[i] = parametros[i] / (self.soma[i]/len(self.soma))
                    #normaliza[i]=parametros[i]/np.max(parametros)
            dicionarionorma[idfog] = sum(normaliza)
        return dicionarionorma

    def Distanciaeuclidiana(self, parametro,ip):
        dicdistancia = {}
        atual = parametro[ip]
        del (parametro[ip])

        for idfog in parametro:
            parametros = np.array(parametro[idfog]).flat
            soma=0
            for i in range(0, 3):
                #print(atual[i])
                #print(parametros[i])
                soma += atual[i] - parametros[i]

            dicdistancia[idfog] = soma
        return dicdistancia

    def score(self, parametro):
        anterior = 0
        fogid=0
        for idfog in parametro:
            parametros = parametro[idfog]
            if parametros > anterior :

                fogid = idfog
                anterior = parametro[idfog]
        retorno = [fogid, anterior]
        return retorno

    def Politica(self, matrizesdepreferencias):
        matrizesdepreferencias = matrizesdepreferencias
        influ = self.Influenciacompeso(matrizesdepreferencias)
        #normalizado = self.Normaliza(influ)
        #distancia = self.Distanciaeuclidiana(normalizado,ip)
        #print(normalizado)
        #print(distancia)
        #print(self.score(distancia))
        return influ
