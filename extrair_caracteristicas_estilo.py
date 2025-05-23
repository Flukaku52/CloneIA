#!/usr/bin/env python3
"""
Script para extrair características de estilo e comunicação dos vídeos de referência.
"""
import os
import sys
import json
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('extrair_caracteristicas')

def carregar_analises(analysis_dir):
    """
    Carrega as análises de vídeos previamente geradas.
    
    Args:
        analysis_dir: Diretório contendo as análises
        
    Returns:
        dict: Análises carregadas
    """
    try:
        # Carregar resumo
        summary_file = os.path.join(analysis_dir, 'summary.json')
        if not os.path.exists(summary_file):
            logger.error(f"Arquivo de resumo não encontrado: {summary_file}")
            return None
        
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        # Carregar análises individuais
        analyses = {}
        for video in summary.get('videos', []):
            video_name = os.path.splitext(video)[0]
            analysis_file = os.path.join(analysis_dir, video_name, 'analysis.json')
            
            if os.path.exists(analysis_file):
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    analyses[video] = json.load(f)
            else:
                logger.warning(f"Arquivo de análise não encontrado: {analysis_file}")
        
        return analyses
    
    except Exception as e:
        logger.error(f"Erro ao carregar análises: {e}")
        return None

def extrair_caracteristicas_audio(audio_path, output_dir):
    """
    Extrai características do áudio para análise de estilo de fala.
    
    Args:
        audio_path: Caminho para o arquivo de áudio
        output_dir: Diretório de saída para os resultados
        
    Returns:
        dict: Características extraídas
    """
    try:
        # Criar diretório de saída
        os.makedirs(output_dir, exist_ok=True)
        
        # Extrair características de ritmo e entonação
        # Usamos ffprobe para obter informações detalhadas sobre o áudio
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            '-select_streams', 'a',
            audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        audio_info = json.loads(result.stdout)
        
        # Extrair características básicas
        caracteristicas = {
            'audio_path': audio_path,
            'duration_seconds': float(audio_info['format'].get('duration', 0)),
            'bitrate': int(audio_info['format'].get('bit_rate', 0)),
            'sample_rate': int(audio_info['streams'][0].get('sample_rate', 0)),
            'channels': int(audio_info['streams'][0].get('channels', 0)),
            'codec': audio_info['streams'][0].get('codec_name', ''),
            'analyzed_at': datetime.now().isoformat()
        }
        
        # Salvar características em JSON
        output_file = os.path.join(output_dir, 'audio_caracteristicas.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(caracteristicas, f, indent=2)
        
        logger.info(f"Características de áudio extraídas: {output_file}")
        
        return caracteristicas
    
    except Exception as e:
        logger.error(f"Erro ao extrair características de áudio {audio_path}: {e}")
        return None

def extrair_caracteristicas_video(frames_dir, output_dir):
    """
    Extrai características visuais dos frames para análise de estilo.
    
    Args:
        frames_dir: Diretório contendo os frames
        output_dir: Diretório de saída para os resultados
        
    Returns:
        dict: Características extraídas
    """
    try:
        # Criar diretório de saída
        os.makedirs(output_dir, exist_ok=True)
        
        # Listar frames
        frames = [os.path.join(frames_dir, f) for f in os.listdir(frames_dir) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if not frames:
            logger.warning(f"Nenhum frame encontrado em {frames_dir}")
            return None
        
        # Extrair características básicas
        caracteristicas = {
            'frames_dir': frames_dir,
            'num_frames': len(frames),
            'frames': frames,
            'analyzed_at': datetime.now().isoformat()
        }
        
        # Salvar características em JSON
        output_file = os.path.join(output_dir, 'video_caracteristicas.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(caracteristicas, f, indent=2)
        
        logger.info(f"Características de vídeo extraídas: {output_file}")
        
        return caracteristicas
    
    except Exception as e:
        logger.error(f"Erro ao extrair características de vídeo {frames_dir}: {e}")
        return None

def extrair_caracteristicas_estilo(analysis, output_dir):
    """
    Extrai características de estilo de comunicação de um vídeo.
    
    Args:
        analysis: Análise do vídeo
        output_dir: Diretório de saída para os resultados
        
    Returns:
        dict: Características de estilo
    """
    try:
        # Criar diretório de saída
        os.makedirs(output_dir, exist_ok=True)
        
        # Extrair características de áudio
        audio_path = analysis.get('audio')
        audio_caracteristicas = None
        if audio_path and os.path.exists(audio_path):
            audio_output_dir = os.path.join(output_dir, 'audio')
            audio_caracteristicas = extrair_caracteristicas_audio(audio_path, audio_output_dir)
        
        # Extrair características de vídeo
        frames = analysis.get('frames', [])
        frames_dir = os.path.dirname(frames[0]) if frames else None
        video_caracteristicas = None
        if frames_dir and os.path.exists(frames_dir):
            video_output_dir = os.path.join(output_dir, 'video')
            video_caracteristicas = extrair_caracteristicas_video(frames_dir, video_output_dir)
        
        # Combinar características
        estilo = {
            'video_info': analysis.get('video_info', {}),
            'audio_caracteristicas': audio_caracteristicas,
            'video_caracteristicas': video_caracteristicas,
            'analyzed_at': datetime.now().isoformat()
        }
        
        # Salvar características em JSON
        output_file = os.path.join(output_dir, 'estilo.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(estilo, f, indent=2)
        
        logger.info(f"Características de estilo extraídas: {output_file}")
        
        return estilo
    
    except Exception as e:
        logger.error(f"Erro ao extrair características de estilo: {e}")
        return None

def extrair_caracteristicas(analyses, output_dir):
    """
    Extrai características de estilo de todos os vídeos analisados.
    
    Args:
        analyses: Análises dos vídeos
        output_dir: Diretório de saída para os resultados
        
    Returns:
        dict: Resumo das características extraídas
    """
    try:
        # Criar diretório de saída
        os.makedirs(output_dir, exist_ok=True)
        
        # Extrair características de cada vídeo
        caracteristicas = {}
        for video, analysis in analyses.items():
            logger.info(f"Extraindo características de estilo: {video}")
            video_name = os.path.splitext(video)[0]
            video_output_dir = os.path.join(output_dir, video_name)
            estilo = extrair_caracteristicas_estilo(analysis, video_output_dir)
            if estilo:
                caracteristicas[video] = estilo
        
        # Salvar resumo em JSON
        summary = {
            'total_videos': len(analyses),
            'analyzed_videos': len(caracteristicas),
            'videos': list(caracteristicas.keys()),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        summary_file = os.path.join(output_dir, 'estilo_summary.json')
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Extração de características concluída: {summary_file}")
        
        return summary
    
    except Exception as e:
        logger.error(f"Erro ao extrair características: {e}")
        return None

def main():
    """
    Função principal.
    """
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Extrator de características de estilo")
    parser.add_argument("--analysis", help="Diretório contendo as análises de vídeos", 
                        default="analysis/videos")
    parser.add_argument("--output", help="Diretório de saída para os resultados", 
                        default="analysis/estilo")
    parser.add_argument("--debug", action="store_true", help="Ativar modo de depuração")

    args = parser.parse_args()

    # Configurar nível de log
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Carregar análises
    analyses = carregar_analises(args.analysis)
    if not analyses:
        logger.error("Falha ao carregar análises")
        return 1
    
    # Extrair características
    summary = extrair_caracteristicas(analyses, args.output)
    
    if summary:
        logger.info(f"Extração concluída com sucesso: {summary['analyzed_videos']} vídeos analisados")
        return 0
    else:
        logger.error("Falha ao extrair características")
        return 1

if __name__ == "__main__":
    sys.exit(main())
