"""
Módulo para gerar áudio a partir de texto usando a API da ElevenLabs.
"""
import os
import json
import time
import logging
import platform
import subprocess
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('audio_generator')

# Carregar variáveis de ambiente
load_dotenv()

class AudioGenerator:
    """
    Classe para gerar áudio a partir de texto usando a API da ElevenLabs.
    """

    def __init__(self, voice_profile: Optional[str] = None):
        """
        Inicializa o gerador de áudio.

        Args:
            voice_profile: Nome do perfil de voz a ser usado (se None, usa o padrão)
        """
        # Carregar a chave da API
        self.api_key = self._load_api_key()

        # Diretório para armazenar os áudios gerados
        self.audio_dir = os.path.join(os.getcwd(), "output", "audio")
        os.makedirs(self.audio_dir, exist_ok=True)

        # Configurações de voz otimizadas para o sotaque carioca
        self.voice_settings = {
            "stability": 0.15,          # Estabilidade para melhor fluidez
            "similarity_boost": 0.65,    # Reduzida para mais naturalidade
            "style": 0.85,              # Estilo para capturar a entonação carioca
            "use_speaker_boost": True,   # Melhorar a qualidade do áudio
            "model_id": "eleven_multilingual_v2"  # Modelo multilíngue avançado
        }

        # Carregar configuração da voz
        self.voice_id = None
        self.voice_name = "Rapidinha Voice"
        self._load_voice_config(voice_profile)

    def _load_api_key(self) -> Optional[str]:
        """
        Carrega a chave da API do ambiente ou do arquivo .env.

        Returns:
            Optional[str]: A chave da API ou None se não encontrada
        """
        # Tentar obter do ambiente
        api_key = os.getenv("ELEVENLABS_API_KEY")

        # Se não conseguir, tentar ler diretamente do arquivo .env
        if not api_key:
            try:
                with open('.env', 'r') as f:
                    for line in f:
                        if line.startswith('ELEVENLABS_API_KEY='):
                            api_key = line.strip().split('=', 1)[1].strip('"').strip("'")
                            break
            except Exception as e:
                logger.error(f"Erro ao ler arquivo .env: {e}")

        if not api_key:
            logger.warning("API key da ElevenLabs não encontrada. A geração de áudio não funcionará.")
        else:
            logger.info(f"API key da ElevenLabs encontrada: {api_key[:5]}...{api_key[-5:]}")

        return api_key

    def _load_voice_config(self, profile_name: Optional[str] = None):
        """
        Carrega a configuração da voz de um arquivo.

        Args:
            profile_name: Nome do perfil de voz a ser carregado
        """
        # Determinar o caminho do arquivo de configuração
        if profile_name:
            if profile_name.lower() == "fluido":
                config_path = os.path.join(os.getcwd(), "config", "voice_config_fluido.json")
            elif profile_name.lower() == "flukakuia":
                config_path = os.path.join(os.getcwd(), "config", "voice_config_flukakuia.json")
            else:
                config_path = os.path.join(os.getcwd(), "config", f"voice_config_{profile_name}.json")
        else:
            config_path = os.path.join(os.getcwd(), "config", "voice_config.json")

        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.voice_id = config.get("voice_id")
                    self.voice_name = config.get("voice_name", "Rapidinha Voice")

                    # Carregar configurações avançadas se disponíveis
                    if "settings" in config:
                        self.voice_settings.update(config["settings"])
                        logger.info(f"Configurações avançadas carregadas: {self.voice_settings}")

                    logger.info(f"Configuração de voz carregada. ID: {self.voice_id}, Nome: {self.voice_name}")
            except Exception as e:
                logger.error(f"Erro ao carregar configuração de voz: {e}")

    def generate_audio(self, text: str, output_path: Optional[str] = None, optimize: bool = True, dry_run: bool = False) -> Optional[str]:
        """
        Gera áudio a partir de texto usando a API da ElevenLabs.

        Args:
            text: Texto a ser convertido em áudio
            output_path: Caminho para salvar o arquivo de áudio. Se None, gera um nome baseado no timestamp
            optimize: Se True, otimiza o texto para fala
            dry_run: Se True, simula a geração sem fazer chamadas de API

        Returns:
            Optional[str]: Caminho para o arquivo de áudio gerado, ou None se falhar
        """
        if not self.api_key and not dry_run:
            logger.error("API key da ElevenLabs não configurada. Não é possível gerar áudio.")
            return None

        # Otimizar o texto se solicitado
        if optimize:
            original_text = text
            text = self._optimize_text(text)
            logger.info(f"Texto otimizado: {len(original_text)} caracteres -> {len(text)} caracteres")

        try:
            # Gerar nome de arquivo baseado no timestamp se não for fornecido
            if not output_path:
                timestamp = int(time.time())
                output_path = os.path.join(self.audio_dir, f"audio_{timestamp}.mp3")

            # Modo de simulação
            if dry_run:
                logger.info(f"[SIMULAÇÃO] Geraria áudio para o texto: '{text[:50]}...'")
                logger.info(f"[SIMULAÇÃO] Salvaria em: {output_path}")
                return output_path

            # Verificar se temos uma voz configurada
            voice_identifier = self.voice_id if self.voice_id else "Rachel"

            # Preparar a requisição para a API
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_identifier}"

            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }

            data = {
                "text": text,
                "model_id": self.voice_settings.get("model_id", "eleven_multilingual_v2"),
                "voice_settings": self.voice_settings
            }

            # Fazer a requisição para a API
            logger.info(f"Gerando áudio para o texto: '{text[:50]}...'")
            response = requests.post(url, json=data, headers=headers, timeout=60)
            response.raise_for_status()

            # Salvar o áudio
            with open(output_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"Áudio gerado com sucesso: {output_path}")
            return output_path

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição à API: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao gerar áudio: {e}")
            return None

    def _optimize_text(self, text: str) -> str:
        """
        Otimiza o texto para fala natural.

        Esta função aplica várias otimizações para tornar o texto mais natural
        quando convertido em fala, incluindo:
        - Substituir a introdução para máxima energia
        - Remover pontuação excessiva que causa pausas
        - Substituir termos para melhor pronúncia
        - Usar maiúsculas para ênfase em palavras-chave

        Args:
            text: Texto original

        Returns:
            str: Texto otimizado
        """
        if not text:
            return text

        # Substituir introdução para máxima energia
        if text.lower().startswith("e aí cambada"):
            text = "EAÍCAMBADA" + text[len("e aí cambada"):]
        elif text.lower().startswith("fala cambada"):
            text = "FALACAMBADA" + text[len("fala cambada"):]

        # Remover pontuação excessiva que causa pausas
        for char in [',', '.', '!', '?', '...', ';', ':']:
            text = text.replace(char, '')

        # Substituir termos para melhor pronúncia
        replacements = {
            "Bitcoin": "Bitcoim",
            "Ethereum": "Etherium",
            "Cardano": "Cardâno",
            "Solana": "Solâna",
            "Polkadot": "Polcadot",
            "Binance": "Bináns",
            "Coinbase": "Cóinbeis",
            "NFT": "ÊnÊfeTê",
            "DeFi": "DêFai",
            "staking": "stêiking",
            "blockchain": "blókcheim",
            "wallet": "wólet",
            "token": "tôken",
            "altcoin": "ôltcoin",
            "mining": "máining",
            "miner": "máiner"
        }

        for original, replacement in replacements.items():
            text = text.replace(original, replacement)

        # Usar maiúsculas para ênfase em palavras-chave
        emphasis_words = [
            "bombando", "muito", "super", "mega", "alta", "subindo",
            "disparou", "explodiu", "recorde", "máxima", "forte",
            "incrível", "enorme", "gigante", "absurdo", "impressionante",
            "surpreendente", "extraordinário", "fenomenal", "espetacular"
        ]

        for word in emphasis_words:
            if word in text.lower():
                text = text.replace(word, word.upper())
                text = text.replace(word.capitalize(), word.upper())

        return text

    def clone_voice(self, audio_files: List[str], voice_name: str = "Rapidinha Voice", dry_run: bool = False) -> Optional[str]:
        """
        Clona uma voz a partir de arquivos de áudio.

        Args:
            audio_files: Lista de caminhos para arquivos de áudio
            voice_name: Nome da voz a ser criada
            dry_run: Se True, simula a clonagem sem fazer chamadas de API

        Returns:
            Optional[str]: ID da voz clonada, ou None se falhar
        """
        if not self.api_key and not dry_run:
            logger.error("API key da ElevenLabs não configurada. Não é possível clonar voz.")
            return None

        # Verificar se temos arquivos de áudio válidos
        valid_files = [f for f in audio_files if os.path.exists(f)]

        if not valid_files:
            logger.error("Nenhum arquivo de áudio válido encontrado.")
            return None

        logger.info(f"Clonando voz a partir de {len(valid_files)} arquivos de áudio...")

        # Modo de simulação
        if dry_run:
            logger.info(f"[SIMULAÇÃO] Clonaria voz '{voice_name}' a partir de {len(valid_files)} arquivos")
            logger.info(f"[SIMULAÇÃO] Arquivos: {valid_files[:5]}{'...' if len(valid_files) > 5 else ''}")

            # Criar um ID de voz simulado
            import hashlib
            simulated_id = hashlib.md5(voice_name.encode()).hexdigest()[:24]

            # Salvar uma configuração simulada
            config_path = os.path.join(os.getcwd(), "config", "voice_config.json")
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            voice_config = {
                "voice_id": simulated_id,
                "voice_name": voice_name,
                "settings": self.voice_settings
            }

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(voice_config, f, ensure_ascii=False, indent=4)

            logger.info(f"[SIMULAÇÃO] ID de voz simulado: {simulated_id}")
            return simulated_id

        try:
            # Preparar os arquivos para upload
            files = []
            for audio_file in valid_files:
                with open(audio_file, 'rb') as f:
                    files.append(('files', (os.path.basename(audio_file), f.read(), 'audio/mpeg')))

            # Fazer a requisição para a API
            url = "https://api.elevenlabs.io/v1/voices/add"
            headers = {"xi-api-key": self.api_key}
            data = {
                "name": voice_name,
                "description": "Voz clonada para o quadro Rapidinha no Cripto"
            }

            response = requests.post(url, headers=headers, data=data, files=files)
            response.raise_for_status()

            # Processar a resposta
            result = response.json()
            voice_id = result.get("voice_id")

            if voice_id:
                logger.info(f"Voz clonada com sucesso! ID: {voice_id}")

                # Atualizar o ID da voz
                self.voice_id = voice_id
                self.voice_name = voice_name

                # Salvar o ID da voz e configurações em um arquivo de configuração
                config_path = os.path.join(os.getcwd(), "config", "voice_config.json")
                os.makedirs(os.path.dirname(config_path), exist_ok=True)

                voice_config = {
                    "voice_id": voice_id,
                    "voice_name": voice_name,
                    "settings": self.voice_settings
                }

                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(voice_config, f, ensure_ascii=False, indent=4)

                return voice_id
            else:
                logger.error("Falha ao clonar voz. Nenhum ID de voz retornado.")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição à API: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao clonar voz: {e}")
            return None

    def extract_audio_samples(self, video_dir: str, output_dir: Optional[str] = None,
                             max_samples: int = 5, max_duration: int = 30) -> List[str]:
        """
        Extrai amostras de áudio de vídeos para clonagem de voz.

        Args:
            video_dir: Diretório contendo os vídeos
            output_dir: Diretório para salvar as amostras (se None, usa o padrão)
            max_samples: Número máximo de amostras a extrair
            max_duration: Duração máxima de cada amostra em segundos

        Returns:
            List[str]: Lista de caminhos para os arquivos de áudio extraídos
        """
        try:
            import moviepy.editor as mp
        except ImportError:
            logger.error("Erro: biblioteca moviepy não encontrada. Instale moviepy.")
            return []

        # Diretório para armazenar as amostras
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), "reference", "voice_samples")

        os.makedirs(output_dir, exist_ok=True)

        try:
            # Listar todos os vídeos no diretório
            video_files = []
            for filename in os.listdir(video_dir):
                if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    video_files.append(os.path.join(video_dir, filename))

            if not video_files:
                logger.warning("Nenhum vídeo encontrado no diretório.")
                return []

            # Limitar o número de vídeos
            video_files = video_files[:max_samples]

            # Extrair amostras de áudio
            audio_samples = []
            for i, video_file in enumerate(video_files):
                try:
                    # Extrair áudio do vídeo
                    video = mp.VideoFileClip(video_file)

                    # Limitar a duração
                    if video.duration > max_duration:
                        video = video.subclip(0, max_duration)

                    # Salvar o áudio
                    audio_path = os.path.join(output_dir, f"sample_{i+1}.mp3")
                    video.audio.write_audiofile(audio_path, codec='mp3')

                    # Adicionar à lista de amostras
                    audio_samples.append(audio_path)

                    # Fechar o vídeo
                    video.close()

                except Exception as e:
                    logger.error(f"Erro ao extrair áudio do vídeo {video_file}: {e}")

            logger.info(f"Extraídas {len(audio_samples)} amostras de áudio para clonagem de voz.")
            return audio_samples

        except Exception as e:
            logger.error(f"Erro ao extrair amostras de áudio: {e}")
            return []

    def extract_short_samples(self, source_dir: str, output_dir: Optional[str] = None,
                             min_duration: float = 7.0, max_duration: float = 12.0,
                             num_samples: int = 40) -> List[str]:
        """
        Extrai amostras curtas de áudio a partir de arquivos de áudio mais longos.

        Args:
            source_dir: Diretório contendo os arquivos de áudio fonte
            output_dir: Diretório para salvar as amostras curtas (se None, usa o padrão)
            min_duration: Duração mínima de cada amostra em segundos
            max_duration: Duração máxima de cada amostra em segundos
            num_samples: Número de amostras a extrair

        Returns:
            List[str]: Lista de caminhos para os arquivos de áudio extraídos
        """
        try:
            import moviepy.editor as mp
        except ImportError:
            logger.error("Erro: biblioteca moviepy não encontrada. Instale moviepy.")
            return []

        # Diretório para armazenar as amostras
        if not output_dir:
            output_dir = os.path.join(os.getcwd(), "reference", "samples", "short_samples")

        os.makedirs(output_dir, exist_ok=True)

        try:
            # Listar todos os arquivos de áudio no diretório
            audio_files = []
            for filename in os.listdir(source_dir):
                if filename.lower().endswith(('.mp3', '.wav', '.m4a')):
                    audio_files.append(os.path.join(source_dir, filename))

            if not audio_files:
                logger.warning("Nenhum arquivo de áudio encontrado no diretório.")
                return []

            # Extrair amostras curtas
            short_samples = []
            sample_count = 0

            for audio_file in audio_files:
                if sample_count >= num_samples:
                    break

                try:
                    # Carregar arquivo de áudio
                    audio = mp.AudioFileClip(audio_file)

                    # Pular se for muito curto
                    if audio.duration < min_duration:
                        continue

                    # Determinar número de amostras a extrair deste arquivo
                    file_samples = min(3, num_samples - sample_count)

                    for i in range(file_samples):
                        # Determinar tempo inicial (evitar o primeiro e último segundo)
                        max_start = max(0, audio.duration - max_duration - 1)
                        if max_start <= 1:
                            start_time = 1
                        else:
                            start_time = 1 + (i * max_start / file_samples)

                        # Determinar tempo final
                        end_time = min(start_time + max_duration, audio.duration - 1)

                        # Garantir duração mínima
                        if end_time - start_time < min_duration:
                            continue

                        # Extrair amostra
                        sample = audio.subclip(start_time, end_time)

                        # Salvar amostra
                        sample_path = os.path.join(output_dir, f"short_sample_{sample_count+1}.mp3")
                        sample.write_audiofile(sample_path, codec='mp3')

                        # Adicionar à lista de amostras
                        short_samples.append(sample_path)
                        sample_count += 1

                    # Fechar áudio
                    audio.close()

                except Exception as e:
                    logger.error(f"Erro ao extrair amostra curta de {audio_file}: {e}")

            # Criar um relatório
            report = {
                "total_samples": len(short_samples),
                "min_duration": min_duration,
                "max_duration": max_duration,
                "samples": [
                    {
                        "path": sample,
                        "duration": mp.AudioFileClip(sample).duration
                    }
                    for sample in short_samples
                ]
            }

            report_path = os.path.join(output_dir, "duration_report.json")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            logger.info(f"Extraídas {len(short_samples)} amostras curtas de áudio.")
            return short_samples

        except Exception as e:
            logger.error(f"Erro ao extrair amostras curtas: {e}")
            return []


