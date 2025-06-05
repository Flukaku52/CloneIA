# Clone Rapidinha no Cripto

Este projeto cria um clone de IA que imita o estilo de comunicação de Renato Santanna Silva para o quadro "Rapidinha no Cripto", gerando automaticamente scripts para reels sobre as principais notícias do mundo cripto para um público leigo.

## Funcionalidades

- **Geração de Conteúdo**: Gera scripts no estilo "Rapidinha no Cripto", mantendo os trejeitos e características de comunicação do apresentador.
- **Coleta de Notícias Reais**: Integração com APIs para coletar notícias reais sobre criptomoedas.
- **Explicações com IA**: Usa a API da OpenAI para gerar explicações personalizadas para as notícias.
- **Análise de Vídeos**: Extrai e analisa o estilo de comunicação a partir de vídeos existentes.
- **Notícias Simuladas**: Inclui um conjunto de notícias simuladas para demonstração e backup.
- **Formato Conciso**: Gera conteúdo otimizado para vídeos de aproximadamente 3 minutos.
- **Interface de Linha de Comando**: Facilita a geração e visualização de scripts.
- **Cache de Explicações**: Armazena explicações geradas pela IA para economizar chamadas à API.

## Requisitos

- Python 3.8+

## Instalação

1. Clone o repositório:
```
git clone [URL_DO_REPOSITÓRIO]
```

2. Crie e ative um ambiente virtual:
```
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Execute o script de configuração:
```
python setup.py
```

## Configuração

Antes de usar o projeto, configure as chaves de API no arquivo `.env`:

```
# Chaves de API para serviços
OPENAI_API_KEY=sua_chave_api_aqui
CRYPTOCOMPARE_API_KEY=sua_chave_cryptocompare_aqui
NEWSAPI_KEY=sua_chave_newsapi_aqui
```

Você pode obter essas chaves gratuitamente nos respectivos sites:
- [OpenAI](https://platform.openai.com/)
- [CryptoCompare](https://min-api.cryptocompare.com/)
- [NewsAPI](https://newsapi.org/)

## Uso dos Vídeos de Referência

Para melhorar a qualidade do clone de IA, você pode usar seus vídeos existentes do quadro "Rapidinha no Cripto":

1. Coloque seus vídeos na pasta `reference/videos`

2. Processe os vídeos para extrair o estilo de comunicação:
```
python video_processor.py --all
```

3. Atualize o prompt da IA com base na análise:
```
python update_ai_prompt.py
```

4. Gere um novo script usando o prompt atualizado:
```
python clone_rapidinha_ai.py --generate
```

### Processamento de Vídeos Passo a Passo

Se preferir, você pode executar cada etapa do processamento separadamente:

1. Extrair áudio dos vídeos:
```
python video_processor.py --extract
```

2. Transcrever o áudio:
```
python video_processor.py --transcribe
```

3. Analisar as transcrições:
```
python video_processor.py --analyze
```

## Uso Geral

### Gerar um novo script com notícias reais e explicações de IA
```
python clone_rapidinha_ai.py --generate
```

### Gerar um script com notícias simuladas
```
python clone_rapidinha_ai.py --generate --mock
```

### Gerar um script sem usar IA para explicações
```
python clone_rapidinha_ai.py --generate --no-ai
```

### Gerar um script com um número específico de notícias
```
python clone_rapidinha_ai.py --generate --count 2
```

### Listar scripts gerados anteriormente
```
python clone_rapidinha_ai.py --list
```

### Visualizar um script específico
```
python clone_rapidinha_ai.py --view [CAMINHO_DO_SCRIPT]
```

## Exemplo de Saída

```
Fala galera! Bora lá com mais uma Rapidinha no Cripto!

Vamos às notícias!

1. Bitcoin ultrapassa US$ 50.000 pela primeira vez em 2023
O Bitcoin finalmente quebrou a barreira dos 50 mil dólares! É como se aquele investimento que você fez ano passado de repente valesse 25% a mais. Essa alta vem principalmente da crescente adoção institucional e da expectativa dos ETFs de Bitcoin à vista. Será que vamos ver os 100 mil em breve?

2. Ethereum implementa atualização que reduz taxas de transação
O Ethereum acaba de implementar uma atualização que reduz drasticamente as taxas! Imagina poder transferir dinheiro pagando centavos em vez de dezenas de reais. Essa mudança vai permitir que muito mais pessoas usem a rede para aplicações do dia a dia, impulsionando ainda mais o ecossistema.

3. Brasil se torna o 5º país com maior adoção de criptomoedas
Olha só, o Brasil está bombando no mundo cripto! Já somos o 5º país com maior adoção dessas moedas digitais. Isso mostra como o brasileiro está antenado nas novas tecnologias financeiras, buscando alternativas para proteger seu dinheiro e fazer transações mais eficientes.

E é isso por hoje, pessoal! Até a próxima rapidinha!
```

## Estrutura do Projeto

```
CloneRapidinha/
├── clone_rapidinha_ai.py     # Interface de linha de comando com IA
├── rapidinha_generator_ai.py # Gerador de conteúdo com IA
├── ai_explainer.py           # Módulo para gerar explicações com IA
├── crypto_news_collector.py  # Coletor de notícias reais
├── video_processor.py        # Processador de vídeos de referência
├── update_ai_prompt.py       # Atualizador de prompt da IA
├── setup.py                  # Script de configuração
├── data/                     # Dados coletados
├── cache/                    # Cache de explicações da IA
├── scripts/                  # Scripts gerados
├── reference/                # Materiais de referência
│   ├── videos/               # Vídeos de referência
│   ├── audio/                # Áudio extraído dos vídeos
│   ├── transcripts/          # Transcrições dos áudios
│   └── analysis/             # Análise do estilo de comunicação
├── requirements.txt          # Dependências
└── README.md                 # Documentação
```

## Personalização

O estilo de comunicação está configurado no arquivo `rapidinha_generator_ai.py`. Você pode ajustar as frases e explicações para refinar ainda mais a imitação do seu jeito de falar.

O prompt para a IA está configurado no arquivo `ai_explainer.py`. Você pode ajustá-lo manualmente ou usar o processo de análise de vídeos para atualizá-lo automaticamente.

## Próximos Passos

- ✅ Implementar coleta de notícias reais de fontes confiáveis
- ✅ Integrar com API de IA para gerar explicações personalizadas
- ✅ Analisar vídeos existentes para capturar o estilo de comunicação
- Adicionar integração com APIs de geração de voz para criar áudio automaticamente
- Criar interface web para gerenciamento de conteúdo
- Implementar geração automática de vídeo com legendas
