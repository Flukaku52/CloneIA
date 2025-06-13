# 🚀 COMANDOS RÁPIDOS - SISTEMA IA CRIPTO

## 📊 MONITORAR NOTÍCIAS

### Verificar uma vez:
```bash
python ia_system/automation/monitor_noticias.py
```

### Monitoramento contínuo (15 min):
```bash
python ia_system/automation/monitor_noticias.py --continuo
```

### Monitoramento rápido (5 min):
```bash
python ia_system/automation/monitor_noticias.py --continuo --intervalo 5
```

### Usar menu interativo:
```bash
python monitorar.py
```

## 🎬 GERAR ROTEIRO E REEL

### Gerar roteiro automático:
```bash
python ia_system/core/script_generator.py
```

### Pipeline completo (roteiro + áudio + vídeo):
```bash
export ELEVENLABS_API_KEY="sk_d4e4dde07c2c95dac15248131f2781ef15b5781579b75527"
export HEYGEN_API_KEY="OGU5OTA4MGFhMTZkNDExNDhmNmZlNGI1ODY2ZDNhNGUtMTc0NzE5OTM4Mg=="
python ia_system/automation/pipeline.py
```

## 🔍 FUNCIONALIDADES

### Ver avatares disponíveis:
```bash
python gerenciar_avatares.py listar
```

### Rotacionar avatar:
```bash
python gerenciar_avatares.py proximo
```

### Testar coletor Twitter:
```bash
python ia_system/core/twitter_collector.py
```

### Limpar outputs:
```bash
python limpar_outputs.py
```

## 📈 STATUS DO SISTEMA

### Pipeline completo mostra:
- ✅ APIs configuradas
- 🎭 Avatares disponíveis  
- 🐦 Twitter + Portais integrados
- 📊 Verificação cruzada ativa

## 💡 DICAS

1. **Notícias de alta prioridade**: Palavras como "urgente", "oficial", "banco central", "aprovado"
2. **Roteiro automático**: 2-3 minutos com 2-4 notícias verificadas
3. **Avatares**: Rotação automática entre 5 disponíveis
4. **Formato**: Sempre portrait (9:16) para reels

---
*Sistema pronto para monitorar e gerar reels automaticamente!* 🚀