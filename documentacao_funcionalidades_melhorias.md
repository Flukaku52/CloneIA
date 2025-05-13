# Documentação de Funcionalidades e Melhorias - Projeto CloneIA

## Índice
1. [Funcionalidades Atuais](#funcionalidades-atuais)
   - [Geração de Áudio](#geração-de-áudio)
   - [Geração de Vídeo](#geração-de-vídeo)
   - [Processamento de Texto](#processamento-de-texto)
   - [Utilitários](#utilitários)
2. [Perfis de Voz](#perfis-de-voz)
3. [Avatares](#avatares)
4. [Fluxos de Trabalho](#fluxos-de-trabalho)
5. [Melhorias Propostas](#melhorias-propostas)
   - [Curto Prazo](#curto-prazo)
   - [Médio Prazo](#médio-prazo)
   - [Longo Prazo](#longo-prazo)
6. [Problemas Conhecidos](#problemas-conhecidos)
7. [Referências e Recursos](#referências-e-recursos)

## Funcionalidades Atuais

### Geração de Áudio

#### 1. Clonagem de Voz
- **Descrição**: Criação de perfis de voz personalizados usando a API do ElevenLabs
- **Arquivos Principais**: `core/audio.py`, `audio_generator.py`
- **Parâmetros Ajustáveis**:
  - `stability`: Controla a consistência da voz (0.0-1.0)
  - `similarity_boost`: Controla a semelhança com a voz original (0.0-1.0)
  - `style`: Controla a preservação do estilo de fala (0.0-1.0)
  - `use_speaker_boost`: Melhora a qualidade geral da voz (true/false)
  - `model_id`: Define o modelo de IA usado para geração

#### 2. Geração de Áudio a partir de Texto
- **Descrição**: Conversão de texto em áudio usando os perfis de voz criados
- **Arquivos Principais**: `core/audio.py`, `test_flukakuia_novo_texto.py`
- **Funcionalidades**:
  - Otimização automática de texto para fala mais natural
  - Suporte a múltiplos perfis de voz
  - Geração de arquivos MP3 com timestamp

#### 3. Extração de Amostras de Áudio
- **Descrição**: Extração de amostras de áudio de vídeos para treinamento de voz
- **Arquivos Principais**: `extract_voice_samples.py`, `extract_short_samples.py`
- **Funcionalidades**:
  - Extração de amostras longas para treinamento inicial
  - Extração de amostras curtas (7-12 segundos) para refinamento
  - Análise de qualidade das amostras

### Geração de Vídeo

#### 1. Integração com HeyGen
- **Descrição**: Geração de vídeos com avatares usando a API do HeyGen
- **Arquivos Principais**: `heygen_video_generator.py`, `heygen_video_generator_optimized.py`
- **Funcionalidades**:
  - Criação de vídeos a partir de texto ou áudio pré-gravado
  - Suporte a avatares personalizados e padrão
  - Configuração de dimensões e fundo do vídeo

#### 2. Criação e Gerenciamento de Avatares
- **Descrição**: Criação e gerenciamento de avatares personalizados no HeyGen
- **Arquivos Principais**: `create_avatar_from_reference.py`, `list_avatars.py`
- **Funcionalidades**:
  - Criação de avatares a partir de vídeos de referência
  - Listagem de avatares disponíveis na conta
  - Configuração e armazenamento de IDs de avatar

### Processamento de Texto

#### 1. Otimização de Texto para Fala
- **Descrição**: Ajuste de texto para melhorar a naturalidade da fala gerada
- **Arquivos Principais**: `core/text.py`, `optimize_text_for_natural_speech.py`
- **Funcionalidades**:
  - Remoção de pontuação excessiva
  - Ajuste de abreviações e números
  - Formatação de expressões específicas do estilo "Rapidinha Cripto"

### Utilitários

#### 1. Gerenciamento de Configurações
- **Descrição**: Gerenciamento de configurações de voz, avatar e APIs
- **Arquivos Principais**: `core/utils.py`, `config/*.json`
- **Funcionalidades**:
  - Carregamento e salvamento de configurações
  - Gerenciamento de chaves de API
  - Criação de diretórios e arquivos

#### 2. Scripts de Teste
- **Descrição**: Scripts para testar diferentes aspectos do sistema
- **Arquivos Principais**: `test_*.py`
- **Funcionalidades**:
  - Testes de geração de áudio com diferentes perfis
  - Testes de geração de vídeo com diferentes avatares
  - Testes de otimização de texto

## Perfis de Voz

### 1. FlukakuIA
- **ID**: oG30eP3GaYrCwnabbDCw
- **Configurações**:
  - stability: 0.05
  - similarity_boost: 0.80
  - style: 1.0
  - use_speaker_boost: true
  - model_id: eleven_multilingual_v2
- **Características**: Alta expressividade, boa semelhança com a voz original, preservação máxima do estilo de fala
- **Recomendado para**: Uso principal nos vídeos "Rapidinha Cripto"

### 2. FlukakuFluido
- **ID**: oG30eP3GaYrCwnabbDCw
- **Configurações**:
  - stability: 0.15
  - similarity_boost: 0.65
  - style: 0.85
  - use_speaker_boost: true
  - model_id: eleven_multilingual_v2
- **Características**: Expressividade moderada, semelhança moderada com a voz original, boa preservação do estilo de fala
- **Recomendado para**: Alternativa caso o FlukakuIA apresente problemas

## Avatares

### 1. Flukaku Rapidinha (Atual)
- **ID**: 189d9626f12f473f8f6e927c5ec482fa
- **Status**: Ativo - Avatar principal em uso
- **Tipo**: Avatar personalizado baseado em vídeos de referência
- **Observação**: Configurado como avatar padrão em 12/05/2025

### 2. Flukaku Rapidinha (Anterior)
- **ID**: 01cbe2535df5453a97f4a872ea532b33
- **Status**: Substituído pelo novo avatar
- **Tipo**: Avatar personalizado baseado em vídeos de referência
- **Observação**: Usado anteriormente como avatar padrão

### 3. Flukaku Rapidinha (Legado)
- **ID**: ae9ff9b6dc47436c8e9a30c25a0d7b29
- **Status**: Legado - não mais utilizado
- **Tipo**: Avatar personalizado baseado em vídeos de referência

### 4. Avatares Padrão
- **Daisy-inshirt-20220818**: Avatar feminino padrão do HeyGen
- **Outros avatares padrão**: Disponíveis através da API do HeyGen

## Fluxos de Trabalho

### 1. Geração Completa de Vídeo
1. Preparar o script do vídeo
2. Otimizar o texto para fala usando `core/text.py`
3. Gerar áudio com o perfil FlukakuIA usando `core/audio.py`
4. Gerar vídeo com o áudio usando `heygen_video_generator.py`
5. Salvar o vídeo final na pasta `output/videos`

### 2. Refinamento de Voz
1. Extrair amostras de áudio de vídeos usando `extract_voice_samples.py`
2. Extrair amostras curtas para refinamento usando `extract_short_samples.py`
3. Adicionar as amostras ao ElevenLabs para melhorar o perfil de voz
4. Testar o perfil atualizado usando scripts de teste

## Melhorias Propostas

### Curto Prazo

#### 1. Resolução de Problemas com Avatar
- **Descrição**: Resolver o problema "not ready" com o avatar personalizado
- **Abordagem**: Recriar o avatar com vídeos de melhor qualidade ou contatar suporte do HeyGen
- **Prioridade**: Alta

#### 2. Refinamento do Perfil de Voz
- **Descrição**: Continuar melhorando o perfil de voz FlukakuIA
- **Abordagem**: Adicionar mais amostras de áudio de alta qualidade ao ElevenLabs
- **Prioridade**: Média

#### 3. Otimização de Texto para Termos Técnicos
- **Descrição**: Melhorar a pronúncia de termos técnicos de criptomoedas
- **Abordagem**: Adicionar regras específicas para termos como "staking", "DeFi", "NFT", etc.
- **Prioridade**: Média

### Médio Prazo

#### 1. Interface de Linha de Comando Unificada
- **Descrição**: Criar uma CLI unificada para todas as funcionalidades
- **Abordagem**: Desenvolver um script principal que integre todas as funcionalidades
- **Prioridade**: Média

#### 2. Automação de Coleta de Notícias
- **Descrição**: Automatizar a coleta de notícias sobre criptomoedas
- **Abordagem**: Integrar APIs de notícias e criar um sistema de filtragem
- **Prioridade**: Média

#### 3. Geração Automática de Scripts
- **Descrição**: Automatizar a geração de scripts para os vídeos
- **Abordagem**: Usar IA para transformar notícias em scripts no estilo "Rapidinha Cripto"
- **Prioridade**: Média

### Longo Prazo

#### 1. Interface Web
- **Descrição**: Criar uma interface web para gerenciar todo o processo
- **Abordagem**: Desenvolver uma aplicação web com Flask ou Django
- **Prioridade**: Baixa

#### 2. Publicação Automática
- **Descrição**: Automatizar a publicação dos vídeos em plataformas sociais
- **Abordagem**: Integrar APIs de plataformas como YouTube, Instagram, TikTok
- **Prioridade**: Baixa

#### 3. Análise de Engajamento
- **Descrição**: Analisar o engajamento dos vídeos publicados
- **Abordagem**: Coletar métricas das plataformas e gerar relatórios
- **Prioridade**: Baixa

## Problemas Conhecidos

### 1. Avatar "Not Ready"
- **Descrição**: O avatar personalizado antigo (ID: 84aa751d70e24c8eb5a12cac86762e6a) apresenta o erro "not ready"
- **Solução**: Novo avatar criado (ID: 4f8680b8f3654e8da9f8b274abd1266b) para substituir o anterior
- **Status**: Resolvido - Pendente de teste

### 2. Pausas na Fala
- **Descrição**: Algumas vezes a voz gerada apresenta pausas não naturais
- **Solução Temporária**: Otimizar o texto removendo pontuação excessiva
- **Status**: Em andamento

### 3. Pronúncia de Termos Técnicos
- **Descrição**: Alguns termos técnicos de criptomoedas não são pronunciados corretamente
- **Solução Temporária**: Ajustar manualmente a escrita desses termos no script
- **Status**: Em andamento

## Referências e Recursos

### APIs
- [ElevenLabs](https://elevenlabs.io/) - API para clonagem e geração de voz
- [HeyGen](https://www.heygen.com/) - API para geração de vídeos com avatares

### Documentação
- [Documentação ElevenLabs](https://docs.elevenlabs.io/)
- [Documentação HeyGen](https://docs.heygen.com/)

### Guias Internos
- `guia_amostras_elevenlabs.md` - Guia para criação de amostras para o ElevenLabs
- `guia_extracao_amostras_audacity.md` - Guia para extração de amostras com Audacity
- `guia_melhorias_baseado_nos_videos.md` - Guia para melhorias baseadas nos vídeos de referência
- `guia_perfil_misto.md` - Guia para criação de perfil de voz misto
- `guia_testes_offline.md` - Guia para testes offline
- `guia_uso_samples_curtos.md` - Guia para uso de amostras curtas
- `guia_uso_samples_elevenlabs.md` - Guia para uso de amostras no ElevenLabs
