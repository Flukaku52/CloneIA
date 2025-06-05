# Guia para Testar o Sistema sem Consumir Créditos do ElevenLabs

Este guia explica como testar todos os aspectos do sistema de geração de áudio e vídeo sem consumir créditos do ElevenLabs.

## 1. Modo de Simulação (Dry Run)

Todos os scripts que interagem com o ElevenLabs incluem um modo de simulação que mostra exatamente o que seria feito, mas não faz nenhuma chamada à API:

### Testar a Geração de Áudio

```bash
python test_flukaku_voice.py --dry-run
```

### Testar a Criação do Perfil Misto

```bash
python create_mixed_voice_profile.py --dry-run
```

### Testar com Diferentes Perfis

```bash
# Testar com o perfil FlukakuSampleFree
python test_flukaku_voice.py --profile flukakusamplefree --dry-run

# Testar com o perfil FlukakuIA
python test_flukaku_voice.py --profile flukakuia --dry-run

# Testar com o perfil misto
python test_flukaku_voice.py --profile mix --dry-run
```

## 2. Teste Offline Completo

O script `test_offline.py` simula o fluxo completo de geração de áudio e vídeo sem fazer nenhuma chamada à API:

```bash
# Testar com o texto padrão
python test_offline.py

# Testar com um texto personalizado
python test_offline.py --text "E aí cambada! Vamos falar sobre o Bitcoin hoje!"

# Testar com um arquivo de script
python test_offline.py --script scripts/exemplo_natural.txt

# Testar com um perfil específico
python test_offline.py --profile flukakuia
```

Este script:
1. Otimiza o texto para fala natural
2. Carrega a configuração do perfil de voz especificado
3. Simula a geração de áudio (copiando um arquivo de amostra existente)
4. Simula a geração de vídeo
5. Exibe um resumo detalhado do processo

## 3. Testar a Otimização de Texto

O script `test_text_optimization.py` permite testar apenas a otimização de texto, que é uma parte importante do processo:

```bash
# Testar com o texto padrão
python test_text_optimization.py

# Testar com um texto personalizado
python test_text_optimization.py --text "E aí cambada! Vamos falar sobre o Bitcoin hoje!"

# Testar com um arquivo de texto
python test_text_optimization.py --file scripts/exemplo_natural.txt

# Salvar o resultado em um arquivo específico
python test_text_optimization.py --output meu_texto_otimizado.txt
```

Este script:
1. Carrega o texto de entrada
2. Aplica todas as otimizações (remoção de pontuação, substituição de termos, etc.)
3. Exibe o texto original e o texto otimizado lado a lado
4. Salva o resultado em um arquivo para referência futura

## 4. Comparar Perfis de Voz

O script `compare_voice_profiles.py` permite comparar os diferentes perfis de voz disponíveis:

```bash
# Comparar todos os perfis
python compare_voice_profiles.py

# Comparar perfis específicos
python compare_voice_profiles.py --profiles flukakusamplefree flukakuia

# Exibir o resultado em formato JSON
python compare_voice_profiles.py --format json
```

Este script:
1. Carrega a configuração de cada perfil
2. Exibe uma tabela comparativa com os parâmetros de cada perfil
3. Fornece observações sobre as diferenças entre os perfis

## 5. Verificar a Configuração Atual

O script `switch_voice_profile.py` permite verificar a configuração atual sem fazer alterações:

```bash
# Listar perfis disponíveis
python switch_voice_profile.py --list

# Verificar perfil atual
python switch_voice_profile.py --current
```

## 6. Testar a Geração de Vídeo com Áudio Existente

Você pode testar a geração de vídeo usando um arquivo de áudio existente:

```bash
# Usar um arquivo de áudio existente
python generate_test_video_augment.py --audio reference/samples/sample_audio.mp3
```

## Dicas para Testes Eficientes

1. **Comece com Textos Curtos**: Use textos curtos para testes iniciais
2. **Teste Diferentes Formatos de Texto**: Experimente diferentes estilos de formatação
3. **Compare os Resultados**: Use os scripts de comparação para entender as diferenças entre perfis
4. **Verifique a Otimização de Texto**: A otimização de texto é crucial para a qualidade da fala
5. **Mantenha um Registro**: Salve os resultados dos testes para referência futura

## Quando Usar Créditos do ElevenLabs

Quando seus créditos do ElevenLabs forem renovados, você pode:

1. **Criar o Perfil Misto Real**: Execute `python create_mixed_voice_profile.py` para criar o perfil misto com todas as amostras
2. **Testar com Textos Reais**: Gere áudio para scripts reais que você usará em seus vídeos
3. **Comparar Perfis Reais**: Compare os resultados dos diferentes perfis para escolher o melhor

## Conclusão

Com estes scripts e técnicas, você pode testar e refinar todo o sistema sem consumir créditos do ElevenLabs. Quando seus créditos forem renovados, você estará pronto para gerar conteúdo de alta qualidade com configurações já otimizadas.
