#!/usr/bin/env python3
"""
Script para processar um script com marcadores de corte explícitos.
"""
import os
import sys
import argparse
import logging
from datetime import datetime
from typing import List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('processar_script_com_cortes')

# Marcador de corte
MARCADOR_CORTE = "[CORTE]"

def remover_fontes_datas(texto: str) -> str:
    """
    Remove fontes e datas do texto.

    Args:
        texto: Texto a ser processado

    Returns:
        str: Texto sem fontes e datas
    """
    import re

    # Remover padrões como (Fonte: Nome, DD/MM/AAAA)
    texto = re.sub(r'\(Fonte:.*?\)', '', texto)

    # Remover datas no formato DD/MM/AAAA
    texto = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4}', '', texto)

    return texto.strip()

def dividir_por_marcadores(conteudo: str) -> List[str]:
    """
    Divide o conteúdo pelos marcadores de corte.

    Args:
        conteudo: Conteúdo do script

    Returns:
        List[str]: Lista de seções
    """
    # Remover fontes e datas
    conteudo = remover_fontes_datas(conteudo)

    # Dividir pelo marcador de corte
    secoes = [secao.strip() for secao in conteudo.split(MARCADOR_CORTE)]

    # Remover seções vazias
    secoes = [secao for secao in secoes if secao]

    return secoes

def exibir_script_com_cortes(secoes: List[str]) -> None:
    """
    Exibe o script formatado com indicações visuais dos cortes.

    Args:
        secoes: Lista de seções do script
    """
    print("\n" + "="*80)
    print("SCRIPT FORMATADO PARA RAPIDINHA COM CORTES")
    print("="*80)

    for i, secao in enumerate(secoes):
        print(secao)

        # Adicionar marcador de corte após cada seção, exceto a última
        if i < len(secoes) - 1:
            print("\n" + "="*40 + " CORTE " + "="*40 + "\n")

    print("="*80)

def exibir_info_secoes(secoes: List[str]) -> None:
    """
    Exibe informações sobre as seções do script.

    Args:
        secoes: Lista de seções do script
    """
    print("\nInformações do Script:")
    print(f"Número de seções: {len(secoes)}")
    print(f"Número de cortes: {len(secoes) - 1}")

    print("\nSeções:")
    for i, secao in enumerate(secoes):
        print(f"\nSeção {i+1}:")
        print("-" * 40)
        print(secao[:100] + "..." if len(secao) > 100 else secao)
        print("-" * 40)

def main():
    """
    Função principal para processar o script com marcadores de corte.
    """
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Processador de script com marcadores de corte")
    parser.add_argument("--arquivo", type=str, required=True, help="Arquivo com o conteúdo do script")
    parser.add_argument("--saida", type=str, help="Arquivo de saída para o áudio")
    parser.add_argument("--gerar-audio", action="store_true", help="Gerar áudio para cada seção")

    args = parser.parse_args()

    # Verificar se o arquivo existe
    if not os.path.exists(args.arquivo):
        logger.error(f"Arquivo não encontrado: {args.arquivo}")
        return 1

    # Ler conteúdo do arquivo
    try:
        with open(args.arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {e}")
        return 1

    logger.info(f"Processando script com marcadores de corte: {args.arquivo}")

    # Dividir o conteúdo pelos marcadores de corte
    secoes = dividir_por_marcadores(conteudo)

    # Exibir script com indicações visuais dos cortes
    exibir_script_com_cortes(secoes)

    # Exibir informações sobre as seções
    exibir_info_secoes(secoes)

    # Gerar áudio para cada seção se solicitado
    if args.gerar_audio:
        try:
            from core.audio_generator import AudioGenerator

            logger.info("Gerando áudio para cada seção...")

            # Criar o gerador de áudio
            audio_gen = AudioGenerator()

            # Gerar áudio para cada seção
            for i, secao in enumerate(secoes):
                logger.info(f"Gerando áudio para a seção {i+1}...")

                # Definir nome do arquivo de saída
                if args.saida:
                    base_name = os.path.splitext(args.saida)[0]
                    ext = os.path.splitext(args.saida)[1] or ".mp3"
                    output_file = f"{base_name}_secao_{i+1}{ext}"
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = f"output/audio/rapidinha_secao_{i+1}_{timestamp}.mp3"

                # Gerar áudio
                audio_path = audio_gen.generate_audio(secao, output_file)

                if audio_path:
                    logger.info(f"Áudio gerado: {audio_path}")
                else:
                    logger.error(f"Erro ao gerar áudio para a seção {i+1}")

        except ImportError:
            logger.error("Módulo audio_generator não encontrado. Não foi possível gerar áudio.")
            return 1
        except Exception as e:
            logger.error(f"Erro ao gerar áudio: {e}")
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
