#!/usr/bin/env python3
"""
Módulo otimizado para gerar vídeos usando a API do HeyGen.
"""
import os
import json
import time
import logging
import requests
from typing import Dict, List, Optional, Any, Union

from core.utils import (
    load_heygen_api_key, ensure_directory, get_timestamp_filename,
    PROJECT_ROOT, OUTPUT_DIR
)

# Configure logging
logger = logging.getLogger('cloneia.heygen')

class HeyGenVideoGenerator:
    """
    Classe para gerar vídeos usando a API do HeyGen.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o gerador de vídeos do HeyGen.

        Args:
            api_key: Chave da API do HeyGen (se None, tentará carregar do ambiente)
        """
        # Chave da API HeyGen
        self.api_key = api_key or load_heygen_api_key()

        if not self.api_key:
            logger.warning("API key do HeyGen não configurada. A geração de vídeo não funcionará.")
        else:
            logger.info(f"API key do HeyGen: {self.api_key[:5]}...{self.api_key[-5:]}")

        # URLs base da API
        self.api_base_url = "https://api.heygen.com/v1"
        self.api_base_url_v2 = "https://api.heygen.com/v2"
        self.upload_base_url = "https://upload.heygen.com/v1"

        # Diretório para armazenar os vídeos gerados
        self.videos_dir = os.path.join(OUTPUT_DIR, "videos")
        ensure_directory(self.videos_dir)

        # Carregar configuração do avatar se existir
        self.avatar_id = None
        self.avatar_name = "Rapidinha Avatar"
        self._load_avatar_config()

    def _load_avatar_config(self):
        """
        Carrega a configuração do avatar de um arquivo.
        """
        config_path = os.path.join(PROJECT_ROOT, "config", "avatar_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.avatar_id = config.get("avatar_id")
                    self.avatar_name = config.get("avatar_name", "Rapidinha Avatar")
                    logger.info(f"Configuração de avatar carregada. ID: {self.avatar_id}, Nome: {self.avatar_name}")
            except Exception as e:
                logger.error(f"Erro ao carregar configuração de avatar: {e}")

    def _save_avatar_config(self, avatar_id, avatar_name):
        """
        Salva a configuração do avatar em um arquivo.

        Args:
            avatar_id (str): ID do avatar.
            avatar_name (str): Nome do avatar.
        """
        config_path = os.path.join(PROJECT_ROOT, "config", "avatar_config.json")
        ensure_directory(os.path.dirname(config_path))

        config = {
            "avatar_id": avatar_id,
            "avatar_name": avatar_name,
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            logger.info(f"Configuração de avatar salva em {config_path}")
        except Exception as e:
            logger.error(f"Erro ao salvar configuração de avatar: {e}")

    def list_avatars(self):
        """
        Lista os avatares disponíveis na conta do HeyGen.

        Returns:
            list: Lista de avatares disponíveis.
        """
        if not self.api_key:
            logger.error("API key do HeyGen não configurada. Não é possível listar avatares.")
            return []

        try:
            url = f"{self.api_base_url_v2}/avatars"
            headers = {
                "X-Api-Key": self.api_key,
                "Content-Type": "application/json"
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            result = response.json()
            avatars = result.get("data", {}).get("avatars", [])

            logger.info(f"Encontrados {len(avatars)} avatares:")
            for i, avatar in enumerate(avatars, 1):
                logger.info(f"{i}. {avatar.get('avatar_name')} (ID: {avatar.get('avatar_id')})")

            return avatars

        except Exception as e:
            logger.error(f"Erro ao listar avatares: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Resposta: {e.response.text}")
            return []

    def create_avatar_from_video(self, video_path, avatar_name=None):
        """
        Cria um avatar a partir de um vídeo.

        Args:
            video_path (str): Caminho para o vídeo.
            avatar_name (str, optional): Nome do avatar. Se None, usa o nome padrão.

        Returns:
            str: ID do avatar criado, ou None se falhar.
        """
        if not self.api_key:
            logger.error("API key do HeyGen não configurada. Não é possível criar avatar.")
            return None

        if not os.path.exists(video_path):
            logger.error(f"Vídeo não encontrado: {video_path}")
            return None

        try:
            # Nome do avatar
            if not avatar_name:
                avatar_name = self.avatar_name

            # Fazer upload do vídeo
            logger.info(f"Fazendo upload do vídeo {video_path}...")

            # Determinar o tipo de conteúdo com base na extensão do arquivo
            file_extension = os.path.splitext(video_path)[1][1:].lower()
            content_type = "video/mp4"  # Padrão para MP4
            if file_extension == "webm":
                content_type = "video/webm"

            # Configurar cabeçalhos para upload
            upload_url = f"{self.upload_base_url}/asset"
            upload_headers = {
                "X-Api-Key": self.api_key,
                "Content-Type": content_type
            }

            # Fazer upload do vídeo diretamente
            with open(video_path, 'rb') as f:
                video_data = f.read()

            upload_response = requests.post(upload_url, headers=upload_headers, data=video_data)
            upload_response.raise_for_status()

            # Processar a resposta
            upload_result = upload_response.json()
            asset_id = upload_result.get("data", {}).get("id")

            if not asset_id:
                logger.error("Falha ao fazer upload do vídeo. Nenhum ID de asset retornado.")
                logger.error(f"Resposta: {upload_result}")
                return None

            logger.info(f"Vídeo enviado com sucesso. Asset ID: {asset_id}")

            # Criar o avatar usando a API v2
            logger.info(f"Criando avatar '{avatar_name}' a partir do vídeo...")

            avatar_url = f"{self.api_base_url_v2}/avatar/create"
            avatar_headers = {
                "X-Api-Key": self.api_key,
                "Content-Type": "application/json"
            }
            avatar_data = {
                "name": avatar_name,
                "asset_id": asset_id,  # Usar o asset_id obtido do upload
                "avatar_type": "talking_photo"  # ou "digital_human" dependendo do tipo desejado
            }

            avatar_response = requests.post(avatar_url, headers=avatar_headers, json=avatar_data)
            avatar_response.raise_for_status()

            avatar_result = avatar_response.json()
            avatar_id = avatar_result.get("data", {}).get("id")

            if avatar_id:
                logger.info(f"Avatar criado com sucesso! ID: {avatar_id}")

                # Salvar a configuração do avatar
                self.avatar_id = avatar_id
                self.avatar_name = avatar_name
                self._save_avatar_config(avatar_id, avatar_name)

                return avatar_id
            else:
                logger.error("Falha ao criar avatar. Nenhum ID de avatar retornado.")
                return None

        except Exception as e:
            logger.error(f"Erro ao criar avatar: {e}")
            return None

    def generate_video(self, script, audio_path=None, output_path=None, folder_name=None, avatar_id=None, voice_id=None):
        """
        Gera um vídeo usando o avatar e o script fornecidos.

        Args:
            script (str): Texto do script.
            audio_path (str, optional): Caminho para o arquivo de áudio. Se fornecido, usa este áudio em vez de gerar um novo.
            output_path (str, optional): Caminho para salvar o vídeo. Se None, gera um nome baseado no timestamp.
            folder_name (str, optional): Nome da pasta no HeyGen onde o vídeo será salvo. Se None, não usa pasta específica.
            avatar_id (str, optional): ID do avatar a ser usado. Se None, usa o avatar configurado ou um avatar padrão.
            voice_id (str, optional): ID da voz a ser usada. Se None, usa uma voz padrão em português.

        Returns:
            str: Caminho para o vídeo gerado, ou None se falhar.
        """
        if not self.api_key:
            logger.error("API key do HeyGen não configurada. Não é possível gerar vídeo.")
            return None

        # Usar avatar_id fornecido, ou o configurado, ou um avatar padrão
        if avatar_id:
            logger.info(f"Usando avatar fornecido (ID: {avatar_id})")
        elif self.avatar_id:
            avatar_id = self.avatar_id
            logger.info(f"Usando avatar configurado (ID: {avatar_id})")
        else:
            avatar_id = "Daisy-inshirt-20220818"  # Avatar padrão
            logger.info(f"Usando avatar padrão (ID: {avatar_id})")

        # Usar voice_id fornecido ou um padrão
        if not voice_id:
            voice_id = "7e4e469711394247bb252ff848ac061d"  # Tiago Costa (português)
            logger.info(f"Usando voz padrão (ID: {voice_id})")

        try:
            # Gerar nome de saída se não for fornecido
            if not output_path:
                filename = get_timestamp_filename("rapidinha_heygen", "mp4")
                output_path = os.path.join(self.videos_dir, filename)

            # Preparar os dados para a requisição usando a API v2
            video_url = f"{self.api_base_url_v2}/video/generate"
            headers = {
                "X-Api-Key": self.api_key,
                "Content-Type": "application/json"
            }

            # Configurar os dados do vídeo
            video_data = {
                "video_inputs": [
                    {
                        "character": {
                            "type": "avatar",
                            "avatar_id": avatar_id,
                            "avatar_style": "normal"
                        },
                        "background": {
                            "type": "color",
                            "value": "#121212"  # Cor de fundo (preto)
                        }
                    }
                ],
                "dimension": {
                    "width": 1080,
                    "height": 1920
                },
                "caption": False  # Não adicionar legendas
            }

            # Adicionar pasta se especificada
            if folder_name:
                video_data["folder_name"] = folder_name
                logger.info(f"Salvando vídeo na pasta '{folder_name}' do HeyGen")

            # Adicionar áudio ou texto
            if audio_path and os.path.exists(audio_path):
                # Fazer upload do áudio
                logger.info(f"Fazendo upload do áudio {audio_path}...")

                # Configurar cabeçalhos para upload
                upload_url = f"{self.upload_base_url}/asset"
                upload_headers = {
                    "X-Api-Key": self.api_key,
                    "Content-Type": "audio/mpeg"
                }

                # Fazer upload do áudio diretamente
                with open(audio_path, 'rb') as f:
                    audio_data = f.read()

                upload_response = requests.post(upload_url, headers=upload_headers, data=audio_data)
                upload_response.raise_for_status()

                # Processar a resposta
                upload_result = upload_response.json()
                audio_asset_id = upload_result.get("data", {}).get("id")

                if not audio_asset_id:
                    logger.error("Falha ao fazer upload do áudio. Nenhum ID de asset retornado.")
                    logger.error(f"Resposta: {upload_result}")
                    return None

                logger.info(f"Áudio enviado com sucesso. Asset ID: {audio_asset_id}")

                # Adicionar o áudio aos dados do vídeo
                video_data["video_inputs"][0]["voice"] = {
                    "type": "audio",
                    "audio_asset_id": audio_asset_id
                }
            else:
                # Usar texto para gerar áudio
                video_data["video_inputs"][0]["voice"] = {
                    "type": "text",
                    "input_text": script,
                    "voice_id": voice_id  # ID da voz em português
                }

            # Criar o vídeo
            logger.info("Gerando vídeo com o HeyGen...")
            logger.debug(f"Dados da requisição: {json.dumps(video_data, indent=2)}")

            try:
                video_response = requests.post(video_url, headers=headers, json=video_data)
                logger.info(f"Status code: {video_response.status_code}")

                if video_response.status_code == 200:
                    video_result = video_response.json()
                    logger.debug(f"Resposta: {json.dumps(video_result, indent=2)}")

                    # Verificar se o ID do vídeo está na resposta
                    if "data" in video_result and "video_id" in video_result["data"]:
                        video_id = video_result["data"]["video_id"]
                    elif "data" in video_result and "id" in video_result["data"]:
                        video_id = video_result["data"]["id"]
                    else:
                        logger.error("Falha ao criar vídeo. Nenhum ID de vídeo retornado.")
                        logger.error(f"Resposta completa: {video_result}")
                        return None
                else:
                    logger.error(f"Erro: {video_response.status_code}")
                    logger.error(f"Resposta: {video_response.text}")
                    return None
            except Exception as e:
                logger.error(f"Erro ao criar vídeo: {e}")
                return None

            # Verificar o status do vídeo e baixá-lo quando estiver pronto
            logger.info(f"Vídeo em processamento (ID: {video_id}). Aguardando conclusão...")

            status_url = f"{self.api_base_url}/video_status.get?video_id={video_id}"
            max_attempts = 60  # 5 minutos (5 segundos por tentativa)

            for attempt in range(max_attempts):
                status_response = requests.get(status_url, headers=headers)
                status_response.raise_for_status()

                status_result = status_response.json()
                status = status_result.get("data", {}).get("status")

                if status == "completed":
                    # Vídeo pronto, baixar
                    video_url = status_result.get("data", {}).get("video_url")

                    if video_url:
                        try:
                            logger.info(f"Vídeo pronto! Baixando de {video_url}...")
                            video_content_response = requests.get(video_url)
                            video_content_response.raise_for_status()

                            with open(output_path, 'wb') as f:
                                f.write(video_content_response.content)

                            logger.info(f"Vídeo salvo em {output_path}")

                            # Salvar uma cópia do vídeo com o ID para referência
                            video_id_path = os.path.join(os.path.dirname(output_path), f"heygen_{video_id}.mp4")
                            with open(video_id_path, 'wb') as f:
                                f.write(video_content_response.content)

                            logger.info(f"Cópia do vídeo salva em {video_id_path}")

                            return output_path
                        except Exception as e:
                            logger.error(f"Erro ao baixar o vídeo: {e}")
                            return None
                    else:
                        logger.error("URL do vídeo não encontrada na resposta.")
                        return None

                elif status == "failed":
                    logger.error("Falha ao processar o vídeo.")
                    return None

                # Aguardar 5 segundos antes de verificar novamente
                logger.info(f"Status do vídeo: {status}. Verificando novamente em 5 segundos...")
                time.sleep(5)

            logger.error("Tempo limite excedido ao aguardar o processamento do vídeo.")
            return None

        except Exception as e:
            logger.error(f"Erro ao gerar vídeo: {e}")
            return None


if __name__ == "__main__":
    import argparse

    # Configure logging for command-line usage
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(description="Gerador de vídeos usando a API do HeyGen")
    parser.add_argument("--list-avatars", action="store_true", help="Listar avatares disponíveis")
    parser.add_argument("--create-avatar", metavar="VIDEO_PATH", help="Criar um avatar a partir de um vídeo")
    parser.add_argument("--avatar-name", help="Nome do avatar a ser criado")
    parser.add_argument("--generate", action="store_true", help="Gerar um vídeo com o avatar configurado")
    parser.add_argument("--script", help="Texto do script para o vídeo")
    parser.add_argument("--audio", help="Caminho para o arquivo de áudio")
    parser.add_argument("--avatar-id", help="ID do avatar a ser usado (opcional)")
    parser.add_argument("--voice-id", help="ID da voz a ser usada (opcional)")

    args = parser.parse_args()

    generator = HeyGenVideoGenerator()

    if args.list_avatars:
        generator.list_avatars()

    elif args.create_avatar:
        generator.create_avatar_from_video(args.create_avatar, args.avatar_name)

    elif args.generate:
        if not args.script and not args.audio:
            logger.error("Erro: Você deve fornecer um script ou um arquivo de áudio.")
        else:
            generator.generate_video(args.script, args.audio, avatar_id=args.avatar_id, voice_id=args.voice_id)
