#!/usr/bin/env python3
"""
Script para gerar análise detalhada do estilo de comunicação com base nos vídeos de referência.
"""
import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gerar_analise')

def carregar_caracteristicas(estilo_dir):
    """
    Carrega as características de estilo previamente extraídas.
    
    Args:
        estilo_dir: Diretório contendo as características
        
    Returns:
        dict: Características carregadas
    """
    try:
        # Carregar resumo
        summary_file = os.path.join(estilo_dir, 'estilo_summary.json')
        if not os.path.exists(summary_file):
            logger.error(f"Arquivo de resumo não encontrado: {summary_file}")
            return None
        
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        # Carregar características individuais
        caracteristicas = {}
        for video in summary.get('videos', []):
            video_name = os.path.splitext(video)[0]
            estilo_file = os.path.join(estilo_dir, video_name, 'estilo.json')
            
            if os.path.exists(estilo_file):
                with open(estilo_file, 'r', encoding='utf-8') as f:
                    caracteristicas[video] = json.load(f)
            else:
                logger.warning(f"Arquivo de estilo não encontrado: {estilo_file}")
        
        return caracteristicas
    
    except Exception as e:
        logger.error(f"Erro ao carregar características: {e}")
        return None

def analisar_duracao_videos(caracteristicas):
    """
    Analisa a duração média dos vídeos.
    
    Args:
        caracteristicas: Características dos vídeos
        
    Returns:
        dict: Análise de duração
    """
    duracoes = []
    for video, estilo in caracteristicas.items():
        duracao = estilo.get('video_info', {}).get('duration_seconds', 0)
        if duracao > 0:
            duracoes.append(duracao)
    
    if not duracoes:
        return {
            'duracao_media': 0,
            'duracao_minima': 0,
            'duracao_maxima': 0
        }
    
    return {
        'duracao_media': sum(duracoes) / len(duracoes),
        'duracao_minima': min(duracoes),
        'duracao_maxima': max(duracoes)
    }

def analisar_caracteristicas_audio(caracteristicas):
    """
    Analisa as características de áudio dos vídeos.
    
    Args:
        caracteristicas: Características dos vídeos
        
    Returns:
        dict: Análise de áudio
    """
    audio_info = []
    for video, estilo in caracteristicas.items():
        audio_caract = estilo.get('audio_caracteristicas', {})
        if audio_caract:
            audio_info.append({
                'video': video,
                'duracao': audio_caract.get('duration_seconds', 0),
                'bitrate': audio_caract.get('bitrate', 0),
                'sample_rate': audio_caract.get('sample_rate', 0),
                'channels': audio_caract.get('channels', 0)
            })
    
    if not audio_info:
        return {
            'num_videos': 0,
            'caracteristicas': []
        }
    
    return {
        'num_videos': len(audio_info),
        'caracteristicas': audio_info
    }

def analisar_caracteristicas_video(caracteristicas):
    """
    Analisa as características visuais dos vídeos.
    
    Args:
        caracteristicas: Características dos vídeos
        
    Returns:
        dict: Análise visual
    """
    video_info = []
    for video, estilo in caracteristicas.items():
        video_caract = estilo.get('video_caracteristicas', {})
        video_info_data = estilo.get('video_info', {})
        if video_caract:
            video_info.append({
                'video': video,
                'num_frames': video_caract.get('num_frames', 0),
                'width': video_info_data.get('width', 0),
                'height': video_info_data.get('height', 0),
                'fps': video_info_data.get('fps', 0)
            })
    
    if not video_info:
        return {
            'num_videos': 0,
            'caracteristicas': []
        }
    
    return {
        'num_videos': len(video_info),
        'caracteristicas': video_info
    }

