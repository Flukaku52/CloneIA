#!/usr/bin/env python3
"""
Script para gerar áudio usando o perfil FlukakuIA com menos espaços entre palavras.
"""
import os
import argparse
import logging
from core.audio import AudioGenerator
from core.utils import ensure_directory, get_timestamp_filename, OUTPUT_DIR

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gerar_audio_rapido')

def optimize_text_for_speed(text):
    """
    Otimiza o texto para reduzir espaços entre palavras e aumentar a velocidade,
    preservando melhor as características da voz original.
    """
    # Processar hífens que foram adicionados para juntar palavras
    text = text.replace("-", " ")

    # Remover espaços extras
    text = ' '.join(text.split())

    # Substituir espaços por espaços reduzidos em certas frases
    text = text.replace("E aí cambada", "EAÍCAMBADA")
    text = text.replace("Fala cambada", "FALACAMBADA")
    text = text.replace("Eaí cambada", "EAÍCAMBADA")

    # Reduzir pontuação que causa pausas (mas não remover completamente)
    for char in [',', ';']:
        text = text.replace(char, '')

    # Manter alguns sinais de pontuação para preservar a entonação natural
    # mas reduzir a quantidade para diminuir as pausas
    text = text.replace("...", ".")
    text = text.replace("!!", "!")
    text = text.replace("??", "?")

    # Substituir termos para melhor pronúncia (apenas os mais importantes)
    replacements = {
        "Bitcoin": "Bitcoim",
        "Ethereum": "Etherium",
        "NFT": "ÊnÊfeTê",
        "DeFi": "DêFai"
    }

    for original, replacement in replacements.items():
        text = text.replace(original, replacement)

    # Adicionar marcadores de velocidade
    text = "<prosody rate='1.35'>" + text + "</prosody>"

    return text

def generate_audio(script_path: str, output_path: str = None, profile_name: str = "flukakuia"):
    """
    Gera áudio a partir de um script usando o perfil especificado.

    Args:
        script_path: Caminho para o arquivo de script
        output_path: Caminho para salvar o áudio (se None, gera um nome baseado no timestamp)
        profile_name: Nome do perfil de voz a ser usado

    Returns:
        str: Caminho para o áudio gerado, ou None se falhar
    """
    if not os.path.exists(script_path):
        logger.error(f"Arquivo de script não encontrado: {script_path}")
        return None

    # Carregar o texto do script
    with open(script_path, 'r', encoding='utf-8') as f:
        script_content = f.read()

    # Otimizar o texto para velocidade
    optimized_text = optimize_text_for_speed(script_content)
    logger.info(f"Texto original: {len(script_content)} chars")
    logger.info(f"Texto otimizado: {len(optimized_text)} chars")
    logger.info(f"Texto otimizado: '{optimized_text[:50]}...'")

    # Criar o gerador de áudio
    audio_generator = AudioGenerator(voice_profile=profile_name)

    # Definir o caminho para o áudio de saída
    if not output_path:
        timestamp = get_timestamp_filename("audio_rapido", "mp3")
        output_path = os.path.join(OUTPUT_DIR, "audio", timestamp)

    # Garantir que o diretório existe
    ensure_directory(os.path.dirname(output_path))

    # Gerar o áudio
    logger.info(f"Gerando áudio com o perfil {profile_name}...")

    # Desativar a otimização padrão, pois já fizemos nossa própria otimização
    audio_result = audio_generator.generate_audio(
        optimized_text, output_path, optimize=False
    )

    if audio_result:
        logger.info(f"Áudio gerado com sucesso: {audio_result}")
        return audio_result
    else:
        logger.error("Falha ao gerar o áudio")
        return None

def main():
    parser = argparse.ArgumentParser(description="Gerador de áudio rápido para o CloneIA")
    parser.add_argument("--script", required=True, help="Caminho para o arquivo de script")
    parser.add_argument("--output", help="Caminho para salvar o áudio")
    parser.add_argument("--profile", default="flukakuia", help="Nome do perfil de voz a ser usado")

    args = parser.parse_args()

    # Gerar o áudio
    audio_path = generate_audio(
        script_path=args.script,
        output_path=args.output,
        profile_name=args.profile
    )

    # Retornar o caminho do áudio para uso em outros scripts
    if audio_path:
        print(f"AUDIO_PATH={audio_path}")

if __name__ == "__main__":
    main()
