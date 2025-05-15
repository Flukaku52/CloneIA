#!/usr/bin/env python3
"""
Gerador de vídeo com cortes para o FlukakuIA.
"""
import os
import sys
import logging
import argparse
import glob
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gerar_video_com_cortes')

# Carregar variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("Módulo python-dotenv não encontrado. Variáveis de ambiente não serão carregadas do arquivo .env.")

# Importar gerenciador de contas
try:
    from core.account_manager import AccountManager
    account_manager = AccountManager()
    logger.info("Gerenciador de contas carregado com sucesso")
except ImportError:
    logger.warning("Módulo account_manager não encontrado. Usando configurações padrão.")
    account_manager = None

def criar_diretorios():
    """
    Cria os diretórios necessários para o funcionamento do script.
    """
    diretorios = [
        "output/audio",
        "output/videos"
    ]

    for diretorio in diretorios:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
            logger.info(f"Diretório criado: {diretorio}")

def gerar_video_para_secao(audio_path, dry_run=False):
    """
    Gera um vídeo para uma seção de áudio.

    Args:
        audio_path: Caminho para o arquivo de áudio
        dry_run: Se True, simula a geração sem fazer chamadas de API

    Returns:
        str: Caminho para o vídeo gerado, ou None em caso de erro
    """
    if dry_run:
        # Simular geração de vídeo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = os.path.join("output", "videos", f"rapidinha_video_secao_{timestamp}.mp4")
        logger.info(f"[SIMULAÇÃO] Vídeo gerado: {video_path}")
        return video_path

    try:
        # Importar bibliotecas necessárias
        import requests
        import json
        import time

        # Obter credenciais do gerenciador de contas ou do ambiente
        if account_manager:
            api_key, avatar_id = account_manager.get_heygen_account()
            active_account = account_manager.get_active_heygen_account_id()
            logger.info(f"Usando conta HeyGen: {active_account}")
        else:
            # Verificar API key
            api_key = os.environ.get("HEYGEN_API_KEY")
            if not api_key:
                logger.error("API key do HeyGen não encontrada.")
                return None

            # ID do avatar padrão do Flukaku
            avatar_id = "431f819b1a8e42bb8f095e98e1e805a4"

        logger.info(f"Usando API key do HeyGen: {api_key[:10]}...")
        logger.info(f"Usando avatar ID: {avatar_id}")

        # Configurar headers
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": api_key
        }

        # Criar vídeo
        url = "https://api.heygen.com/v2/video/generate"

        payload = {
            "dimension": {
                "width": 720,
                "height": 1280
            },
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id,
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "audio"
                    },
                    "background": {
                        "type": "color",
                        "value": "#000000"
                    }
                }
            ]
        }

        # Ler o arquivo de áudio
        with open(audio_path, 'rb') as audio_file:
            audio_data = audio_file.read()

        # Fazer upload do áudio para o endpoint de upload
        upload_url = "https://upload.heygen.com/v1/asset"

        # Configurar headers para upload
        upload_headers = {
            "Content-Type": "audio/mpeg",
            "X-Api-Key": api_key
        }

        # Salvar o áudio em um arquivo temporário
        temp_audio_path = os.path.join("output", "audio", "temp_audio.mp3")
        with open(temp_audio_path, "wb") as f:
            f.write(audio_data)

        # Enviar o áudio como um arquivo
        with open(temp_audio_path, "rb") as f:
            upload_response = requests.post(
                upload_url,
                headers=upload_headers,
                data=f.read()
            )

        # Remover o arquivo temporário
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        if upload_response.status_code != 200:
            logger.error(f"Erro ao fazer upload do áudio: {upload_response.text}")
            return None

        # Obter o ID do áudio
        audio_asset_id = upload_response.json().get("data", {}).get("id")

        if not audio_asset_id:
            logger.error("ID do áudio não encontrado na resposta.")
            return None

        # Atualizar o payload com o ID do áudio
        payload["video_inputs"][0]["voice"]["audio_asset_id"] = audio_asset_id

        # Enviar a requisição para gerar o vídeo
        logger.info(f"Enviando requisição para gerar vídeo: {url}")
        logger.info(f"Payload: {payload}")

        response = requests.post(
            url,
            headers=headers,
            json=payload
        )

        logger.info(f"Resposta: {response.status_code} - {response.text}")

        if response.status_code != 200:
            logger.error(f"Erro ao criar vídeo: {response.text}")
            return None

        # Obter ID do vídeo
        video_id = response.json().get("data", {}).get("video_id")
        if not video_id:
            logger.error("ID do vídeo não encontrado na resposta.")
            return None

        # Verificar status do vídeo
        url_status = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
        logger.info(f"Verificando status do vídeo: {url_status}")

        max_attempts = 30  # 30 tentativas
        attempts = 0
        wait_time = 60  # Aguardar 60 segundos entre as verificações

        while attempts < max_attempts:
            attempts += 1
            logger.info(f"Tentativa {attempts}/{max_attempts}")

            try:
                response = requests.get(url_status, headers=headers)
                logger.info(f"Resposta: {response.status_code} - {response.text}")

                if response.status_code != 200:
                    logger.error(f"Erro ao verificar status do vídeo: {response.text}")
                    return None

                status = response.json().get("data", {}).get("status")
                logger.info(f"Status do vídeo: {status}")
            except Exception as e:
                logger.error(f"Erro ao verificar status do vídeo: {e}")
                return None

            if status == "completed":
                # Obter URL do vídeo
                video_url = response.json().get("data", {}).get("video_url")

                if not video_url:
                    logger.error("URL do vídeo não encontrada na resposta.")
                    return None

                # Extrair o número da seção do nome do arquivo de áudio
                secao = os.path.basename(audio_path).split("_")[2]

                # Baixar vídeo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                video_path = os.path.join("output", "videos", f"rapidinha_video_secao_{secao}_{timestamp}.mp4")

                try:
                    # Usar curl para baixar o vídeo
                    import subprocess
                    logger.info(f"Baixando vídeo: {video_url}")
                    logger.info(f"Salvando em: {video_path}")

                    # Escapar a URL para o shell
                    escaped_url = video_url.replace('"', '\\"')

                    # Executar o comando curl
                    cmd = f'curl -o "{video_path}" "{escaped_url}"'
                    subprocess.run(cmd, shell=True, check=True)

                    logger.info(f"Vídeo gerado com sucesso: {video_path}")
                    return video_path
                except Exception as e:
                    logger.error(f"Erro ao baixar vídeo: {e}")

                    # Tentar método alternativo com requests
                    try:
                        logger.info("Tentando método alternativo para baixar o vídeo...")
                        response = requests.get(video_url)

                        with open(video_path, "wb") as f:
                            f.write(response.content)

                        logger.info(f"Vídeo gerado com sucesso: {video_path}")
                        return video_path
                    except Exception as e2:
                        logger.error(f"Erro ao baixar vídeo (método alternativo): {e2}")
                        return None

            elif status == "failed":
                logger.error("Falha ao gerar vídeo.")
                return None

            # Aguardar antes de verificar novamente
            time.sleep(wait_time)

        logger.error("Tempo limite excedido ao aguardar a geração do vídeo.")
        return None

    except Exception as e:
        logger.error(f"Erro ao gerar vídeo: {e}")
        return None

