#!/usr/bin/env python3
"""
Script simples para gerar um Reels a partir de um script existente.
"""
import os
import sys
import logging
import argparse
from datetime import datetime

# Carregar variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger_env = logging.getLogger('env_loader')
    logger_env.info("Arquivo .env carregado com sucesso")
except ImportError:
    print("Pacote python-dotenv não encontrado. As variáveis de ambiente precisam ser definidas manualmente.")
except Exception as e:
    print(f"Erro ao carregar arquivo .env: {e}")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('reels_simples')

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

def gerar_audio(script_path, dry_run=False):
    """
    Gera o áudio para o script.

    Args:
        script_path: Caminho para o arquivo de script
        dry_run: Se True, simula a geração sem fazer chamadas de API

    Returns:
        str: Caminho para o arquivo de áudio
    """
    import os
    from datetime import datetime

    logger.info(f"Gerando áudio para o script: {script_path}")

    if dry_run:
        logger.info("[SIMULAÇÃO] Gerando áudio...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = os.path.join("output", "audio", f"rapidinha_audio_{timestamp}.mp3")
        logger.info(f"[SIMULAÇÃO] Áudio seria salvo em: {audio_path}")
        return audio_path

    try:
        # Importar o gerador de áudio
        import elevenlabs
        import os
        import json
        import requests

        # Verificar API key
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            logger.error("API key do ElevenLabs não encontrada.")
            return None

        # Usar a chave diretamente se necessário
        if api_key == "sua_chave_aqui":
            api_key = "sk_2eeadfe816f7442422d9a3a508e5d912797de421403ba9d6"

        logger.info(f"Usando API key do ElevenLabs: {api_key[:10]}...")

        # Ler o script
        with open(script_path, "r", encoding="utf-8") as f:
            texto = f.read()

        # Usar a voz FlukakuIA
        voice_id = "oG30eP3GaYrCwnabbDCw"  # FlukakuIA

        # Configurações de voz otimizadas
        voice_settings = {
            "stability": 0.71,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }

        # Usar a API REST diretamente
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }

        payload = {
            "text": texto,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": voice_settings
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            logger.error(f"Erro ao gerar áudio: {response.text}")
            return None

        # O áudio está no conteúdo da resposta
        audio = response.content

        # Salvar áudio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = os.path.join("output", "audio", f"rapidinha_audio_{timestamp}.mp3")

        with open(audio_path, "wb") as f:
            f.write(audio)

        logger.info(f"Áudio gerado com sucesso: {audio_path}")
        return audio_path

    except Exception as e:
        logger.error(f"Erro ao gerar áudio: {e}")
        return None

def gerar_video(audio_path, dry_run=False):
    """
    Gera o vídeo para o áudio.

    Args:
        audio_path: Caminho para o arquivo de áudio
        dry_run: Se True, simula a geração sem fazer chamadas de API

    Returns:
        str: Caminho para o arquivo de vídeo
    """
    import os
    from datetime import datetime

    logger.info(f"Gerando vídeo para o áudio: {audio_path}")

    if dry_run:
        logger.info("[SIMULAÇÃO] Gerando vídeo...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = os.path.join("output", "videos", f"rapidinha_video_{timestamp}.mp4")
        logger.info(f"[SIMULAÇÃO] Vídeo seria salvo em: {video_path}")
        return video_path

    try:
        # Importar bibliotecas necessárias
        import requests
        import json
        import time

        # Verificar API key
        api_key = os.environ.get("HEYGEN_API_KEY")
        if not api_key:
            logger.error("API key do HeyGen não encontrada.")
            return None

        # Usar a chave diretamente se necessário
        if api_key == "sua_chave_aqui":
            api_key = "OTU2YjcxM2ZhZGY2NDE5Mjg3MzYzMmZlNjEyYjZiNzUtMTc0Njc1NzMxNQ=="

        logger.info(f"Usando API key do HeyGen: {api_key[:10]}...")

        # ID do avatar padrão do Flukaku
        avatar_id = "431f819b1a8e42bb8f095e98e1e805a4"

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

        max_attempts = 60  # Aumentar para 60 tentativas
        attempts = 0
        wait_time = 20  # Aguardar 20 segundos entre as verificações

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

                # Baixar vídeo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                video_path = os.path.join("output", "videos", f"rapidinha_video_{timestamp}.mp4")

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
    parser = argparse.ArgumentParser(description="Gerador simples de Reels")
    parser.add_argument("script", help="Caminho para o arquivo de script")
    parser.add_argument("--dry-run", action="store_true", help="Simular operações sem fazer chamadas de API")
    parser.add_argument("--no-abrir", action="store_true", help="Não abrir os arquivos gerados")
    parser.add_argument("--debug", action="store_true", help="Ativar modo de depuração")

    args = parser.parse_args()

    # Configurar nível de log
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Verificar se o script existe
    if not os.path.exists(args.script):
        logger.error(f"Script não encontrado: {args.script}")
        return 1

    # Criar diretórios necessários
    criar_diretorios()

    # Gerar áudio
    audio_path = gerar_audio(args.script, args.dry_run)
    if not audio_path:
        logger.error("Falha ao gerar áudio")
        return 1

    # Gerar vídeo
    video_path = gerar_video(audio_path, args.dry_run)
    if not video_path:
        logger.error("Falha ao gerar vídeo")
        return 1

    # Exibir resultado
    logger.info("Reels gerado com sucesso!")
    logger.info(f"Script: {args.script}")
    logger.info(f"Áudio: {audio_path}")
    logger.info(f"Vídeo: {video_path}")

    if args.dry_run:
        logger.info("NOTA: Este foi um teste em modo de simulação. Nenhum recurso de API foi consumido.")

    # Abrir os arquivos se solicitado
    if not args.no_abrir:
        abrir_arquivo(args.script)
        if not args.dry_run:
            abrir_arquivo(video_path)

    return 0

if __name__ == "__main__":
    sys.exit(main())