def open_audio_file(file_path: str) -> bool:
    """
    Abre um arquivo de áudio com o player padrão do sistema.

    Args:
        file_path: Caminho para o arquivo de áudio

    Returns:
        bool: True se bem-sucedido, False caso contrário
    """
    if not os.path.exists(file_path):
        logger.error(f"Arquivo de áudio não encontrado: {file_path}")
        return False

    try:
        system = platform.system()

        if system == "Darwin":  # macOS
            subprocess.call(["open", file_path])
        elif system == "Windows":
            subprocess.call(["start", file_path], shell=True)
        else:  # Linux e outros
            subprocess.call(["xdg-open", file_path])

        logger.info(f"Arquivo de áudio aberto: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao abrir arquivo de áudio: {e}")
        return False

def list_available_voices(api_key: str) -> List[dict]:
    """
    Lista as vozes disponíveis na conta do ElevenLabs.

    Args:
        api_key: Chave da API do ElevenLabs

    Returns:
        List[dict]: Lista de vozes disponíveis
    """
    if not api_key:
        logger.error("API key da ElevenLabs não configurada.")
        return []

    try:
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": api_key}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        voices_data = response.json()
        voices = voices_data.get("voices", [])

        logger.info(f"Encontradas {len(voices)} vozes disponíveis:")
        for voice in voices:
            logger.info(f"- {voice.get('name')} (ID: {voice.get('voice_id')})")

        return voices
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição à API: {e}")
        return []
    except Exception as e:
        logger.error(f"Erro ao listar vozes: {e}")
        return []

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gerador de áudio para o Clone Rapidinha no Cripto")
    parser.add_argument("--text", help="Texto a ser convertido em áudio")
    parser.add_argument("--clone", action="store_true", help="Clonar voz a partir de amostras de áudio")
    parser.add_argument("--extract", action="store_true", help="Extrair amostras de áudio de vídeos")
    parser.add_argument("--extract-short", action="store_true", help="Extrair amostras curtas de áudio")
    parser.add_argument("--list-voices", action="store_true", help="Listar vozes disponíveis")
    parser.add_argument("--play", action="store_true", help="Reproduzir o áudio gerado")
    parser.add_argument("--profile", help="Perfil de voz a ser usado")
    parser.add_argument("--optimize", action="store_true", help="Otimizar o texto para fala")
    parser.add_argument("--dry-run", action="store_true", help="Simular operações sem fazer chamadas de API")

    args = parser.parse_args()

    # Inicializar o gerador de áudio
    generator = AudioGenerator(voice_profile=args.profile)

    # Listar vozes disponíveis
    if args.list_voices:
        list_available_voices(generator.api_key)

    # Extrair amostras de áudio de vídeos
    if args.extract:
        video_dir = os.path.join(os.getcwd(), "reference", "videos")
        if not os.path.exists(video_dir):
            logger.error(f"Diretório de vídeos não encontrado: {video_dir}")
        else:
            generator.extract_audio_samples(video_dir)

    # Extrair amostras curtas de áudio
    if args.extract_short:
        source_dir = os.path.join(os.getcwd(), "reference", "voice_samples")
        if not os.path.exists(source_dir):
            logger.error(f"Diretório de amostras não encontrado: {source_dir}")
        else:
            generator.extract_short_samples(source_dir)

    # Clonar voz a partir de amostras de áudio
    if args.clone:
        samples_dir = os.path.join(os.getcwd(), "reference", "voice_samples")
        if os.path.exists(samples_dir):
            audio_files = [os.path.join(samples_dir, f) for f in os.listdir(samples_dir) if f.endswith('.mp3')]
            if audio_files:
                generator.clone_voice(audio_files, dry_run=args.dry_run)
            else:
                logger.error("Nenhuma amostra de áudio encontrada. Execute primeiro com --extract.")
        else:
            logger.error("Diretório de amostras não encontrado. Execute primeiro com --extract.")

    # Gerar áudio a partir de texto
    if args.text:
        audio_path = generator.generate_audio(args.text, optimize=args.optimize, dry_run=args.dry_run)
        if audio_path and args.play and not args.dry_run:
            open_audio_file(audio_path)
