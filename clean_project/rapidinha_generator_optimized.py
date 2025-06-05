#!/usr/bin/env python3
"""
Script otimizado para gerar vídeos para o quadro Rapidinha Cripto.
Integra a geração de áudio e vídeo em um único fluxo.
"""
import os
import logging
import argparse
import time
from typing import Optional

from core.audio import AudioGenerator
from heygen_video_generator_optimized import HeyGenVideoGenerator
from core.utils import ensure_directory, get_timestamp_filename, optimize_text, PROJECT_ROOT, OUTPUT_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('rapidinha_generator')

def generate_rapidinha(script: str, output_dir: Optional[str] = None, 
                      voice_profile: Optional[str] = None, 
                      avatar_id: Optional[str] = None,
                      voice_id: Optional[str] = None,
                      optimize_speech: bool = True,
                      dry_run: bool = False) -> Optional[str]:
    """
    Gera um vídeo completo para o quadro Rapidinha Cripto.
    
    Args:
        script: Texto do script
        output_dir: Diretório para salvar os arquivos (se None, usa o padrão)
        voice_profile: Perfil de voz a ser usado (se None, usa o padrão)
        avatar_id: ID do avatar a ser usado (se None, usa o configurado)
        voice_id: ID da voz a ser usada (se None, usa o padrão)
        optimize_speech: Se True, otimiza o texto para fala
        dry_run: Se True, simula a geração sem fazer chamadas de API
        
    Returns:
        Optional[str]: Caminho para o vídeo gerado, ou None se falhar
    """
    # Configurar diretório de saída
    if not output_dir:
        output_dir = os.path.join(OUTPUT_DIR, "rapidinha")
    ensure_directory(output_dir)
    
    # Gerar timestamp para os arquivos
    timestamp = int(time.time())
    
    # Inicializar geradores
    audio_generator = AudioGenerator(voice_profile=voice_profile)
    video_generator = HeyGenVideoGenerator()
    
    # Otimizar o script para fala, se solicitado
    if optimize_speech:
        original_script = script
        script = optimize_text(script)
        logger.info(f"Script otimizado: {len(original_script)} chars -> {len(script)} chars")
    
    # Gerar áudio
    logger.info("Gerando áudio...")
    audio_path = os.path.join(output_dir, f"rapidinha_audio_{timestamp}.mp3")
    audio_path = audio_generator.generate_audio(script, audio_path, optimize=False, dry_run=dry_run)
    
    if not audio_path:
        logger.error("Falha ao gerar áudio. Abortando.")
        return None
    
    logger.info(f"Áudio gerado: {audio_path}")
    
    # Gerar vídeo
    if dry_run:
        logger.info("[DRY RUN] Simulando geração de vídeo...")
        video_path = os.path.join(output_dir, f"rapidinha_video_{timestamp}.mp4")
        logger.info(f"[DRY RUN] Vídeo seria salvo em: {video_path}")
        return video_path
    
    logger.info("Gerando vídeo...")
    video_path = os.path.join(output_dir, f"rapidinha_video_{timestamp}.mp4")
    video_path = video_generator.generate_video(
        script=script,
        audio_path=audio_path,
        output_path=video_path,
        avatar_id=avatar_id,
        voice_id=voice_id
    )
    
    if not video_path:
        logger.error("Falha ao gerar vídeo.")
        return None
    
    logger.info(f"Vídeo gerado com sucesso: {video_path}")
    return video_path

def main():
    """
    Função principal para execução via linha de comando.
    """
    parser = argparse.ArgumentParser(description="Gerador de vídeos para o quadro Rapidinha Cripto")
    parser.add_argument("--script", help="Texto do script ou caminho para arquivo de script")
    parser.add_argument("--voice-profile", help="Perfil de voz a ser usado")
    parser.add_argument("--avatar-id", help="ID do avatar a ser usado")
    parser.add_argument("--voice-id", help="ID da voz a ser usada")
    parser.add_argument("--no-optimize", action="store_true", help="Não otimizar o texto para fala")
    parser.add_argument("--dry-run", action="store_true", help="Simular a geração sem fazer chamadas de API")
    
    args = parser.parse_args()
    
    # Obter o script
    script = args.script
    
    # Se o script não foi fornecido, usar um script de exemplo
    if not script:
        script = """
        E aí cambada! Tô de volta na área e bora de Rapidinha! Hoje vamos falar sobre as últimas novidades do mundo cripto.
        
        Primeiro, o Bitcoin continua bombando e atingiu um novo recorde de preço, chegando a mais de 60 mil dólares!
        
        Segundo, o Ethereum também tá em alta com a implementação do EIP-1559 que promete reduzir as taxas de transação.
        
        E por último, mas não menos importante, as NFTs continuam fazendo sucesso com vendas milionárias de arte digital.
        
        E aí, o que você achou dessas notícias? Deixa seu comentário e não esquece de dar aquele like!
        """
    # Se o script é um caminho para arquivo, ler o conteúdo
    elif os.path.exists(script):
        with open(script, 'r', encoding='utf-8') as f:
            script = f.read()
    
    # Gerar o vídeo
    video_path = generate_rapidinha(
        script=script,
        voice_profile=args.voice_profile,
        avatar_id=args.avatar_id,
        voice_id=args.voice_id,
        optimize_speech=not args.no_optimize,
        dry_run=args.dry_run
    )
    
    if video_path:
        logger.info(f"Processo concluído com sucesso! Vídeo salvo em: {video_path}")
    else:
        logger.error("Falha ao gerar o vídeo.")

if __name__ == "__main__":
    main()
