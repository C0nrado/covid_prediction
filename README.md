# Prevendo Mortes por Covid

O projeto consistiu em produzir módulos, scripts, notebooks para as tarefas de análise exploratória e modelagem preditiva do número de mortes pela COVID em 2020.

Os dados oferecidos são acessados pela api:

* COVID TRACKING: https://api.covidtracking.com 
    - Valores históricos: /v1/us/daily.csv
    - Meta dados dos Estados: /v1/states/info.csv
    - Valores históricos para Estados: /v1/states/{state}/current.csv
   
Além desses, foram também consultados:

* POPULATION ESTIMATES API: https://api.census.gov/data/2019/pep/population
    - Consulta a estimativas populacionais nos EUA.


# 1. Ferramentas Utilizadas

Foram resultados desse projeto, além do sue objetivo principal o resenvolvimento de duas aplicações:

## O módulo `api_manager`
---

LOCALIZAÇÃO 

    .resources/
        |__io/
            |__api_manager.py

Esse modulo oferece uma class `ApiManager` que automatiza os requests as APIs, o gerencimento dos diretório onde os dados serão armazenados ao mesmo tempo que ofere rapido acesso a eles.

DESCRIÇÃO

A classe efetua essas atividades automáticamente, requerindo apenas o input de um arquivo de configuração no formato YAML.

## A classe `DataframeTransformer` (módulo transformers.py)
---

LOCALIZAÇÃO

    .resources/
        |__processing/
                |__transformers.py

DESCRIÇÃO

Este módulo perimte construir pipelines de transformação em estruturas de dados. Nesse projeto ele foi utilizado para fazer pipelines de processamento dos dados buscados na API.

Foi pensado em ser versátil e prático e por isso ele é capaz de utilizar com facilidade funções customizadas para integrar o pipeline.

## Scripts
---

Os scripts desenvolvidos são únicos para esse projeto e tem como objetivos:

* Coletar dados via API
* Processar e alimentar dados para análises
* Criar datasets
* Treinar e avaliar modelos preditivos


        .scripts/
            |__retrieve-data-nb01.py    # coletar dados do covid
            |__retrieve-data-by-states.py   # coletar dados por estados
            |__retrieve-data-census.py  # coletar dados demográficos
            |__processing_data_by_states.py     # preparar dados para EDA
            |__make_datasets.py     # construir `traininig` e `test` sets
            |__training.py      # trainer modelo de regressão
            |__model_evaluation.py  # Calcular previsão e métrica para o `test_set`

O processo de captura, processamento, treinamento e dumping do modelo é todo realizado pela execução dos scripts na sequência apresentada.

* Acessar `--help` do script informa sobre inputs necessários para rodá-los.

## Notebooks
---

Os notebooks se encontra na raiz do repositório e foram utilizados para *análise exploratória* (EDA), vizualização e avaliação do modelo.

A Análise Exploratória dos dados nesse projeto teve como foco primário estudar as variáveis acessíveis na COVID TRACKING API e definir estratégias para modelagem preditiva. Nesse escopo encontram-se atividades de visualização, tratamento, engenharia de atributos e análises estatísticas e de mineraçao.

* `01_exploração_inicial.ipynb`
    
    Esse notebook investiga as características da séries temporais das variáveis relacionadas a epidemia do covid. Define a melhor variável alvo com seus possíveis preditores, além de investigar tratamentos nos dados visando ganhos no modelo preditivo.

* `02_EDA_avancada.ipynb`

    O foco deste notebook é visualização e mineração para definição de estratégias para o modelo preditivo. Foram empegadas técnicas e/ou algorítimos para decomposição espectral das séries temporais e clusterização para detecção de anomalias. A mineração se voltou para com essas técnicas buscar perfis regionais de evolução da covid no território americano.

* `03_Avaliacao_regressao,ipynb`

    Este é um notebook dedicado para visualização dos resultados/previsões do modelo nos dados de teste.

    Aqui foram  exploradas tanto as taxas de mortes diárias como acumuladas ao longo do período de teste.

## Outros
---

Diretório `./config`
> Aqui ficam armazenados os arquivos YAML utilizados pela classe `ApiManager` para coletar e gerenciar os dados oriundos das API configuradas por ele.

Diretório `/data`
> Esse diretório mantém arquivos relevantes a serem consumidos por scripts ou notebooks. Ao contrário do `./cache` que não é versionado.

Package `resources`
> Envelopa as principais funções e módulos necessários no projeto por funcionalidade.

# 2. Análise Exploratória de Dados EDA
## Sumário Executivo

* Inicialmente os dados foram avaliados quanto a sua dispoibilidade, e considerando a *concentração de null* com o processo de aderência dos estados em reportar seus dados reltivos a covid foi concluído que os dados de  janeiro, fevereiro e março devem ser descartados pois a sua representatividade da situação da covid pode ser questionada.

* Foi decido que a modelagem preditiva seria mais beneficiada se trabalhar com taxas de variação (como aquelas sufixadas por *Increase*) e portanto a tarefa de regressão ideal seria a previsão da variável `deathIncrease`. Isso, contudo, apresenta desafios pois possui um comportamento cíclico característico.

