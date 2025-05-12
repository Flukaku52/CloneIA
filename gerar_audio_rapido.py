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

    # Adicionar marcadores de velocidade (25% mais rápido)
    text = "<prosody rate='1.25'>" + text + "</prosody>"

    return text

def generate_audio(script_path: str, output_path: str = None, profile_name: str = "flukakuia",
                validate: bool = True, force: bool = False):
    """
    Gera áudio a partir de um script usando o perfil especificado.

    Args:
        script_path: Caminho para o arquivo de script
        output_path: Caminho para salvar o áudio (se None, gera um nome baseado no timestamp)
        profile_name: Nome do perfil de voz a ser usado
        validate: Se True, valida o roteiro antes de gerar o áudio
        force: Se True, gera o áudio mesmo se a validação falhar

    Returns:
        str: Caminho para o áudio gerado, ou None se falhar
    """
    if not os.path.exists(script_path):
        logger.error(f"Arquivo de script não encontrado: {script_path}")
        return None

    # Carregar o texto do script
    with open(script_path, 'r', encoding='utf-8') as f:
        script_content = f.read()

    # Validar o roteiro antes de gerar o áudio
    if validate:
        try:
            from validador_roteiro import ValidadorRoteiro
            validador = ValidadorRoteiro()
            valido, problemas = validador.validar_texto(script_content)
            custos = validador.estimar_custos(script_content)

            logger.info("\n=== Validação do Roteiro ===")
            logger.info(f"Válido: {'Sim' if valido else 'Não'}")

            if not valido:
                for problema in problemas:
                    logger.warning(f"- {problema}")

                logger.info("\n=== Estimativa de Custos ===")
                logger.info(f"Caracteres: {custos.get('caracteres', 0)}")
                logger.info(f"Duração estimada: {custos.get('duracao_segundos', 0):.2f} segundos")
                logger.info(f"Custo ElevenLabs: ${custos.get('custo_elevenlabs', 0):.4f}")
                logger.info(f"Custo HeyGen: ${custos.get('custo_heygen', 0):.2f}")
                logger.info(f"Custo total: ${custos.get('custo_total', 0):.2f}")

                if not force:
                    logger.error("Geração de áudio cancelada devido a problemas no roteiro. Use --force para ignorar.")
                    return None
                else:
                    logger.warning("Ignorando problemas no roteiro devido à flag --force.")
        except ImportError:
            logger.warning("Módulo validador_roteiro não encontrado. Pulando validação.")

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
    parser.add_argument("--no-validate", action="store_true", help="Desativa a validação do roteiro")
    parser.add_argument("--force", action="store_true", help="Força a geração mesmo com problemas no roteiro")
    parser.add_argument("--validate-only", action="store_true", help="Apenas valida o roteiro, sem gerar áudio")

    args = parser.parse_args()

    # Se a opção --validate-only foi especificada, apenas validar o roteiro
    if args.validate_only:
        try:
            from validador_roteiro import validar_arquivo
            valido, mensagem, custos = validar_arquivo(args.script, corrigir=False)

            print("\n=== Resultado da Validação ===")
            print(f"Arquivo: {args.script}")
            print(f"Válido: {'Sim' if valido else 'Não'}")
            print(mensagem)

            print("\n=== Estimativa de Custos ===")
            print(f"Caracteres: {custos.get('caracteres', 0)}")
            print(f"Duração estimada: {custos.get('duracao_segundos', 0):.2f} segundos")
            print(f"Custo ElevenLabs: ${custos.get('custo_elevenlabs', 0):.4f}")
            print(f"Custo HeyGen: ${custos.get('custo_heygen', 0):.2f}")
            print(f"Custo total: ${custos.get('custo_total', 0):.2f}")

            return 0 if valido else 1
        except ImportError:
            logger.error("Módulo validador_roteiro não encontrado. Não é possível validar o roteiro.")
            return 1

    # Gerar o áudio
    audio_path = generate_audio(
        script_path=args.script,
        output_path=args.output,
        profile_name=args.profile,
        validate=not args.no_validate,
        force=args.force
    )

    # Retornar o caminho do áudio para uso em outros scripts
    if audio_path:
        print(f"AUDIO_PATH={audio_path}")
        return 0
    else:
        return 1

if __name__ == "__main__":
    main()
