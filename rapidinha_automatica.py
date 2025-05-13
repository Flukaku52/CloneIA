#!/usr/bin/env python3
"""
Script principal para automatizar todo o processo de criação da Rapidinha:
1. Buscar notícias e tweets sobre criptomoedas
2. Gerar um script para a Rapidinha
3. Gerar áudios para cada parte do script
4. Gerar vídeos para cada parte do script
"""
import os
import sys
import logging
import argparse
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('rapidinha_automatica')

def verificar_dependencias():
    """
    Verifica se todas as dependências estão disponíveis.
    
    Returns:
        bool: True se todas as dependências estão disponíveis, False caso contrário
    """
    dependencias = [
        "buscador_noticias_cripto",
        "buscador_tweets_cripto",
        "gerador_script_rapidinha",
        "gerar_reels_automatico"
    ]
    
    for dep in dependencias:
        try:
            __import__(dep)
        except ImportError:
            logger.error(f"Dependência não encontrada: {dep}.py")
            return False
    
    return True

def main():
    """
    Função principal para automatizar todo o processo de criação da Rapidinha.
    """
    parser = argparse.ArgumentParser(description="Automatização completa da Rapidinha")
    parser.add_argument("--noticias", type=int, default=5, help="Número de notícias a incluir no script")
    parser.add_argument("--tweets", type=int, default=2, help="Número de tweets a incluir no script")
    parser.add_argument("--output", help="Nome base para os arquivos de saída")
    parser.add_argument("--audio-only", action="store_true", help="Gerar apenas os áudios, sem os vídeos")
    parser.add_argument("--force", action="store_true", help="Forçar a geração mesmo se houver problemas")
    parser.add_argument("--no-validate", action="store_true", help="Desativar a validação dos scripts")
    
    args = parser.parse_args()
    
    # Verificar dependências
    if not verificar_dependencias():
        logger.error("Algumas dependências não foram encontradas. Abortando.")
        return 1
    
    # Importar módulos
    from gerador_script_rapidinha import GeradorScriptRapidinha
    from gerar_reels_automatico import ReelsGenerator
    
    # Definir nome base para os arquivos de saída
    if not args.output:
        data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"rapidinha_{data_hora}.txt"
    
    # Etapa 1: Gerar o script
    logger.info("="*50)
    logger.info("ETAPA 1: GERANDO SCRIPT PARA A RAPIDINHA")
    logger.info("="*50)
    
    gerador = GeradorScriptRapidinha()
    script = gerador.gerar_script(
        num_noticias=args.noticias,
        num_tweets=args.tweets
    )
    caminho_script = gerador.salvar_script(script, args.output)
    
    if not caminho_script:
        logger.error("Falha ao salvar o script. Abortando.")
        return 1
    
    logger.info(f"Script gerado e salvo em {caminho_script}")
    
    # Etapa 2: Gerar áudios e vídeos
    logger.info("\n" + "="*50)
    logger.info("ETAPA 2: GERANDO ÁUDIOS E VÍDEOS")
    logger.info("="*50)
    
    # Extrair o prefixo do nome do arquivo
    nome_arquivo = os.path.basename(caminho_script)
    prefixo = os.path.splitext(nome_arquivo)[0]
    
    # Criar o gerador de vídeos
    reels_generator = ReelsGenerator(
        script_path=caminho_script,
        prefix=prefixo,
        validate=not args.no_validate,
        force=args.force,
        skip_video=args.audio_only
    )
    
    # Processar o script
    resultados = reels_generator.processar_script()
    
    # Exibir resumo
    logger.info("\n" + "="*50)
    logger.info("RESUMO DA GERAÇÃO")
    logger.info("="*50)
    logger.info(f"Scripts gerados: {len(resultados['scripts'])}")
    logger.info(f"Áudios gerados: {len(resultados['audios'])}")
    logger.info(f"Vídeos gerados: {len(resultados['videos'])}")
    
    # Exibir instruções para o próximo passo
    if resultados['videos']:
        logger.info("\nVídeos gerados com sucesso! Agora você pode:")
        logger.info("1. Usar um editor de vídeo como o CapCut para juntar os vídeos")
        logger.info("2. Adicionar transições entre os segmentos")
        logger.info("3. Adicionar música de fundo ou efeitos sonoros")
        logger.info("4. Publicar o vídeo final nas redes sociais")
    elif resultados['audios']:
        logger.info("\nÁudios gerados com sucesso! Agora você pode:")
        logger.info("1. Gerar os vídeos usando o comando:")
        logger.info(f"   python3 gerar_reels_automatico.py --script {caminho_script}")
        logger.info("2. Ou usar os áudios gerados para criar vídeos manualmente")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