<center><img src="data/imgs/deathIncrease_noisy.png"></center>

* Com a modelagem da séries de dados `deathIncrease`, representando a taxa de mortes, baseada na *seasonal trend decomposition* foi possível obter uma suavização com pouquíssima perde de informação em relação ao dados brutos quando comparada aos dados do campo de *mortes acumuladas*. A análise das oscilações indica que elas derivam mais do processo de registro de dados do que ao fenômeno da covid. 

<center><img src="data/imgs/stl_trends_deaths.png"></center>

Com a nova curva representativa da taxa de mortes, foi avaliado como a série se relacionada com as outras variáveis do dataset e a capacidade preditiva destas.

Desse modo, inspirado na função de autocorrelação, foi avaliado qual a defasage, ou quantos *lags* havia entre a taxa de mortes e as demais variáveis (em formas de taxas) de modo a maximizar a o coeficiente de Pearson entre elas. Houve resultados promissores.

    [inIcuCurrently...........] Linear Corr (0.820) maximizado para lag => 00
    [hospitalizedCurrently....] Linear Corr (0.616) maximizado para lag => 11
    [hospitalizedIncrease.....] Linear Corr (0.808) maximizado para lag => 10
    [positiveIncrease.........] Linear Corr (0.401) maximizado para lag => 31


`hospiralizedIncrease` e `positiveIncrease` apresentaram capcidade modesta à boa de previsão da taxa de mortos. No geral, as variáveis apresentam uma proximidade entre suas séries temporais e existe a possibilidade de modelos de regressão linear serem aplicados. Mas ainda a melhor forma de serem aplicados é um ponto a ser investigado. Como esses dados são nacionais eles podem estar escondendo aspectos locais, que por conta de não serem aproveitadas no treinamento do modelo, podem prejudicar sua performance.

Essa exploração inicial pode também estabelecer técnicas e ajustes a serem utilizados em um conjunto de dados maior. Esses detalhes foram aproveitados e aperfeoçados em scripts para prover dados a análises mais detalhadas.

Primeiramente, a partir da seleção anterior da variável *taxa de mortes* por covid (`deathIncrease`) para cada estado, é feita a decomposição da parte sasonal da série, e os valores da *trend* são transformados no índice *taxa de mortes por cada 100.000 habitantes* para amenizar os efeitos da diferenças populaiconais entre os estados que há nos dados absolutos. 

<center><img src="data/imgs/mean_component.png"></center>

A decomposição espectral do dataset de séries *individuais* por estados vai fornecer um conjunto menor de séries que apresentam características *compartilhadas* por todos os estados. Cada uma dessas séries será chamada de **compontes principais** e elas podem fornecer atributos com os quais os estados podem ser avaliados entre si.

No dataset presente, a decomposição em 4 componentes já representou ~95% de toda a variância do dataset.

<center><img src="data/imgs/components.png"></center>

<center><img src="data/imgs/clsuters_parall_plot.png"></center>

Ambos, componentes e clusters (em análise realizada posterioremente), indicam que os estados divergem quanto ao ínicio da pandemia, mas em meados do fim de ano as componentes são muito parecidas.

A excessão se faz pela componente 2, que está ligada a estados que diveram uma forte alta de casos de covid no período em que o modelo será avaliado. A imagem abaixo ilustra a disposição dos estados para cada uma das componentes. 

<center><img src="data/imgs/projeçoes_estados.png"></center>

Ao analisar a componente 2, observou-se que seu efeito é muito localizado em uma região com pouco peso populacional nos EUA, então não estará pesando fortemente na taxa de mortes nacionais.

**BOTTOMLINE**

O comportamento do covid nos eua evoluiu para um estado em que o comportamento da pandemia é similar mesmo em regiões geograficamente afastadas. 

O período inicial dos dados será descartado pois nesse período o estados apresentam séries bastantes dispersas. A partir destas informações já é possível desenhar modelos preditivos e de *forecasting* basedos nestes dados. Opções são utilizar a própria autocorrelação das séries nacionais em modelos autoregressivos como ARIMA ou utilizar utilizar preditores.

# 3. Modelo Regressivo

O modelo de previsão vai se passear na relação lienar entre os preditores encontrados.

Não se observou a necessidade de criar modelos para grupos de estados específicos, apesar de a taxa de mortes nacional ser uma composição das taxas locais, e de os estados terem tidos pontos de partidas diversos ao longo de 2020, a tendência tem sido uma uniformização dos efeitos da COVID e as estatísticas nacionais foram utilizadas diretamente.

Os dados foram tratados através das técnicas discutidas anteriormente, a decomposição sasonal (Loess) e utilizando os *lags* caracteríticos dos preditores.

O aprendizado foi concluído pelo algorítmo de regresssão dos mínimos quadráticos (regressão linear). Não foram utilizadas penalizações pois são poucos preditores.

<center><img src="data/imgs/model_performance.png"></center>

O modelo se aproxima bastante da taxa de mortes suavizada com Loess e se faz assim representativo da série temporal dos registros de `deathIncrease`. Ao lado, ao integrar o modelo, o o viés (bias) do model vai ficando aparente. 