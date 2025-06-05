# Clone IA para "Rapidinha Cripto" (Versão Otimizada)

Este projeto cria um clone de IA que imita o estilo de comunicação de Renato Santanna Silva para o quadro "Rapidinha Cripto", gerando automaticamente conteúdo completo (áudio e vídeo) com o estilo e voz do apresentador.

## Funcionalidades

- **Clonagem de Voz**: Usa a API da ElevenLabs para clonar a voz do apresentador.
- **Geração de Áudio**: Converte os scripts em áudio usando a voz clonada.
- **Geração de Vídeo**: Cria vídeos com o clone visual do apresentador usando a API do HeyGen.
- **Formato Conciso**: Gera conteúdo otimizado para vídeos de aproximadamente 3 minutos.
- **Interface de Linha de Comando**: Facilita a geração e visualização de áudios e vídeos.

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
ELEVENLABS_API_KEY=sua_chave_elevenlabs_aqui
HEYGEN_API_KEY=sua_chave_heygen_aqui
```

Você pode obter essas chaves gratuitamente nos respectivos sites:
- [ElevenLabs](https://elevenlabs.io/)
- [HeyGen](https://www.heygen.com/)

## Uso

### Geração de Vídeo

#### Gerar um vídeo completo usando o gerador otimizado
```
python rapidinha_generator_optimized.py --script "Seu script aqui"
```

#### Testar apenas a geração de vídeo com o HeyGen
```
python test_optimized_generator.py --generate
```

#### Listar avatares disponíveis na conta do HeyGen
```
python test_optimized_generator.py --list-avatars
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

## Uso dos Vídeos de Referência

Para melhorar a qualidade do clone de IA, você pode usar seus vídeos existentes do quadro "Rapidinha Cripto":

1. Coloque seus vídeos na pasta `reference/videos`

2. Extraia amostras de voz dos vídeos e adicione-as ao ElevenLabs para melhorar a qualidade da voz clonada

3. Crie um avatar personalizado no HeyGen usando um dos vídeos de referência

4. Atualize o arquivo de configuração com o ID do seu avatar personalizado

## Estrutura do Projeto

```
CloneIA/
├── heygen_video_generator_optimized.py # Integração otimizada com a API do HeyGen
├── rapidinha_generator_optimized.py  # Gerador otimizado de vídeos completos
├── test_optimized_generator.py       # Script para testar o gerador otimizado
├── setup.py                          # Script de configuração
├── core/                             # Módulos principais otimizados
│   ├── audio.py                      # Geração de áudio otimizada
│   ├── text.py                       # Processamento de texto
│   ├── video.py                      # Geração de vídeo
│   └── utils.py                      # Funções utilitárias
├── config/                           # Configurações
│   ├── voice_config.json             # Configuração da voz clonada
│   └── avatar_config.json            # Configuração do avatar
├── output/                           # Saídas geradas
│   ├── audio/                        # Áudios gerados
│   └── videos/                       # Vídeos gerados
├── reference/                        # Materiais de referência
│   ├── videos/                       # Vídeos de referência
│   └── voice_samples/                # Amostras de áudio extraídas
├── requirements.txt                  # Dependências
└── README.md                         # Documentação
```

## Personalização

Você pode personalizar o projeto de várias maneiras:

1. **Configuração do Avatar**: Edite o arquivo `config/avatar_config.json` para usar seu próprio avatar do HeyGen.

2. **Configuração da Voz**: Edite o arquivo `config/voice_config.json` para usar seu próprio perfil de voz do ElevenLabs.

3. **Estilo de Fala**: Ajuste os parâmetros de geração de áudio no arquivo `core/audio.py` para controlar a velocidade, entonação e estilo da fala.

## Próximos Passos

- ✅ Implementar integração com APIs de geração de voz para criar áudio automaticamente
- ✅ Implementar geração automática de vídeo com clone visual
- Melhorar a qualidade visual dos vídeos com elementos gráficos
- Criar interface web para gerenciamento de conteúdo
- Implementar publicação automática nas redes sociais
