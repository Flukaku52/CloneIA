#!/usr/bin/env python3
"""
Script para automatizar todo o processo de criação e publicação da Rapidinha no Instagram:
1. Buscar notícias e tweets sobre criptomoedas
2. Gerar um script para a Rapidinha
3. Gerar áudios para cada parte do script
4. Gerar vídeos para cada parte do script
5. Juntar os vídeos em um único arquivo
6. Publicar o vídeo no Instagram
"""
import os
import sys
import json
import logging
import argparse
import subprocess
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('rapidinha_instagram')

# Importar módulos necessários
try:
    from rapidinha_automatica import verificar_dependencias
    from instagram_publisher import InstagramPublisher
except ImportError as e:
    logger.error(f"Erro ao importar módulos necessários: {e}")
    logger.error("Certifique-se de que os arquivos rapidinha_automatica.py e instagram_publisher.py estão disponíveis.")
    sys.exit(1)

def gerar_conteudo(args: argparse.Namespace) -> Optional[Dict[str, Any]]:
    """
    Gera o conteúdo da Rapidinha (script, áudios e vídeos).
    
    Args:
        args: Argumentos da linha de comando
        
    Returns:
        Optional[Dict[str, Any]]: Informações sobre o conteúdo gerado, ou None se falhar
    """
    logger.info("Gerando conteúdo da Rapidinha...")
    
    # Verificar dependências
    if not verificar_dependencias():
        logger.error("Algumas dependências não foram encontradas. Abortando.")
        return None
    
    # Importar módulos
    from gerador_script_rapidinha import GeradorScriptRapidinha
    from gerar_reels_automatico import ReelsGenerator
    
    # Definir nome base para os arquivos de saída
    data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"rapidinha_{data_hora}.txt"
    
    # Etapa 1: Gerar o script
    logger.info("="*50)
    logger.info("ETAPA 1: GERANDO SCRIPT PARA A RAPIDINHA")
    logger.info("="*50)
    
    gerador = GeradorScriptRapidinha()
    script = gerador.gerar_script(
        num_noticias=args.noticias,
        num_tweets=args.tweets
    )
    caminho_script = gerador.salvar_script(script, nome_arquivo)
    
    if not caminho_script:
        logger.error("Falha ao salvar o script. Abortando.")
        return None
    
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
    
    # Verificar se temos vídeos gerados
    if not args.audio_only and not resultados['videos']:
        logger.error("Nenhum vídeo foi gerado. Abortando.")
        return None
    
    # Etapa 3: Juntar os vídeos (se necessário)
    video_final = None
    
    if not args.audio_only and len(resultados['videos']) > 1 and not args.no_join:
        logger.info("\n" + "="*50)
        logger.info("ETAPA 3: JUNTANDO OS VÍDEOS")
        logger.info("="*50)
        
        # Juntar os vídeos usando FFmpeg
        video_final = os.path.join("output", "videos", f"{prefixo}_final.mp4")
        
        # Criar arquivo de lista para o FFmpeg
        lista_videos = os.path.join("output", "videos", f"{prefixo}_list.txt")
        with open(lista_videos, 'w', encoding='utf-8') as f:
            for video in resultados['videos']:
                f.write(f"file '{os.path.abspath(video)}'\n")
        
        # Executar FFmpeg para juntar os vídeos
        try:
            cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
                "-i", lista_videos, "-c", "copy", video_final
            ]
            
            logger.info(f"Executando comando: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            
            logger.info(f"Vídeos juntados com sucesso em {video_final}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao juntar vídeos: {e}")
            video_final = None
        except FileNotFoundError:
            logger.error("FFmpeg não encontrado. Não foi possível juntar os vídeos.")
            video_final = None
    elif not args.audio_only and resultados['videos']:
        # Se temos apenas um vídeo, usar ele diretamente
        video_final = resultados['videos'][0]
    
    # Retornar informações sobre o conteúdo gerado
    return {
        "script_path": caminho_script,
        "script_content": script,
        "audio_paths": resultados['audios'],
        "video_paths": resultados['videos'],
        "video_final": video_final,
        "prefix": prefixo
    }

def publicar_instagram(conteudo: Dict[str, Any], args: argparse.Namespace) -> Optional[str]:
    """
    Publica o vídeo no Instagram.
    
    Args:
        conteudo: Informações sobre o conteúdo gerado
        args: Argumentos da linha de comando
        
    Returns:
        Optional[str]: ID da publicação, ou None se falhar
    """
    if args.audio_only:
        logger.info("Modo somente áudio ativado. Pulando publicação no Instagram.")
        return None
    
    if not conteudo.get("video_final"):
        logger.error("Nenhum vídeo final disponível para publicação.")
        return None
    
    logger.info("\n" + "="*50)
    logger.info("ETAPA 4: PUBLICANDO NO INSTAGRAM")
    logger.info("="*50)
    
    # Criar o publicador do Instagram
    publisher = InstagramPublisher()
    
    # Verificar autenticação
    if not publisher.check_auth_status():
        logger.error("Autenticação do Instagram inválida ou não configurada.")
        logger.error("Execute 'python instagram_publisher.py setup --app-id SEU_APP_ID --app-secret SEU_APP_SECRET --redirect-uri SUA_URI' para configurar.")
        return None
    
    # Extrair a primeira parte do script como legenda
    linhas = conteudo["script_content"].split("\n\n")
    legenda = ""
    
    # Usar as primeiras linhas até o primeiro marcador de corte como legenda
    for linha in linhas:
        if linha.strip() == "(Corte)":
            break
        legenda += linha + "\n\n"
    
    # Limitar a legenda a 2200 caracteres (limite do Instagram)
    if len(legenda) > 2200:
        legenda = legenda[:2197] + "..."
    
    # Adicionar hashtags
    hashtags = ["bitcoin", "cripto", "criptomoedas", "rapidinha", "flukaku"]
    if args.hashtags:
        hashtags.extend([tag.strip() for tag in args.hashtags.split(",")])
    
    # Publicar ou agendar
    if args.schedule:
        try:
            # Converter string de data/hora para objeto datetime
            publish_time = datetime.strptime(args.schedule, "%Y-%m-%d %H:%M")
            
            # Verificar se a data é futura
            if publish_time <= datetime.now():
                logger.warning("Data de publicação deve ser futura. Publicando imediatamente.")
                return publisher.publish_reels(conteudo["video_final"], legenda, hashtags)
            
            # Agendar publicação
            post_id = publisher.schedule_post(
                conteudo["video_final"], 
                legenda, 
                publish_time, 
                hashtags
            )
            
            if post_id:
                logger.info(f"Publicação agendada com sucesso para {publish_time.isoformat()}")
                logger.info(f"ID da publicação agendada: {post_id}")
                return post_id
            else:
                logger.error("Falha ao agendar publicação")
                return None
        except ValueError:
            logger.error(f"Formato de data e hora inválido: {args.schedule}")
            logger.error("Use o formato: YYYY-MM-DD HH:MM")
            return None
    else:
        # Publicar imediatamente
        post_id = publisher.publish_reels(conteudo["video_final"], legenda, hashtags)
        
        if post_id:
            logger.info(f"Vídeo publicado com sucesso no Instagram!")
            logger.info(f"ID da publicação: {post_id}")
            return post_id
        else:
            logger.error("Falha ao publicar vídeo no Instagram")
            return None

def main():
    """
    Função principal para automatizar todo o processo de criação e publicação da Rapidinha no Instagram.
    """
    parser = argparse.ArgumentParser(description="Automatização completa da Rapidinha para Instagram")
    
    # Argumentos para geração de conteúdo
    parser.add_argument("--noticias", type=int, default=5, help="Número de notícias a incluir no script")
    parser.add_argument("--tweets", type=int, default=2, help="Número de tweets a incluir no script")
    parser.add_argument("--no-validate", action="store_true", help="Desativar a validação dos scripts")
    parser.add_argument("--force", action="store_true", help="Forçar a geração mesmo se houver problemas")
    parser.add_argument("--audio-only", action="store_true", help="Gerar apenas os áudios, sem os vídeos")
    parser.add_argument("--no-join", action="store_true", help="Não juntar os vídeos em um único arquivo")
    
    # Argumentos para publicação no Instagram
    parser.add_argument("--no-publish", action="store_true", help="Não publicar no Instagram")
    parser.add_argument("--hashtags", help="Hashtags adicionais separadas por vírgula")
    parser.add_argument("--schedule", help="Agendar publicação (formato: YYYY-MM-DD HH:MM)")
    
    args = parser.parse_args()
    
    # Gerar conteúdo
    conteudo = gerar_conteudo(args)
    
    if not conteudo:
        logger.error("Falha ao gerar conteúdo. Abortando.")
        return 1
    
    # Publicar no Instagram
    if not args.no_publish and not args.audio_only:
        post_id = publicar_instagram(conteudo, args)
        
        if post_id:
            logger.info("\nProcesso completo executado com sucesso!")
            return 0
        else:
            logger.error("\nFalha na publicação no Instagram, mas o conteúdo foi gerado.")
            return 1
    else:
        logger.info("\nConteúdo gerado com sucesso!")
        logger.info("Publicação no Instagram desativada.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
