# Integração com HeyGen para o Clone Rapidinha no Cripto

Este guia explica como usar a integração com o HeyGen para criar vídeos com um clone visual para o quadro "Rapidinha no Cripto".

## O que é o HeyGen?

HeyGen é uma plataforma de síntese de vídeo que permite criar vídeos realistas de avatares falando. Com o HeyGen, você pode criar um clone visual que imita seus gestos, expressões faciais e movimentos labiais.

## Pré-requisitos

1. Conta no HeyGen: Crie uma conta em [heygen.com](https://www.heygen.com)
2. Chave de API: Obtenha uma chave de API no painel de desenvolvedor do HeyGen
3. Vídeo de referência: Um vídeo seu apresentando o quadro "Rapidinha no Cripto"

## Configuração

1. Adicione sua chave de API do HeyGen ao arquivo `.env`:
   ```
   HEYGEN_API_KEY=sua_chave_heygen_aqui
   ```

2. Crie um avatar usando um vídeo de referência:
   ```
   python rapidinha_heygen_creator.py avatar --create --video caminho/para/seu/video.mp4
   ```

## Uso

### Listar avatares disponíveis

```
python rapidinha_heygen_creator.py avatar --list
```

### Criar um novo avatar

```
python rapidinha_heygen_creator.py avatar --create --video caminho/para/seu/video.mp4 --name "Meu Avatar"
```

### Gerar um vídeo completo

```
python rapidinha_heygen_creator.py create
```

### Gerar um vídeo com notícias simuladas

```
python rapidinha_heygen_creator.py create --mock
```

### Listar vídeos gerados anteriormente

```
python rapidinha_heygen_creator.py list
```

## Como funciona

1. **Geração de script**: O sistema coleta notícias e gera um script no seu estilo de comunicação
2. **Geração de áudio**: O script é convertido em áudio usando a API da ElevenLabs
3. **Geração de vídeo**: O HeyGen cria um vídeo com seu avatar falando o conteúdo do script

## Dicas para melhores resultados

1. **Vídeo de referência**: Use um vídeo de boa qualidade, bem iluminado e com áudio claro
2. **Duração do vídeo**: O vídeo de referência deve ter pelo menos 30 segundos
3. **Posição da câmera**: Grave o vídeo de frente, com seu rosto bem visível
4. **Áudio**: Fale claramente e evite ruídos de fundo

## Limitações

- O HeyGen tem limites de uso dependendo do seu plano
- A geração de vídeos pode levar alguns minutos
- A qualidade do avatar depende da qualidade do vídeo de referência

## Solução de problemas

- **Erro de autenticação**: Verifique se a chave de API está correta no arquivo `.env`
- **Falha na criação do avatar**: Verifique se o vídeo de referência atende aos requisitos do HeyGen
- **Vídeo sem áudio**: Verifique se o áudio foi gerado corretamente pela API da ElevenLabs
