"""
Módulo para gerar vídeos usando a API do HeyGen.
"""
import os
import json
import time
import logging
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('heygen_video_generator')

# Carregar variáveis de ambiente
load_dotenv()

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
        # Carregar a chave da API
        self.api_key = api_key or self._load_api_key()

        # URLs base da API
        self.api_base_url = "https://api.heygen.com/v1"
        self.api_base_url_v2 = "https://api.heygen.com/v2"
        self.upload_base_url = "https://upload.heygen.com/v1"

        # Diretório para armazenar os vídeos gerados
        self.videos_dir = os.path.join(os.getcwd(), "output", "videos")
        os.makedirs(self.videos_dir, exist_ok=True)

        # Carregar configuração do avatar
        self.avatar_id = None
        self.avatar_name = "Rapidinha Avatar"
        self._load_avatar_config()

        logger.info(f"HeyGenVideoGenerator inicializado com avatar: {self.avatar_name} (ID: {self.avatar_id})")

    def _load_api_key(self) -> Optional[str]:
        """
        Carrega a chave da API do ambiente ou do arquivo .env.

        Returns:
            Optional[str]: A chave da API ou None se não encontrada
        """
        # Tentar obter do ambiente
        api_key = os.getenv("HEYGEN_API_KEY")

        # Se não conseguir, tentar ler diretamente do arquivo .env
        if not api_key:
            try:
                with open('.env', 'r') as f:
                    for line in f:
                        if line.startswith('HEYGEN_API_KEY='):
                            api_key = line.strip().split('=', 1)[1].strip('"').strip("'")
                            break
            except Exception as e:
                logger.error(f"Erro ao ler arquivo .env: {e}")

        if not api_key:
            logger.warning("API key do HeyGen não encontrada. A geração de vídeo não funcionará.")
        else:
            logger.info(f"API key do HeyGen encontrada: {api_key[:5]}...{api_key[-5:]}")

        return api_key

    def _load_avatar_config(self):
        """
        Carrega a configuração do avatar de um arquivo.
        """
        config_path = os.path.join(os.getcwd(), "config", "avatar_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.avatar_id = config.get("avatar_id")
                    self.avatar_name = config.get("avatar_name", "Rapidinha Avatar")
                    logger.info(f"Configuração de avatar carregada. ID: {self.avatar_id}, Nome: {self.avatar_name}")
            except Exception as e:
                logger.error(f"Erro ao carregar configuração de avatar: {e}")

    def _save_avatar_config(self, avatar_id: str, avatar_name: str):
        """
        Salva a configuração do avatar em um arquivo.

        Args:
            avatar_id: ID do avatar
            avatar_name: Nome do avatar
        """
        config_path = os.path.join(os.getcwd(), "config", "avatar_config.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

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

    def list_avatars(self) -> List[Dict]:
        """
        Lista os avatares disponíveis na conta do HeyGen.

        Returns:
            List[Dict]: Lista de avatares disponíveis
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

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição à API: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Resposta: {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Erro ao listar avatares: {e}")
            return []

    def create_avatar_from_video(self, video_path: str, avatar_name: Optional[str] = None,
                             dry_run: bool = False) -> Optional[str]:
        """
        Cria um avatar a partir de um vídeo.

        Args:
            video_path: Caminho para o vídeo
            avatar_name: Nome do avatar (se None, usa o nome padrão)
            dry_run: Se True, simula a criação sem fazer chamadas de API

        Returns:
            Optional[str]: ID do avatar criado, ou None se falhar
        """
        if not self.api_key and not dry_run:
            logger.error("API key do HeyGen não configurada. Não é possível criar avatar.")
            return None

        if not os.path.exists(video_path):
            logger.error(f"Vídeo não encontrado: {video_path}")
            return None

        # Nome do avatar
        if not avatar_name:
            avatar_name = self.avatar_name

        # Modo de simulação
        if dry_run:
            logger.info(f"[SIMULAÇÃO] Criaria avatar '{avatar_name}' a partir do vídeo: {video_path}")

            # Criar um ID de avatar simulado
            import hashlib
            simulated_id = hashlib.md5(f"{avatar_name}_{video_path}".encode()).hexdigest()[:24]

            # Salvar uma configuração simulada
            self.avatar_id = simulated_id
            self.avatar_name = avatar_name
            self._save_avatar_config(simulated_id, avatar_name)

            logger.info(f"[SIMULAÇÃO] ID de avatar simulado: {simulated_id}")
            return simulated_id

        try:
            # Determinar o tipo de conteúdo com base na extensão do arquivo
            file_extension = os.path.splitext(video_path)[1][1:].lower()
            content_type = "video/mp4"  # Padrão para MP4
            if file_extension == "webm":
                content_type = "video/webm"

            # Fazer upload do vídeo
            logger.info(f"Fazendo upload do vídeo {video_path}...")

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

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição à API: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Resposta: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Erro ao criar avatar: {e}")
            return None

    def generate_video(self, script: str, audio_path: Optional[str] = None,
                     output_path: Optional[str] = None, folder_name: Optional[str] = None,
                     avatar_id: Optional[str] = None, voice_id: Optional[str] = None,
                     dry_run: bool = False) -> Optional[str]:
        """
        Gera um vídeo usando o avatar e o script fornecidos.

        Args:
            script: Texto do script
            audio_path: Caminho para o arquivo de áudio (se fornecido, usa este áudio em vez de gerar um novo)
            output_path: Caminho para salvar o vídeo (se None, gera um nome baseado no timestamp)
            folder_name: Nome da pasta no HeyGen onde o vídeo será salvo (se None, não usa pasta específica)
            avatar_id: ID do avatar a ser usado (se None, usa o avatar configurado ou um avatar padrão)
            voice_id: ID da voz a ser usada (se None, usa uma voz padrão em português)
            dry_run: Se True, simula a geração sem fazer chamadas de API

        Returns:
            Optional[str]: Caminho para o vídeo gerado, ou None se falhar
        """
        if not self.api_key and not dry_run:
            logger.error("API key do HeyGen não configurada. Não é possível gerar vídeo.")
            return None

        # Determinar o avatar a ser usado
        if avatar_id:
            logger.info(f"Usando avatar fornecido (ID: {avatar_id})")
        elif self.avatar_id:
            avatar_id = self.avatar_id
            logger.info(f"Usando avatar configurado (ID: {avatar_id})")
        else:
            avatar_id = "Daisy-inshirt-20220818"  # Avatar padrão
            logger.info(f"Usando avatar padrão (ID: {avatar_id})")

        # Determinar a voz a ser usada
        if not voice_id:
            voice_id = "7e4e469711394247bb252ff848ac061d"  # Tiago Costa (português)
            logger.info(f"Usando voz padrão (ID: {voice_id})")

        # Gerar nome de saída se não for fornecido
        if not output_path:
            timestamp = int(time.time())
            output_path = os.path.join(self.videos_dir, f"rapidinha_heygen_{timestamp}.mp4")

        # Modo de simulação
        if dry_run:
            logger.info(f"[SIMULAÇÃO] Geraria vídeo com avatar ID: {avatar_id}")
            if audio_path and os.path.exists(audio_path):
                logger.info(f"[SIMULAÇÃO] Usaria áudio: {audio_path}")
            else:
                logger.info(f"[SIMULAÇÃO] Geraria áudio a partir do script com voz ID: {voice_id}")

            if folder_name:
                logger.info(f"[SIMULAÇÃO] Salvaria na pasta '{folder_name}' do HeyGen")

            logger.info(f"[SIMULAÇÃO] Salvaria vídeo em: {output_path}")
            return output_path

        try:
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
                    "width": 1280,
                    "height": 720
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
                    "voice_id": voice_id
                }

            # Criar o vídeo
            logger.info("Gerando vídeo com o HeyGen...")
            logger.debug(f"Dados da requisição: {json.dumps(video_data, indent=2)}")

            # Fazer a requisição para criar o vídeo
            video_response = requests.post(video_url, headers=headers, json=video_data)

            if video_response.status_code != 200:
                logger.error(f"Erro: {video_response.status_code}")
                logger.error(f"Resposta: {video_response.text}")
                return None

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

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição à API: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Resposta: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Erro ao gerar vídeo: {e}")
            return None


def open_video_file(file_path: str) -> bool:
    """
    Abre um arquivo de vídeo com o player padrão do sistema.

    Args:
        file_path: Caminho para o arquivo de vídeo

    Returns:
        bool: True se bem-sucedido, False caso contrário
    """
    if not os.path.exists(file_path):
        logger.error(f"Arquivo de vídeo não encontrado: {file_path}")
        return False

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

        logger.info(f"Arquivo de vídeo aberto: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao abrir arquivo de vídeo: {e}")
        return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gerador de vídeos para o Clone Rapidinha no Cripto")
    parser.add_argument("--list-avatars", action="store_true", help="Listar avatares disponíveis")
    parser.add_argument("--create-avatar", metavar="VIDEO_PATH", help="Criar um avatar a partir de um vídeo")
    parser.add_argument("--avatar-name", help="Nome do avatar a ser criado")
    parser.add_argument("--generate", action="store_true", help="Gerar um vídeo com o avatar configurado")
    parser.add_argument("--script", help="Texto do script para o vídeo")
    parser.add_argument("--audio", help="Caminho para o arquivo de áudio")
    parser.add_argument("--avatar-id", help="ID do avatar a ser usado (opcional)")
    parser.add_argument("--voice-id", help="ID da voz a ser usada (opcional)")
    parser.add_argument("--play", action="store_true", help="Reproduzir o vídeo gerado")
    parser.add_argument("--dry-run", action="store_true", help="Simular operações sem fazer chamadas de API")

    args = parser.parse_args()

    generator = HeyGenVideoGenerator()

    if args.list_avatars:
        generator.list_avatars()

    elif args.create_avatar:
        generator.create_avatar_from_video(args.create_avatar, args.avatar_name, dry_run=args.dry_run)

    elif args.generate:
        if not args.script and not args.audio:
            logger.error("Erro: Você deve fornecer um script ou um arquivo de áudio.")
        else:
            video_path = generator.generate_video(
                args.script,
                args.audio,
                avatar_id=args.avatar_id,
                voice_id=args.voice_id,
                dry_run=args.dry_run
            )

            if video_path and args.play and not args.dry_run:
                open_video_file(video_path)
