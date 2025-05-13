#!/usr/bin/env python3
"""
Script para gerar um vídeo Rapidinha completo, desde a busca de notícias até o vídeo final.
"""
import os
import sys
import logging
import argparse
from datetime import datetime
from typing import Optional, Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('rapidinha_completa')

# Verificar dependências
try:
    from core.gerador_script import GeradorScript
    from core.content_manager import ContentManager
except ImportError as e:
    logger.error(f"Erro ao importar módulos necessários: {e}")
    logger.error("Verifique se os arquivos estão no diretório correto.")
    sys.exit(1)

def verificar_apis():
    """
    Verifica se as APIs necessárias estão configuradas.

    Returns:
        bool: True se todas as APIs estão configuradas, False caso contrário
    """
    # Verificar API do ElevenLabs
    elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not elevenlabs_api_key:
        logger.warning("API key do ElevenLabs não encontrada. Usando modo de simulação.")
        return False

    # Verificar API do HeyGen
    heygen_api_key = os.environ.get("HEYGEN_API_KEY")
    if not heygen_api_key:
        logger.warning("API key do HeyGen não encontrada. Usando modo de simulação.")
        return False

    logger.info("APIs configuradas corretamente.")
    return True

def criar_diretorios():
    """
    Cria os diretórios necessários para o projeto.
    """
    diretorios = [
        "scripts",
        "output",
        "output/audio",
        "output/videos"
    ]

    for diretorio in diretorios:
        os.makedirs(diretorio, exist_ok=True)
        logger.debug(f"Diretório criado/verificado: {diretorio}")

def gerar_script(dias_max: int = 7, num_noticias: int = 2, num_tweets: int = 1) -> Optional[str]:
    """
    Gera um script para o vídeo Rapidinha.

    Args:
        dias_max: Número máximo de dias de antiguidade das notícias
        num_noticias: Número de notícias a incluir
        num_tweets: Número de tweets a incluir

    Returns:
        Optional[str]: Script gerado ou None se falhar
    """
    logger.info(f"Gerando script com {num_noticias} notícias e {num_tweets} tweets...")

    try:
        # Inicializar o gerador de scripts
        gerador = GeradorScript(dias_max=dias_max)

        # Gerar o script
        script = gerador.gerar_script(num_noticias=num_noticias, num_tweets=num_tweets)

        if not script:
            logger.error("Falha ao gerar o script.")
            return None

        # Salvar o script em um arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_path = os.path.join("scripts", f"rapidinha_script_{timestamp}.txt")

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script)

        logger.info(f"Script salvo em: {script_path}")
        return script_path

    except Exception as e:
        logger.error(f"Erro ao gerar script: {e}")
        return None

