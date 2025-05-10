#!/usr/bin/env python3
"""
Script para gerar um vídeo de reel com configurações otimizadas.
"""
import os
import json
import logging
import requests
from typing import Optional
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('reel_generator')

# Importar utilitários do projeto
try:
    from core.utils import load_elevenlabs_api_key, load_heygen_api_key, AVATAR_ID
    using_core_utils = True
except ImportError:
    logger.warning("Módulo core.utils não encontrado, usando implementação local")
    using_core_utils = False
    from dotenv import load_dotenv
    load_dotenv()

class ReelVideoGenerator:
    """
    Classe para gerar vídeos de reels com áudio otimizado.
    """

    def __init__(self, voice_profile: Optional[str] = None):
        """
        Inicializa o gerador de vídeo para reels.

        Args:
            voice_profile: Nome do perfil de voz a ser usado (se None, usa o padrão)
        """
        # Carregar API keys
        if using_core_utils:
            self.elevenlabs_api_key = load_elevenlabs_api_key()
            self.heygen_api_key = load_heygen_api_key()
        else:
            self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
            self.heygen_api_key = os.getenv("HEYGEN_API_KEY")

        if not self.elevenlabs_api_key:
            raise ValueError("API key do ElevenLabs não encontrada.")

        if not self.heygen_api_key:
            raise ValueError("API key do HeyGen não encontrada.")

        self.elevenlabs_api_base_url = "https://api.elevenlabs.io"
        self.heygen_api_base_url = "https://api.heygen.com"

        # Carregar configuração de voz existente
        self.voice_id = None
        self.voice_name = None
        self.voice_settings = None

        self._load_voice_config(voice_profile)

        # Avatar ID do HeyGen
        if using_core_utils:
            self.avatar_id = AVATAR_ID
        else:
            self.avatar_id = "84aa751d70e24c8eb5a12cac86762e6a"  # Avatar padrão

        logger.info(f"ReelVideoGenerator inicializado com avatar ID: {self.avatar_id}")
        logger.info(f"Voz configurada: {self.voice_name} (ID: {self.voice_id})")

    def _load_voice_config(self, profile_name: Optional[str] = None):
        """
        Carrega a configuração de voz existente.

        Args:
            profile_name: Nome do perfil de voz a ser carregado
        """
        # Determinar o caminho do arquivo de configuração
        if profile_name:
            config_path = os.path.join(os.getcwd(), "config", f"voice_config_{profile_name}.json")
        else:
            config_path = os.path.join(os.getcwd(), "config", "voice_config.json")

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.voice_id = config.get("voice_id")
                    self.voice_name = config.get("voice_name")

                    if "settings" in config:
                        self.voice_settings = config["settings"]

                logger.info(f"Configuração de voz carregada: {self.voice_name} (ID: {self.voice_id})")
            except Exception as e:
                logger.error(f"Erro ao carregar configuração de voz: {e}")
        else:
            logger.warning(f"Arquivo de configuração não encontrado: {config_path}")

    def generate_reel_audio(self, script_path: str, reel_settings: Optional[dict] = None,
                         optimize: bool = True, dry_run: bool = False) -> Optional[str]:
        """
        Gera áudio otimizado para reels.

        Args:
            script_path: Caminho para o arquivo de script
            reel_settings: Configurações personalizadas para o áudio
            optimize: Se True, otimiza o texto para fala natural
            dry_run: Se True, simula a geração sem fazer chamadas de API

        Returns:
            Optional[str]: Caminho para o arquivo de áudio gerado, ou None se falhar
        """
        if not self.voice_id:
            logger.error("Nenhuma voz clonada encontrada.")
            return None

        # Ler o script
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
        except Exception as e:
            logger.error(f"Erro ao ler o script: {e}")
            return None

        logger.info(f"Script carregado: {script_path}")
        logger.info(f"Conteúdo: {script_content[:50]}...")

        # Otimizar o texto se solicitado
        if optimize:
            try:
                # Tentar usar a função do core.utils
                if using_core_utils:
                    from core.utils import optimize_text
                    original_content = script_content
                    script_content = optimize_text(script_content)
                    logger.info(f"Texto otimizado: {len(original_content)} -> {len(script_content)} caracteres")
                else:
                    logger.info("Otimização de texto não disponível (core.utils não encontrado)")
            except Exception as e:
                logger.warning(f"Erro ao otimizar texto: {e}")

        # Configurações para reels
        if not reel_settings:
            reel_settings = {
                "stability": 0.15,           # Estabilidade para melhor fluidez
                "similarity_boost": 0.65,     # Reduzida para mais naturalidade
                "style": 0.85,               # Estilo para capturar a entonação carioca
                "use_speaker_boost": True,    # Melhorar a qualidade do áudio
                "model_id": "eleven_multilingual_v2"  # Modelo multilíngue avançado
            }

        # Diretório para o áudio
        output_dir = os.path.join(os.getcwd(), "output", "audio")
        os.makedirs(output_dir, exist_ok=True)

        # Timestamp para o arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"reel_audio_{timestamp}.mp3")

        # Modo de simulação
        if dry_run:
            logger.info(f"[SIMULAÇÃO] Geraria áudio para o script: {script_path}")
            logger.info(f"[SIMULAÇÃO] Usaria voz: {self.voice_name} (ID: {self.voice_id})")
            logger.info(f"[SIMULAÇÃO] Salvaria em: {output_path}")
            return output_path

        try:
            # Gerar áudio
            url = f"{self.elevenlabs_api_base_url}/v1/text-to-speech/{self.voice_id}"

            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }

            data = {
                "text": script_content,
                "model_id": reel_settings["model_id"],
                "voice_settings": {
                    "stability": reel_settings["stability"],
                    "similarity_boost": reel_settings["similarity_boost"],
                    "style": reel_settings["style"],
                    "use_speaker_boost": reel_settings["use_speaker_boost"]
                }
            }

            logger.info("Gerando áudio otimizado para reels...")
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()

            # Salvar o áudio
            with open(output_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"Áudio salvo em: {output_path}")
            return output_path

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição à API: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Resposta: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Erro ao gerar áudio: {e}")
            return None

    def generate_reel_video(self, audio_path: str, folder_name: str = "augment",
                         dry_run: bool = False) -> Optional[str]:
        """
        Gera um vídeo de reel usando o HeyGen.

        Args:
            audio_path: Caminho para o arquivo de áudio
            folder_name: Nome da pasta no HeyGen onde o vídeo será salvo
            dry_run: Se True, simula a geração sem fazer chamadas de API

        Returns:
            Optional[str]: Caminho para o arquivo de vídeo gerado, ou None se falhar
        """
        if not os.path.exists(audio_path) and not dry_run:
            logger.error(f"Arquivo de áudio não encontrado: {audio_path}")
            return None

        logger.info(f"Gerando vídeo de reel com o áudio: {audio_path}")

        # Diretório para o vídeo
        output_dir = os.path.join(os.getcwd(), "output", "videos")
        os.makedirs(output_dir, exist_ok=True)

        # Timestamp para o arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"reel_video_{timestamp}.mp4")

        # Modo de simulação
        if dry_run:
            logger.info(f"[SIMULAÇÃO] Geraria vídeo com o áudio: {audio_path}")
            logger.info(f"[SIMULAÇÃO] Usaria avatar ID: {self.avatar_id}")
            logger.info(f"[SIMULAÇÃO] Salvaria na pasta '{folder_name}' do HeyGen")
            logger.info(f"[SIMULAÇÃO] Salvaria vídeo em: {output_path}")
            return output_path

        try:
            # Fazer upload do áudio
            logger.info("Fazendo upload do áudio...")

            upload_url = f"{self.heygen_api_base_url}/v1/upload"

            headers = {
                "X-Api-Key": self.heygen_api_key
            }

            with open(audio_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(upload_url, headers=headers, files=files)
                response.raise_for_status()

            upload_data = response.json()
            audio_asset_id = upload_data.get("data", {}).get("asset_id")

            if not audio_asset_id:
                logger.error("Erro: Não foi possível obter o ID do asset de áudio.")
                return None

            logger.info(f"Áudio enviado com sucesso. Asset ID: {audio_asset_id}")

            # Gerar o vídeo
            logger.info("Gerando vídeo com o HeyGen...")

            video_url = f"{self.heygen_api_base_url}/v1/video/generate"

            video_data = {
                "video_inputs": [
                    {
                        "character": {
                            "type": "avatar",
                            "avatar_id": self.avatar_id,
                            "avatar_style": "normal"
                        },
                        "background": {
                            "type": "color",
                            "value": "#121212"  # Cor de fundo (preto)
                        },
                        "voice": {
                            "type": "audio",
                            "audio_asset_id": audio_asset_id
                        }
                    }
                ],
                "dimension": {
                    "width": 1080,  # Dimensão vertical para reels
                    "height": 1920
                },
                "caption": False  # Não adicionar legendas
            }

            # Adicionar pasta se especificada
            if folder_name:
                video_data["folder_name"] = folder_name
                logger.info(f"Salvando vídeo na pasta '{folder_name}' do HeyGen")

            logger.debug(f"Dados da requisição: {json.dumps(video_data, indent=2)}")

            response = requests.post(video_url, headers=headers, json=video_data)
            logger.debug(f"Status code: {response.status_code}")
            logger.debug(f"Resposta: {json.dumps(response.json(), indent=2)}")

            response.raise_for_status()

            video_data = response.json()
            video_id = video_data.get("data", {}).get("video_id")

            if not video_id:
                logger.error("Erro: Não foi possível obter o ID do vídeo.")
                return None

            logger.info(f"Vídeo em processamento (ID: {video_id}). Aguardando conclusão...")

            # Verificar o status do vídeo
            status_url = f"{self.heygen_api_base_url}/v1/video/status"

            # Importar time aqui para evitar importação global não utilizada
            import time
            max_attempts = 60  # 5 minutos (5 segundos por tentativa)

            for attempt in range(max_attempts):
                response = requests.get(f"{status_url}?video_id={video_id}", headers=headers)
                response.raise_for_status()

                status_data = response.json()
                status = status_data.get("data", {}).get("status")

                logger.info(f"Status do vídeo: {status}. Verificando novamente em 5 segundos...")

                if status == "completed":
                    # Vídeo pronto, baixar
                    video_url = status_data.get("data", {}).get("video_url")

                    if not video_url:
                        logger.error("Erro: URL do vídeo não encontrada.")
                        return None

                    logger.info(f"Vídeo pronto! Baixando de {video_url}...")

                    # Baixar o vídeo
                    response = requests.get(video_url)
                    response.raise_for_status()

                    with open(output_path, 'wb') as f:
                        f.write(response.content)

                    logger.info(f"Vídeo salvo em {output_path}")

                    # Salvar uma cópia com o ID do vídeo
                    copy_path = os.path.join(output_dir, f"heygen_{video_id}.mp4")
                    with open(copy_path, 'wb') as f:
                        f.write(response.content)

                    logger.info(f"Cópia do vídeo salva em {copy_path}")

                    return output_path

                elif status == "failed":
                    logger.error("Falha ao processar o vídeo.")
                    return None

                # Aguardar 5 segundos antes de verificar novamente
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

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Gera um vídeo de reel com configurações otimizadas")
    parser.add_argument("--script", default="scripts/rapidinha_reel_style.txt", help="Caminho para o script de reel")
    parser.add_argument("--audio", help="Caminho para um arquivo de áudio existente (opcional)")
    parser.add_argument("--folder", default="augment", help="Nome da pasta no HeyGen")
    parser.add_argument("--profile", help="Perfil de voz a ser usado (opcional)")
    parser.add_argument("--optimize", action="store_true", help="Otimizar o texto para fala natural")
    parser.add_argument("--play", action="store_true", help="Reproduzir o vídeo gerado")
    parser.add_argument("--dry-run", action="store_true", help="Simular operações sem fazer chamadas de API")

    args = parser.parse_args()

    # Inicializar o gerador com o perfil de voz especificado
    generator = ReelVideoGenerator(voice_profile=args.profile)

    # Gerar áudio ou usar existente
    audio_path = args.audio
    if not audio_path:
        audio_path = generator.generate_reel_audio(
            args.script,
            optimize=args.optimize,
            dry_run=args.dry_run
        )

    if not audio_path:
        logger.error("Erro: Não foi possível obter o áudio.")
        return

    # Gerar vídeo
    video_path = generator.generate_reel_video(
        audio_path,
        folder_name=args.folder,
        dry_run=args.dry_run
    )

    if video_path:
        logger.info(f"Vídeo de reel gerado com sucesso: {video_path}")

        # Reproduzir o vídeo se solicitado
        if args.play and not args.dry_run:
            open_video_file(video_path)
    else:
        logger.error("Erro: Não foi possível gerar o vídeo de reel.")

if __name__ == "__main__":
    main()