def abrir_arquivo(file_path):
    """
    Abre um arquivo com o aplicativo padrão do sistema.

    Args:
        file_path: Caminho para o arquivo
    """
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return

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

    except Exception as e:
        logger.error(f"Erro ao abrir arquivo: {e}")

def main():
    """
    Função principal.
    """
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Gerador de vídeo com cortes para o FlukakuIA")
    parser.add_argument("--timestamp", help="Timestamp dos arquivos de áudio (formato: YYYYMMDD_HHMMSS)")
    parser.add_argument("--dry-run", action="store_true", help="Simular operações sem fazer chamadas de API")
    parser.add_argument("--no-abrir", action="store_true", help="Não abrir os arquivos gerados")
    parser.add_argument("--debug", action="store_true", help="Ativar modo de depuração")

    # Argumentos para gerenciamento de contas
    if account_manager:
        parser.add_argument("--conta", choices=["conta1", "conta2", "conta3"],
                           help="Conta HeyGen a ser utilizada")
        parser.add_argument("--listar-contas", action="store_true",
                           help="Listar contas HeyGen disponíveis")

    args = parser.parse_args()

    # Configurar nível de log
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Listar contas se solicitado
    if account_manager and hasattr(args, 'listar_contas') and args.listar_contas:
        contas = account_manager.list_heygen_accounts()
        conta_ativa = account_manager.get_active_heygen_account_id()

        print("\nContas HeyGen disponíveis:")
        for conta_id, conta_info in contas.items():
            status = " (ATIVA)" if conta_id == conta_ativa else ""
            print(f"  - {conta_id}{status}: {conta_info.get('description', '')}")
            print(f"    Avatar ID: {conta_info.get('avatar_id', '')}")

        return 0

    # Definir conta ativa se solicitado
    if account_manager and hasattr(args, 'conta') and args.conta:
        if account_manager.set_active_heygen_account(args.conta):
            logger.info(f"Conta HeyGen ativa definida: {args.conta}")
        else:
            logger.error(f"Falha ao definir conta HeyGen ativa: {args.conta}")
            return 1

    # Criar diretórios necessários
    criar_diretorios()

    # Encontrar arquivos de áudio
    if args.timestamp:
        # Usar um padrão mais flexível para encontrar todos os arquivos com o timestamp base
        audio_files = sorted(glob.glob(f"output/audio/rapidinha_secao_*_{args.timestamp}*.mp3"))
    else:
        # Encontrar o timestamp mais recente
        all_audio_files = glob.glob("output/audio/rapidinha_secao_*.mp3")
        if not all_audio_files:
            logger.error("Nenhum arquivo de áudio encontrado.")
            return 1

        # Extrair timestamps
        timestamps = set()
        for file in all_audio_files:
            parts = os.path.basename(file).split("_")
            if len(parts) >= 4:
                # Formato: rapidinha_secao_1_20250513_201745.mp3
                # Queremos extrair 20250513_201745
                timestamp = "_".join(parts[3:]).split(".")[0]
                timestamps.add(timestamp)

        if not timestamps:
            logger.error("Não foi possível extrair timestamps dos arquivos de áudio.")
            return 1

        # Usar o timestamp mais recente
        latest_timestamp = sorted(timestamps)[-1]
        logger.info(f"Timestamp mais recente: {latest_timestamp}")

        # Verificar se o timestamp contém um underscore
        if "_" in latest_timestamp:
            # Formato: 20250513_201745
            audio_files = sorted(glob.glob(f"output/audio/rapidinha_secao_*_{latest_timestamp}.mp3"))
        else:
            # Formato antigo: 20250513
            audio_files = sorted(glob.glob(f"output/audio/rapidinha_secao_*_{latest_timestamp}*.mp3"))
        logger.info(f"Usando arquivos de áudio com timestamp {latest_timestamp}")

    if not audio_files:
        logger.error("Nenhum arquivo de áudio encontrado.")
        return 1

    logger.info(f"Encontrados {len(audio_files)} arquivos de áudio:")
    for audio_file in audio_files:
        logger.info(f"  - {audio_file}")

    # Gerar vídeo para cada seção
    video_files = []
    for audio_file in audio_files:
        logger.info(f"Gerando vídeo para {audio_file}...")
        video_path = gerar_video_para_secao(audio_file, args.dry_run)
        if video_path:
            video_files.append(video_path)
        else:
            logger.error(f"Falha ao gerar vídeo para {audio_file}")

    # Exibir resultado
    if video_files:
        logger.info(f"Gerados {len(video_files)} vídeos com sucesso!")
        for video_file in video_files:
            logger.info(f"  - {video_file}")

            # Abrir os arquivos se solicitado
            if not args.no_abrir and not args.dry_run:
                abrir_arquivo(video_file)
    else:
        logger.error("Nenhum vídeo foi gerado.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
