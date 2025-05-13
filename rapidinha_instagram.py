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
import logging
import argparse
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('rapidinha_instagram')

# Importar módulos necessários
try:
    from instagram_publisher import InstagramPublisher
except ImportError as e:
    logger.error(f"Erro ao importar módulos necessários: {e}")
    logger.error("Certifique-se de que o arquivo instagram_publisher.py está disponível.")
    sys.exit(1)

def verificar_dependencias():
    """
    Verifica se todas as dependências necessárias estão instaladas.

    Returns:
        bool: True se todas as dependências estão disponíveis, False caso contrário
    """
    dependencias = {
        "moviepy": "Processamento de vídeo",
        "requests": "Requisições HTTP",
        "pillow": "Processamento de imagens",
        "numpy": "Processamento numérico"
    }

    faltando = []

    for modulo, descricao in dependencias.items():
        try:
            __import__(modulo)
        except ImportError:
            faltando.append(f"{modulo} ({descricao})")

    if faltando:
        logger.error("As seguintes dependências estão faltando:")
        for dep in faltando:
            logger.error(f"- {dep}")
        logger.error("Instale-as usando: pip install " + " ".join([d.split()[0] for d in faltando]))
        return False

    return True

def gerar_script_rapidinha(noticias: List[Dict[str, Any]], tweets: List[Dict[str, Any]]) -> str:
    """
    Gera um script para a Rapidinha Cripto com base nas notícias e tweets fornecidos.

    Args:
        noticias: Lista de notícias sobre criptomoedas
        tweets: Lista de tweets sobre criptomoedas

    Returns:
        str: Script gerado
    """
    # Introdução padrão
    introducao = "E aí cambada! Tô de volta com mais uma Rapidinha Cripto!\n\n"

    # Corpo com as notícias
    corpo = "Vamos às notícias!\n\n"

    # Adicionar as notícias
    for i, noticia in enumerate(noticias, 1):
        titulo = noticia.get('titulo', 'Notícia sem título')
        resumo = noticia.get('resumo', 'Sem detalhes disponíveis')

        # Limitar o resumo a 200 caracteres
        if len(resumo) > 200:
            resumo = resumo[:197] + "..."

        corpo += f"{i}. {titulo}\n"
        corpo += f"{resumo}\n\n"

    # Adicionar tweets interessantes
    if tweets:
        corpo += "E o que estão falando nas redes sociais?\n\n"

        for i, tweet in enumerate(tweets, 1):
            texto = tweet.get('text', 'Tweet sem texto')
            autor = tweet.get('author_username', 'usuário')

            # Limitar o texto a 150 caracteres
            if len(texto) > 150:
                texto = texto[:147] + "..."

            corpo += f"@{autor} diz: \"{texto}\"\n\n"

    # Conclusão padrão
    conclusao = "E é isso por hoje, pessoal! Até a próxima rapidinha!"

    # Juntar tudo
    script = introducao + corpo + conclusao

    return script

