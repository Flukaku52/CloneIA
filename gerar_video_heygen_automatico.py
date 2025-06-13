#!/usr/bin/env python3
"""
Script para gerar vídeo automaticamente no HeyGen via API
"""

import os
import sys
import json
import time
import requests
import logging
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class HeyGenVideoCreator:
    def __init__(self):
        self.api_key = os.getenv('HEYGEN_API_KEY')
        if not self.api_key:
            raise ValueError("HEYGEN_API_KEY não encontrada no .env")
            
        self.api_base_url = "https://api.heygen.com/v2"
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Configurações específicas fornecidas pelo usuário
        self.avatar_id = "ad46ec4202394d9aa33bcf5974bac416"
        self.avatar_name = "Avatar Personalizado"
        self.voice_id = "25NR0sM9ehsgXaoknsxO"
        
        logging.info(f"Avatar configurado: {self.avatar_name} (ID: {self.avatar_id})")
        logging.info(f"Voice ID: {self.voice_id}")
    
    def upload_audio(self, audio_path):
        """Upload do áudio para o HeyGen"""
        logging.info(f"Fazendo upload do áudio: {audio_path}")
        
        # HeyGen v2 API usa upload direto no endpoint de criação de vídeo
        # Então vamos apenas retornar o caminho do arquivo para uso posterior
        return audio_path
    
    def create_video(self, audio_path):
        """Cria o vídeo com o áudio local"""
        logging.info("Criando vídeo no HeyGen...")
        
        # Para a API v2, primeiro fazemos upload do áudio
        with open(audio_path, 'rb') as audio_file:
            # Primeiro, cria o asset de áudio
            files = {
                'file': (os.path.basename(audio_path), audio_file, 'audio/mpeg')
            }
            
            upload_response = requests.post(
                "https://upload.heygen.com/v1/asset",
                headers={"X-Api-Key": self.api_key},
                files=files
            )
            
            if upload_response.status_code != 200:
                logging.error(f"Erro ao fazer upload: {upload_response.status_code} - {upload_response.text}")
                return None
                
            upload_data = upload_response.json()
            audio_asset_id = upload_data.get('data', {}).get('id')
            
            if not audio_asset_id:
                logging.error("Não foi possível obter o ID do asset de áudio")
                return None
                
            logging.info(f"Áudio enviado. Asset ID: {audio_asset_id}")
        
        # Agora cria o vídeo com o asset de áudio
        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": self.avatar_id,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "audio",
                    "audio_asset_id": audio_asset_id
                },
                "background": {
                    "type": "color",
                    "value": "#1a1a1a"
                }
            }],
            "dimension": {
                "width": 1080,
                "height": 1920
            },
            "aspect_ratio": "9:16",
            "test": False
        }
        
        create_url = f"{self.api_base_url}/video/generate"
        response = requests.post(create_url, headers=self.headers, json=payload)
        
        if response.status_code in [200, 201]:
            result = response.json()
            video_id = result.get('data', {}).get('video_id')
            logging.info(f"Vídeo criado! ID: {video_id}")
            return video_id
        else:
            logging.error(f"Erro ao criar vídeo: {response.status_code} - {response.text}")
            return None
    
    def check_status(self, video_id):
        """Verifica o status do vídeo"""
        status_url = f"{self.api_base_url}/video_status.get?video_id={video_id}"
        response = requests.get(status_url, headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('data', {})
        return None
    
    def wait_for_video(self, video_id, max_wait=600):
        """Aguarda o vídeo ser processado"""
        logging.info("Aguardando processamento do vídeo...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status_data = self.check_status(video_id)
            
            if status_data:
                status = status_data.get('status')
                
                if status == 'completed':
                    video_url = status_data.get('video_url')
                    logging.info(f"Vídeo processado com sucesso!")
                    return video_url
                elif status == 'failed':
                    error = status_data.get('error', 'Erro desconhecido')
                    logging.error(f"Falha no processamento: {error}")
                    return None
                else:
                    logging.info(f"Status: {status} - Aguardando...")
            
            time.sleep(10)
        
        logging.error("Timeout esperando o vídeo")
        return None
    
    def download_video(self, video_url, output_path):
        """Baixa o vídeo gerado"""
        logging.info(f"Baixando vídeo...")
        
        response = requests.get(video_url, stream=True)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logging.info(f"Vídeo salvo em: {output_path}")
            return True
        else:
            logging.error(f"Erro ao baixar vídeo: {response.status_code}")
            return False

def main():
    print("🎬 GERANDO VÍDEO AUTOMATICAMENTE NO HEYGEN")
    print("=" * 60)
    
    # Caminhos
    project_root = Path(__file__).parent.resolve()
    audio_path = project_root / "output" / "audio" / "renato_connecticut_bitcoin_audio.mp3"
    
    if not audio_path.exists():
        print(f"❌ Erro: Áudio não encontrado em {audio_path}")
        return 1
    
    try:
        # Inicializa o criador de vídeos
        creator = HeyGenVideoCreator()
        
        print(f"📁 Áudio: {audio_path}")
        print(f"🤖 Avatar: {creator.avatar_name} (ID: {creator.avatar_id})")
        print("🔄 Iniciando processo...")
        
        # 1. Preparando áudio
        print("\n[1/4] Preparando áudio...")
        
        # 2. Cria o vídeo (upload é feito dentro do método)
        print("\n[2/4] Criando vídeo com upload do áudio...")
        video_id = creator.create_video(str(audio_path))
        
        if not video_id:
            print("❌ Erro ao criar vídeo")
            return 1
        
        # 3. Aguarda processamento
        print(f"\n[3/4] Processando vídeo (ID: {video_id})...")
        video_url = creator.wait_for_video(video_id)
        
        if not video_url:
            print("❌ Erro no processamento do vídeo")
            return 1
        
        # 4. Baixa o vídeo
        print("\n[4/4] Baixando vídeo...")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = project_root / "output" / "videos" / f"renato_connecticut_{timestamp}.mp4"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if creator.download_video(video_url, str(output_path)):
            print(f"\n✅ SUCESSO! Vídeo gerado: {output_path}")
            print(f"🔗 URL do vídeo: {video_url}")
        else:
            print("❌ Erro ao baixar vídeo")
            print(f"💡 Baixe manualmente de: {video_url}")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        logging.exception("Erro detalhado:")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())