def gerar_audio(script_path: str, dry_run: bool = False) -> Optional[str]:
    """
    Gera o áudio para o script usando o ElevenLabs.

    Args:
        script_path: Caminho para o arquivo de script
        dry_run: Se True, simula a geração sem fazer chamadas de API

    Returns:
        Optional[str]: Caminho para o arquivo de áudio ou None se falhar
    """
    logger.info(f"Gerando áudio para o script: {script_path}")

    if dry_run:
        logger.info("[SIMULAÇÃO] Gerando áudio...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = os.path.join("output", "audio", f"rapidinha_audio_{timestamp}.mp3")
        logger.info(f"[SIMULAÇÃO] Áudio seria salvo em: {audio_path}")
        return audio_path

    try:
        # Importar o gerador de vídeo de reels
        from generate_reel_video import ReelVideoGenerator

        # Inicializar o gerador
        generator = ReelVideoGenerator()

        # Gerar o áudio
        audio_path = generator.generate_reel_audio(script_path, optimize=True)

        if not audio_path:
            logger.error("Falha ao gerar o áudio.")
            return None

        logger.info(f"Áudio gerado com sucesso: {audio_path}")
        return audio_path

    except Exception as e:
        logger.error(f"Erro ao gerar áudio: {e}")
        return None

def gerar_video(audio_path: str, dry_run: bool = False) -> Optional[str]:
    """
    Gera o vídeo para o áudio usando o HeyGen.

    Args:
        audio_path: Caminho para o arquivo de áudio
        dry_run: Se True, simula a geração sem fazer chamadas de API

    Returns:
        Optional[str]: Caminho para o arquivo de vídeo ou None se falhar
    """
    logger.info(f"Gerando vídeo para o áudio: {audio_path}")

    if dry_run:
        logger.info("[SIMULAÇÃO] Gerando vídeo...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = os.path.join("output", "videos", f"rapidinha_video_{timestamp}.mp4")
        logger.info(f"[SIMULAÇÃO] Vídeo seria salvo em: {video_path}")
        return video_path

    try:
        # Importar o gerador de vídeo de reels
        from generate_reel_video import ReelVideoGenerator

        # Inicializar o gerador
        generator = ReelVideoGenerator()

        # Gerar o vídeo
        video_path = generator.generate_reel_video(audio_path, folder_name="rapidinha")

        if not video_path:
            logger.error("Falha ao gerar o vídeo.")
            return None

        logger.info(f"Vídeo gerado com sucesso: {video_path}")
        return video_path

    except Exception as e:
        logger.error(f"Erro ao gerar vídeo: {e}")
        return None

def abrir_arquivo(file_path: str) -> bool:
    """
    Abre um arquivo com o aplicativo padrão do sistema.

    Args:
        file_path: Caminho para o arquivo

    Returns:
        bool: True se bem-sucedido, False caso contrário
    """
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return False

    try:
        import platform
        import subprocess

        system = platform.system()

        if system == "Darwin":  # macOS
            subprocess.call(["open", file_path])
        elif system == "Windows":
            subprocess.call(["start", file_path], shell=True)
        else:  # Linux e outros
            subprocess.call(["xdg-open", file_path])

        logger.info(f"Arquivo aberto: {file_path}")
        return True

    except Exception as e:
        logger.error(f"Erro ao abrir arquivo: {e}")
        return False

def gerar_rapidinha_completa(dias_max: int = 7, num_noticias: int = 2, num_tweets: int = 1,
                           dry_run: bool = False, abrir_resultado: bool = True) -> Dict[str, Any]:
    """
    Gera um vídeo Rapidinha completo, desde a busca de notícias até o vídeo final.

    Args:
        dias_max: Número máximo de dias de antiguidade das notícias
        num_noticias: Número de notícias a incluir
        num_tweets: Número de tweets a incluir
        dry_run: Se True, simula a geração sem fazer chamadas de API
        abrir_resultado: Se True, abre os arquivos gerados

    Returns:
        Dict[str, Any]: Dicionário com os caminhos dos arquivos gerados
    """
    # Criar diretórios necessários
    criar_diretorios()

    # Verificar APIs (se não for dry_run)
    if not dry_run:
        apis_ok = verificar_apis()
        if not apis_ok:
            logger.warning("APIs não configuradas. Usando modo de simulação.")
            dry_run = True

    # Gerar script
    script_path = gerar_script(dias_max, num_noticias, num_tweets)
    if not script_path:
        return {"status": "error", "message": "Falha ao gerar script"}

    # Abrir o script se solicitado
    if abrir_resultado:
        abrir_arquivo(script_path)

    # Gerar áudio
    audio_path = gerar_audio(script_path, dry_run)
    if not audio_path:
        return {"status": "error", "message": "Falha ao gerar áudio", "script_path": script_path}

    # Gerar vídeo
    video_path = gerar_video(audio_path, dry_run)
    if not video_path:
        return {"status": "error", "message": "Falha ao gerar vídeo",
                "script_path": script_path, "audio_path": audio_path}

    # Abrir o vídeo se solicitado
    if abrir_resultado and not dry_run:
        abrir_arquivo(video_path)

    return {
        "status": "success",
        "script_path": script_path,
        "audio_path": audio_path,
        "video_path": video_path,
        "dry_run": dry_run
    }

def main():
    """
    Função principal.
    """
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Gerador de vídeos Rapidinha")
    parser.add_argument("--dias", type=int, default=7, help="Número máximo de dias de antiguidade das notícias")
    parser.add_argument("--noticias", type=int, default=2, help="Número de notícias a incluir")
    parser.add_argument("--tweets", type=int, default=1, help="Número de tweets a incluir")
    parser.add_argument("--script", type=str, help="Caminho para um script existente (opcional)")
    parser.add_argument("--dry-run", action="store_true", help="Simular operações sem fazer chamadas de API")
    parser.add_argument("--no-abrir", action="store_true", help="Não abrir os arquivos gerados")
    parser.add_argument("--debug", action="store_true", help="Ativar modo de depuração")

    args = parser.parse_args()

    # Configurar nível de log
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Verificar se foi fornecido um script existente
    script_path = None
    if args.script:
        if os.path.exists(args.script):
            script_path = args.script
            logger.info(f"Usando script existente: {script_path}")
        else:
            logger.error(f"Script não encontrado: {args.script}")
            return 1

    # Gerar o script se não foi fornecido um existente
    if not script_path:
        script_path = gerar_script(args.dias, args.noticias, args.tweets)
        if not script_path:
            logger.error("Falha ao gerar script")
            return 1

    # Gerar áudio
    audio_path = gerar_audio(script_path, args.dry_run)
    if not audio_path:
        logger.error("Falha ao gerar áudio")
        return 1

    # Gerar vídeo
    video_path = gerar_video(audio_path, args.dry_run)
    if not video_path:
        logger.error("Falha ao gerar vídeo")
        return 1

    # Exibir resultado
    logger.info("Vídeo Rapidinha gerado com sucesso!")
    logger.info(f"Script: {script_path}")
    logger.info(f"Áudio: {audio_path}")
    logger.info(f"Vídeo: {video_path}")

    if args.dry_run:
        logger.info("NOTA: Este foi um teste em modo de simulação. Nenhum recurso de API foi consumido.")

    # Abrir os arquivos se solicitado
    if not args.no_abrir:
        abrir_arquivo(script_path)
        if not args.dry_run:
            abrir_arquivo(video_path)



    return 0

if __name__ == "__main__":
    sys.exit(main())
