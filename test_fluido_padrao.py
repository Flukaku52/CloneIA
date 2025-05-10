#!/usr/bin/env python3
"""
Script para testar o perfil de voz 'fluido' como padrão do projeto.
Gera um vídeo com o HeyGen usando o texto otimizado.
"""
import os
import sys
import json
import time
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_fluido_padrao.log')
    ]
)
logger = logging.getLogger('test_fluido_padrao')

# Importar os módulos necessários
from heygen_video_generator import HeyGenVideoGenerator, open_video_file
from core.text import TextProcessor

# Texto do script fornecido
SCRIPT_TEXT = """E aí CAMBADA! Tô de volta na área com energia!
Bora de RAPIDINHA!
Hoje eu tenho um desafio: tem algo diferente nesse vídeo... consegue adivinhar?
Comenta aí!
No fim do vídeo eu revelo o mistério!"""

# ID do avatar a ser usado
AVATAR_ID = "ae9ff9b6dc47436c8e9a30c25a0d7b29"

# Pasta no HeyGen onde o vídeo será salvo
FOLDER_NAME = "augment"

def verify_voice_config():
    """
    Verifica se o perfil de voz 'fluido' foi configurado corretamente como padrão.

    Returns:
        bool: True se a configuração está correta, False caso contrário
    """
    # Verificar o arquivo de configuração do perfil fluido
    fluido_config_path = os.path.join(os.getcwd(), "config", "voice_config_fluido.json")
    default_config_path = os.path.join(os.getcwd(), "config", "voice_config.json")

    try:
        # Carregar as configurações
        with open(fluido_config_path, 'r', encoding='utf-8') as f:
            fluido_config = json.load(f)

        with open(default_config_path, 'r', encoding='utf-8') as f:
            default_config = json.load(f)

        # Verificar se as configurações são iguais
        if fluido_config == default_config:
            logger.info("Perfil 'fluido' configurado corretamente como padrão.")

            # Verificar os parâmetros específicos
            settings = default_config.get("settings", {})
            stability = settings.get("stability")
            similarity_boost = settings.get("similarity_boost")
            style = settings.get("style")

            if stability == 0.2 and similarity_boost == 0.7 and style == 1.0:
                logger.info("Parâmetros do perfil 'fluido' configurados corretamente:")
                logger.info(f"- stability: {stability}")
                logger.info(f"- similarity_boost: {similarity_boost}")
                logger.info(f"- style: {style}")
                return True
            else:
                logger.error("Parâmetros do perfil 'fluido' não estão configurados corretamente.")
                logger.error(f"- stability: {stability} (esperado: 0.2)")
                logger.error(f"- similarity_boost: {similarity_boost} (esperado: 0.7)")
                logger.error(f"- style: {style} (esperado: 1.0)")
                return False
        else:
            logger.error("Perfil 'fluido' não está configurado como padrão.")
            return False

    except Exception as e:
        logger.error(f"Erro ao verificar configuração de voz: {e}")
        return False

def optimize_text(text):
    """
    Otimiza o texto para fala natural usando o TextProcessor.

    Args:
        text: Texto original

    Returns:
        str: Texto otimizado
    """
    logger.info("Otimizando texto para fala natural...")

    # Inicializar o processador de texto
    processor = TextProcessor()

    # Otimizar o texto
    optimized_text = processor.optimize_for_speech(text)

    logger.info(f"Texto original: {text}")
    logger.info(f"Texto otimizado: {optimized_text}")

    return optimized_text

def generate_video(text, avatar_id, folder_name):
    """
    Gera um vídeo com o HeyGen usando o texto otimizado.

    Args:
        text: Texto otimizado
        avatar_id: ID do avatar a ser usado
        folder_name: Nome da pasta no HeyGen onde o vídeo será salvo

    Returns:
        str: Caminho para o arquivo de vídeo gerado, ou None se falhar
    """
    logger.info("Gerando vídeo com o HeyGen...")

    # Inicializar o gerador de vídeo
    video_generator = HeyGenVideoGenerator()

    # Gerar nome para o arquivo de vídeo
    timestamp = int(time.time())
    output_dir = os.path.join(os.getcwd(), "output", "videos")
    os.makedirs(output_dir, exist_ok=True)
    video_path = os.path.join(output_dir, f"fluido_padrao_{timestamp}.mp4")

    # Gerar o vídeo diretamente com o texto otimizado (sem gerar áudio separadamente)
    video_path = video_generator.generate_video(
        script=text,
        audio_path=None,  # Não usar áudio pré-gerado
        output_path=video_path,
        avatar_id=avatar_id,
        folder_name=folder_name
    )

    if video_path:
        logger.info(f"Vídeo gerado com sucesso: {video_path}")
        return video_path
    else:
        logger.error("Falha ao gerar vídeo.")
        return None

def main():
    """
    Função principal que executa o processo completo.
    """
    logger.info("Iniciando teste do perfil 'fluido' como padrão...")

    # Verificar se o perfil foi configurado corretamente
    if not verify_voice_config():
        logger.error("Configuração do perfil 'fluido' não está correta. Abortando teste.")
        return

    # Otimizar o texto
    optimized_text = optimize_text(SCRIPT_TEXT)

    # Gerar o vídeo
    video_path = generate_video(optimized_text, AVATAR_ID, FOLDER_NAME)

    if video_path:
        # Reproduzir o vídeo automaticamente
        logger.info("Reproduzindo o vídeo gerado...")
        open_video_file(video_path)

        # Gerar relatório
        report = [
            "=== RELATÓRIO DE TESTE DO PERFIL 'FLUIDO' COMO PADRÃO ===",
            f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\nTexto utilizado: {SCRIPT_TEXT}",
            f"\nTexto otimizado: {optimized_text}",
            f"\nAvatar utilizado: {AVATAR_ID}",
            f"\nVídeo gerado: {video_path}",
            "\n=== CONFIGURAÇÃO DO PERFIL 'FLUIDO' ===",
            "- stability: 0.2",
            "- similarity_boost: 0.7",
            "- style: 1.0",
            "- use_speaker_boost: true",
            "- model_id: eleven_multilingual_v2",
            "\n=== OBSERVAÇÕES ===",
            "- O perfil 'fluido' foi configurado como padrão do projeto.",
            "- Os parâmetros foram ajustados para melhorar a fluidez e entonação.",
            "- O vídeo foi gerado diretamente com o HeyGen usando o texto otimizado.",
            "- O vídeo foi reproduzido automaticamente."
        ]

        # Salvar o relatório
        report_path = os.path.join(os.getcwd(), "output", f"relatorio_fluido_padrao_{int(time.time())}.txt")
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(report))

        logger.info(f"Relatório salvo em: {report_path}")
        logger.info("Teste concluído com sucesso!")
    else:
        logger.error("Teste falhou devido a erro na geração do vídeo.")

if __name__ == "__main__":
    main()