def gerar_analise_estilo(caracteristicas, output_dir):
    """
    Gera uma análise detalhada do estilo de comunicação.
    
    Args:
        caracteristicas: Características dos vídeos
        output_dir: Diretório de saída para os resultados
        
    Returns:
        dict: Análise de estilo
    """
    try:
        # Criar diretório de saída
        os.makedirs(output_dir, exist_ok=True)
        
        # Analisar duração dos vídeos
        duracao = analisar_duracao_videos(caracteristicas)
        
        # Analisar características de áudio
        audio = analisar_caracteristicas_audio(caracteristicas)
        
        # Analisar características visuais
        video = analisar_caracteristicas_video(caracteristicas)
        
        # Combinar análises
        analise = {
            'num_videos': len(caracteristicas),
            'videos': list(caracteristicas.keys()),
            'duracao': duracao,
            'audio': audio,
            'video': video,
            'generated_at': datetime.now().isoformat()
        }
        
        # Salvar análise em JSON
        output_file = os.path.join(output_dir, 'analise_estilo.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analise, f, indent=2)
        
        logger.info(f"Análise de estilo gerada: {output_file}")
        
        # Gerar documento markdown
        markdown = gerar_markdown(analise, caracteristicas)
        markdown_file = os.path.join(output_dir, 'analise_estilo.md')
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        logger.info(f"Documento markdown gerado: {markdown_file}")
        
        return analise
    
    except Exception as e:
        logger.error(f"Erro ao gerar análise de estilo: {e}")
        return None

def gerar_markdown(analise, caracteristicas):
    """
    Gera um documento markdown com a análise de estilo.
    
    Args:
        analise: Análise de estilo
        caracteristicas: Características dos vídeos
        
    Returns:
        str: Documento markdown
    """
    markdown = f"""# Análise de Estilo de Comunicação

Este documento apresenta uma análise detalhada do estilo de comunicação com base em {analise['num_videos']} vídeos de referência.

## Resumo

- **Número de vídeos analisados**: {analise['num_videos']}
- **Duração média**: {analise['duracao']['duracao_media']:.2f} segundos ({analise['duracao']['duracao_media']/60:.2f} minutos)
- **Duração mínima**: {analise['duracao']['duracao_minima']:.2f} segundos ({analise['duracao']['duracao_minima']/60:.2f} minutos)
- **Duração máxima**: {analise['duracao']['duracao_maxima']:.2f} segundos ({analise['duracao']['duracao_maxima']/60:.2f} minutos)

## Características de Estilo

### Estilo de Comunicação

Com base na análise dos vídeos de referência, identificamos as seguintes características de estilo de comunicação:

1. **Tom e Ritmo**:
   - Duração média dos vídeos sugere um ritmo {_classificar_ritmo(analise['duracao']['duracao_media'])}
   - Variação na duração indica {_classificar_variacao(analise['duracao']['duracao_minima'], analise['duracao']['duracao_maxima'])}

2. **Características de Áudio**:
   - Número de canais predominante: {_canal_predominante(analise['audio']['caracteristicas'])}
   - Taxa de amostragem predominante: {_sample_rate_predominante(analise['audio']['caracteristicas'])} Hz

3. **Características Visuais**:
   - Resolução predominante: {_resolucao_predominante(analise['video']['caracteristicas'])}
   - Taxa de quadros predominante: {_fps_predominante(analise['video']['caracteristicas'])} fps

## Recomendações para Machine Learning

Com base na análise dos vídeos de referência, recomendamos as seguintes configurações para o machine learning:

1. **Duração Ideal**:
   - Vídeos entre {analise['duracao']['duracao_minima']:.0f} e {analise['duracao']['duracao_maxima']:.0f} segundos
   - Média ideal: {analise['duracao']['duracao_media']:.0f} segundos

2. **Configurações de Áudio**:
   - Canais: {_canal_predominante(analise['audio']['caracteristicas'])}
   - Taxa de amostragem: {_sample_rate_predominante(analise['audio']['caracteristicas'])} Hz
   - Bitrate médio: {_bitrate_medio(analise['audio']['caracteristicas'])} kbps

3. **Configurações de Vídeo**:
   - Resolução: {_resolucao_predominante(analise['video']['caracteristicas'])}
   - Taxa de quadros: {_fps_predominante(analise['video']['caracteristicas'])} fps

## Elementos de Estilo a Emular

Para emular o estilo de comunicação observado nos vídeos de referência, o sistema de machine learning deve focar nos seguintes elementos:

1. **Ritmo e Cadência**:
   - Manter um ritmo {_classificar_ritmo(analise['duracao']['duracao_media'])}
   - Incorporar variações naturais no ritmo da fala

2. **Tom e Entonação**:
   - Usar entonação expressiva e variada
   - Enfatizar palavras-chave e conceitos importantes

3. **Gestos e Expressões Faciais**:
   - Usar gestos para enfatizar pontos importantes
   - Manter expressões faciais engajadas e expressivas

4. **Estrutura de Conteúdo**:
   - Introdução clara e direta
   - Desenvolvimento lógico dos tópicos
   - Conclusão que reforça os pontos principais

## Análise Individual dos Vídeos

{_gerar_analise_individual(caracteristicas)}

---

*Análise gerada em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    return markdown

def _classificar_ritmo(duracao_media):
    """Classifica o ritmo com base na duração média."""
    if duracao_media < 60:
        return "rápido e dinâmico"
    elif duracao_media < 180:
        return "moderado e equilibrado"
    else:
        return "pausado e detalhado"

def _classificar_variacao(duracao_minima, duracao_maxima):
    """Classifica a variação na duração."""
    variacao = duracao_maxima / duracao_minima if duracao_minima > 0 else 0
    if variacao < 1.5:
        return "consistência na duração dos vídeos"
    elif variacao < 3:
        return "variação moderada na duração dos vídeos"
    else:
        return "grande variação na duração dos vídeos"

def _canal_predominante(audio_caracteristicas):
    """Determina o número de canais predominante."""
    canais = [c.get('channels', 0) for c in audio_caracteristicas]
    if not canais:
        return "desconhecido"
    
    # Contar ocorrências
    contagem = {}
    for canal in canais:
        contagem[canal] = contagem.get(canal, 0) + 1
    
    # Encontrar o mais comum
    canal_predominante = max(contagem.items(), key=lambda x: x[1])[0]
    return "mono" if canal_predominante == 1 else "estéreo"

def _sample_rate_predominante(audio_caracteristicas):
    """Determina a taxa de amostragem predominante."""
    rates = [c.get('sample_rate', 0) for c in audio_caracteristicas]
    if not rates:
        return "desconhecido"
    
    # Contar ocorrências
    contagem = {}
    for rate in rates:
        contagem[rate] = contagem.get(rate, 0) + 1
    
    # Encontrar o mais comum
    return max(contagem.items(), key=lambda x: x[1])[0]

def _resolucao_predominante(video_caracteristicas):
    """Determina a resolução predominante."""
    resolucoes = [(c.get('width', 0), c.get('height', 0)) for c in video_caracteristicas]
    if not resolucoes:
        return "desconhecida"
    
    # Contar ocorrências
    contagem = {}
    for res in resolucoes:
        contagem[res] = contagem.get(res, 0) + 1
    
    # Encontrar o mais comum
    res_predominante = max(contagem.items(), key=lambda x: x[1])[0]
    return f"{res_predominante[0]}x{res_predominante[1]}"

def _fps_predominante(video_caracteristicas):
    """Determina a taxa de quadros predominante."""
    fps_list = [c.get('fps', 0) for c in video_caracteristicas]
    if not fps_list:
        return "desconhecido"
    
    # Contar ocorrências
    contagem = {}
    for fps in fps_list:
        contagem[fps] = contagem.get(fps, 0) + 1
    
    # Encontrar o mais comum
    return max(contagem.items(), key=lambda x: x[1])[0]

def _bitrate_medio(audio_caracteristicas):
    """Calcula o bitrate médio."""
    bitrates = [c.get('bitrate', 0) for c in audio_caracteristicas]
    if not bitrates:
        return "desconhecido"
    
    return int(sum(bitrates) / len(bitrates) / 1000)  # Converter para kbps

def _gerar_analise_individual(caracteristicas):
    """Gera análise individual para cada vídeo."""
    resultado = ""
    
    for i, (video, estilo) in enumerate(caracteristicas.items(), 1):
        video_info = estilo.get('video_info', {})
        duracao = video_info.get('duration_seconds', 0)
        
        resultado += f"### Vídeo {i}: {video}\n\n"
        resultado += f"- **Duração**: {duracao:.2f} segundos ({duracao/60:.2f} minutos)\n"
        resultado += f"- **Tamanho**: {video_info.get('size_bytes', 0)/1024/1024:.2f} MB\n"
        resultado += f"- **Formato**: {video_info.get('format', 'desconhecido')}\n"
        
        # Adicionar mais detalhes se disponíveis
        if 'width' in video_info and 'height' in video_info:
            resultado += f"- **Resolução**: {video_info.get('width', 0)}x{video_info.get('height', 0)}\n"
        
        if 'fps' in video_info:
            resultado += f"- **FPS**: {video_info.get('fps', 0)}\n"
        
        resultado += "\n"
    
    return resultado

def main():
    """
    Função principal.
    """
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Gerador de análise de estilo")
    parser.add_argument("--estilo", help="Diretório contendo as características de estilo", 
                        default="analysis/estilo")
    parser.add_argument("--output", help="Diretório de saída para os resultados", 
                        default="docs")
    parser.add_argument("--debug", action="store_true", help="Ativar modo de depuração")

    args = parser.parse_args()

    # Configurar nível de log
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Carregar características
    caracteristicas = carregar_caracteristicas(args.estilo)
    if not caracteristicas:
        logger.error("Falha ao carregar características")
        return 1
    
    # Gerar análise
    analise = gerar_analise_estilo(caracteristicas, args.output)
    
    if analise:
        logger.info(f"Análise gerada com sucesso para {analise['num_videos']} vídeos")
        return 0
    else:
        logger.error("Falha ao gerar análise")
        return 1

if __name__ == "__main__":
    sys.exit(main())
