## Sobre o programa
O programa é baseado em um framework dash para NS-3 (@haraldott/dash). Sua principal função é simular transmissões dash em diferentes cenários criados a partir do NS-3, podendo adicionar diferentes algoritmos de adaptação, ou utilizar um dos algoritmos presentes no framework (Tobasco, Panda e Festive).

## Parâmetros
Os seguintes parâmetros devem ser especificados para executar o programa:
simlationId: o ID da simulação, para obter diferentes logs em simulações que utilizam o mesmo cenário (mesmo algoritmo e mesmo número de clientes).
- numberOfClients: O número de clientes usado na simulação.
- segmentDuration: A duração de cada segmento de vídeo (em microsegundos).
- adaptationAlgo: O algoritmo de adaptção que o cliente utiliza. Os algoritmos pré-instalados são: tobasco, panda e festive.
- segmentSizeFile: O arquivo contendo o tamanho dos segmentos de vídeo. A estrutura do arquivo é uma matriz (n,m), com n sendo o número de níveis de representação e m sendo o número de segmentos. Por exemplo, um vídeo codificado em três níveis de representação e dividido em 2 segmentos pode ser descrito através de um arquivo:

1564 22394

1627 46529

1987 121606

## Como executar

Para executar o programa é necessário seguir o seguintes passos:

1. Acessar a pasta ns-3.29
2. Mover a pasta 'dash-migration' para a pasta 'src' do ns-3.29 
3. Habilitar os testes e exemplos através do comando:

  ./waf configure --enable-tests --enable-examples
  CXXFLAGS="-Wall" ./waf configure --enable-examples --enable-tests (Comando caso precise para desabilitar 'Warnings treated as errors')

4. Construir e linkar as dependências e configurações estabelicidas através do comando:

  ./waf

5. Rodar o script dash-migration através do comando:

  ./waf --run=dash-migration-v2

6. Alternativamente pode-se rodar o script dash-migration, localizado na pasta src do ns-3.29, passando os parâmetros necessários descritos anteriormente. Exemplo:

  ./waf --run="dash-migration --simulationId=1 --numberOfClients=3 --adaptationAlgo=panda --segmentDuration=2000000 --segmentSizeFile=src/dash-migration/dash/segmentSizesBigBuck1A.txt"
  
7. A partir do diretorio do Ns3 pode-se chamar o script em python para se fazer multiplas simulações. Exemplo:

  python3 src/dash-migration/Run.py dash-migration-v2 -i simulationId -s seedValue -r 17 -args politica=0 -args numberOfClients=32 -args segmentSizeFile=src/dash-migration/dash/segmentSizesBigBuck90.txt -ug -g src/dash-migration/graficos.py -rargs runs=r -cargs numberOfClients=c -gargs seg=segmentSizesBigBuck90.txt

## Resultados
Os resultados podem ser obtidos através dos logs dentro da pasta "dash-log-files"

## Graficos
Os gráficos são gerados pelo arquivo 'graficos.py' que se encontra dentro da pasta dash-migration, antes de rodar o script deve-se alterar os parâmetros inicias dentro do método 'main' de forma a retratar a simulação feita. No momento é gerado 5 graficos que ficam na mesma pasta onde de encontram os logs, abaixo um exemplo de como fazer o setup.
->Parametros:
   ->adaptAlgo="festive" (Algoritmo de adaptação escolhido)
   ->simulation=1  (SimulationId escolhido para a simulação)
   ->numberOfClients=15 - (Valor referente ao número de clientes na simulação)
   ->segmentfile="segmentSizesBigBuck90.txt" (Arquivo de segmento utilizado)
