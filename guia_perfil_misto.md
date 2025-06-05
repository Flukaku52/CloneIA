# Guia para Usar o Perfil de Voz Misto (FlukakuMix)

Este guia explica como usar o novo perfil de voz misto que combina as amostras dos perfis "FlukakuSampleFree" e "FlukakuIA" para obter uma voz mais completa e embasada.

## O Que é o Perfil Misto?

O perfil misto "FlukakuMix" é uma combinação dos seus dois perfis de voz existentes:
- **FlukakuSampleFree** (24 amostras)
- **FlukakuIA** 

Ao combinar as amostras de ambos os perfis, obtemos uma voz mais rica e natural, que captura melhor seu estilo de fala.

## Como Criar o Perfil Misto

Quando seus créditos do ElevenLabs forem renovados, você pode criar o perfil misto executando o seguinte comando:

```bash
python create_mixed_voice_profile.py
```

Este script irá:
1. Baixar todas as amostras de áudio dos dois perfis
2. Criar um novo perfil de voz no ElevenLabs com todas as amostras combinadas
3. Configurar o sistema para usar o novo perfil misto por padrão

## Como Usar o Perfil Misto

O perfil misto já está configurado como o perfil padrão do sistema. Isso significa que todos os scripts de geração de áudio e vídeo usarão automaticamente o perfil misto.

### Gerar Áudio com o Perfil Misto

```bash
python test_flukaku_voice.py
```

### Gerar Vídeo com o Perfil Misto

```bash
python generate_test_video_augment.py
```

## Como Alternar entre Perfis

Se você quiser alternar entre diferentes perfis de voz, use o script `switch_voice_profile.py`:

### Listar Perfis Disponíveis

```bash
python switch_voice_profile.py --list
```

### Verificar Perfil Atual

```bash
python switch_voice_profile.py --current
```

### Alternar para o Perfil Misto

```bash
python switch_voice_profile.py --switch mix
```

### Alternar para o Perfil FlukakuSampleFree

```bash
python switch_voice_profile.py --switch flukakusamplefree
```

### Alternar para o Perfil FlukakuIA

```bash
python switch_voice_profile.py --switch flukakuia
```

## Testar sem Consumir Créditos

Para testar a configuração sem consumir créditos do ElevenLabs, use a opção `--dry-run`:

```bash
python test_flukaku_voice.py --dry-run
```

## Parâmetros Otimizados

O perfil misto usa os seguintes parâmetros otimizados:

```json
{
    "stability": 0.05,          // Estabilidade mínima para máxima expressividade
    "similarity_boost": 0.80,    // Reduzida para mais naturalidade e velocidade
    "style": 1.0,               // Máximo estilo para capturar a entonação carioca
    "use_speaker_boost": true,   // Melhorar a qualidade do áudio
    "model_id": "eleven_multilingual_v2"  // Modelo multilíngue avançado
}
```

Estes parâmetros foram otimizados para:
- Maximizar a fluidez e naturalidade da fala
- Reduzir pausas artificiais
- Manter seu estilo energético e expressivo
- Capturar seu sotaque carioca

## Dicas para Melhores Resultados

1. **Formatação de Texto Otimizada**:
   - Remova pontuação que causa pausas
   - Use maiúsculas para palavras enfatizadas (ex: "BOMBANDO")
   - Adapte termos técnicos (ex: "Bitcoim" em vez de "Bitcoin")
   - Junte palavras em expressões características (ex: "EAÍCAMBADA")

2. **Segmentação de Textos Longos**:
   - Divida textos longos em segmentos menores
   - Gere vídeos separados para cada segmento
   - Una os vídeos no CapCut

3. **Amostras Adicionais**:
   - Continue adicionando amostras de alta qualidade aos perfis
   - Recrie o perfil misto periodicamente para incluir novas amostras

## Próximos Passos

1. **Criar o Perfil Misto Real**:
   - Quando seus créditos do ElevenLabs forem renovados, execute `python create_mixed_voice_profile.py`
   - Isso criará o perfil misto real com todas as amostras combinadas

2. **Testar e Refinar**:
   - Teste o perfil misto com diferentes textos
   - Ajuste os parâmetros conforme necessário
   - Compare com os perfis individuais para verificar a melhoria

3. **Adicionar Novas Amostras**:
   - Use os samples curtos (7-12 segundos) que extraímos
   - Adicione-os ao perfil misto para melhorar ainda mais a qualidade

Seguindo este guia, você obterá uma voz mais natural, fluida e expressiva para seus vídeos de "Rapidinha Cripto".