def gerar_conteudo(args: argparse.Namespace) -> Optional[Dict[str, Any]]:
    """
    Gera o conteúdo da Rapidinha (script, áudios e vídeos).

    Args:
        args: Argumentos da linha de comando

    Returns:
        Optional[Dict[str, Any]]: Informações sobre o conteúdo gerado, ou None se falhar
    """
    logger.info("Gerando conteúdo da Rapidinha...")

    # Verificar dependências (comentado para testes)
    # if not verificar_dependencias():
    #     logger.error("Algumas dependências não foram encontradas. Abortando.")
    #     return None

    # Importar módulos necessários
    from buscador_noticias_cripto import NoticiasCriptoScraper
    from buscador_tweets_cripto import TwitterCriptoScraper
    from core.audio import AudioGenerator
    from core.utils import ensure_directory, OUTPUT_DIR

    # Definir nome base para os arquivos de saída
    data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"rapidinha_{data_hora}.txt"

    # Etapa 1: Gerar o script
    logger.info("="*50)
    logger.info("ETAPA 1: GERANDO SCRIPT PARA A RAPIDINHA")
    logger.info("="*50)

    # Buscar notícias e tweets
    logger.info("Buscando notícias e tweets sobre criptomoedas...")

    # Criar os buscadores
    noticias_scraper = NoticiasCriptoScraper()
    tweets_scraper = TwitterCriptoScraper()

    # Buscar notícias e tweets
    noticias = noticias_scraper.buscar_todas_noticias(max_total=args.noticias, dias_max=7)
    tweets = tweets_scraper.buscar_tweets_por_termos(max_total=args.tweets, dias_max=7)

    # Gerar o script
    script = gerar_script_rapidinha(noticias, tweets)

    # Salvar o script
    scripts_dir = os.path.join(OUTPUT_DIR, "scripts")
    ensure_directory(scripts_dir)
    caminho_script = os.path.join(scripts_dir, nome_arquivo)

    with open(caminho_script, 'w', encoding='utf-8') as f:
        f.write(script)

    if not os.path.exists(caminho_script):
        logger.error("Falha ao salvar o script. Abortando.")
        return None

    logger.info(f"Script gerado e salvo em {caminho_script}")

    # Etapa 2: Gerar áudios
    logger.info("\n" + "="*50)
    logger.info("ETAPA 2: GERANDO ÁUDIOS")
    logger.info("="*50)

    # Extrair o prefixo do nome do arquivo
    nome_arquivo = os.path.basename(caminho_script)
    prefixo = os.path.splitext(nome_arquivo)[0]

    # Gerar áudio
    audio_generator = AudioGenerator(voice_profile="flukakuia")
    audio_path = os.path.join(OUTPUT_DIR, "audio", f"{prefixo}.mp3")

    # Garantir que o diretório existe
    ensure_directory(os.path.dirname(audio_path))

    # Gerar o áudio
    audio_result = audio_generator.generate_audio(
        script,
        audio_path,
        optimize=True
    )

    # Resultados
    resultados = {
        'audios': [audio_result] if audio_result else [],
        'videos': []
    }

    # Se não quisermos gerar vídeo, retornar aqui
    if args.audio_only:
        logger.info("Modo somente áudio ativado. Pulando geração de vídeo.")
        return {
            "script_path": caminho_script,
            "script_content": script,
            "audio_paths": resultados['audios'],
            "video_paths": [],
            "video_final": None,
            "prefix": prefixo
        }

    # Etapa 3: Gerar vídeo com o HeyGen
    if not args.audio_only and audio_result:
        logger.info("\n" + "="*50)
        logger.info("ETAPA 3: GERANDO VÍDEO COM HEYGEN")
        logger.info("="*50)

        try:
            # Importar o gerador de vídeo do HeyGen
            from gerar_video_heygen import generate_heygen_video

            # Gerar o vídeo
            video_path = os.path.join(OUTPUT_DIR, "videos", f"{prefixo}.mp4")

            # Garantir que o diretório existe
            ensure_directory(os.path.dirname(video_path))

            # Gerar o vídeo
            logger.info(f"Gerando vídeo com o HeyGen usando o áudio: {audio_result}")
            video_final = generate_heygen_video(
                audio_path=audio_result,
                script_path=caminho_script,
                output_path=video_path
            )

            if video_final:
                logger.info(f"Vídeo gerado com sucesso: {video_final}")
                resultados['videos'].append(video_final)
            else:
                logger.error("Falha ao gerar o vídeo com o HeyGen")
                video_final = None
        except Exception as e:
            logger.error(f"Erro ao gerar vídeo com o HeyGen: {e}")
            video_final = None
    else:
        video_final = None

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

    # Argumentos para personalização
    parser.add_argument("--patterns", help="Arquivo com padrões extraídos de Reels existentes")

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
