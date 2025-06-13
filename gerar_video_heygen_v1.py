#!/usr/bin/env python3
"""
Script para gerar vídeo no HeyGen usando API v1
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

class HeyGenV1Creator:
    def __init__(self):
        self.api_key = os.getenv('HEYGEN_API_KEY')
        if not self.api_key:
            raise ValueError("HEYGEN_API_KEY não encontrada no .env")
            
        self.api_base_url = "https://api.heygen.com/v1"
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Avatar e voz específicos
        self.avatar_id = "ad46ec4202394d9aa33bcf5974bac416"
        self.voice_id = "25NR0sM9ehsgXaoknsxO"
        
        logging.info(f"Configurado com Avatar ID: {self.avatar_id}")
        logging.info(f"Voice ID: {self.voice_id}")
    
    def create_talking_photo(self, audio_path):
        """Cria vídeo usando talking photo API"""
        logging.info("Criando vídeo com talking photo...")
        
        # Lê o áudio
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        
        # Codifica em base64
        import base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Payload para API v1
        payload = {
            "avatar_id": self.avatar_id,
            "voice": {
                "type": "audio",
                "audio_base64": audio_base64
            },
            "background": {
                "type": "color",
                "value": "#000000"
            },
            "ratio": "9:16"
        }
        
        # Endpoint v1
        create_url = f"{self.api_base_url}/talking_photo"
        
        response = requests.post(create_url, headers=self.headers, json=payload)
        
        if response.status_code in [200, 201]:
            result = response.json()
            video_id = result.get('data', {}).get('id')
            logging.info(f"Vídeo criado! ID: {video_id}")
            return video_id
        else:
            logging.error(f"Erro: {response.status_code} - {response.text}")
            return None
    
    def check_status(self, video_id):
        """Verifica status do vídeo"""
        status_url = f"{self.api_base_url}/talking_photo/{video_id}"
        response = requests.get(status_url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json().get('data', {})
        return None
    
    def wait_for_video(self, video_id, max_wait=600):
        """Aguarda processamento"""
        logging.info("Aguardando processamento...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            data = self.check_status(video_id)
            
            if data:
                status = data.get('status')
                
                if status == 'completed':
                    video_url = data.get('result_url')
                    logging.info("Vídeo processado!")
                    return video_url
                elif status == 'failed':
                    error = data.get('error', 'Erro desconhecido')
                    logging.error(f"Falha: {error}")
                    return None
                else:
                    logging.info(f"Status: {status}...")
            
            time.sleep(10)
        
        logging.error("Timeout")
        return None
    
    def download_video(self, video_url, output_path):
        """Baixa o vídeo"""
        logging.info("Baixando vídeo...")
        
        response = requests.get(video_url, stream=True)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logging.info(f"Salvo em: {output_path}")
            return True
        return False

def main():
    print("🎬 GERANDO VÍDEO NO HEYGEN (API v1)")
    print("=" * 60)
    
    project_root = Path(__file__).parent.resolve()
    audio_path = project_root / "output" / "audio" / "renato_connecticut_bitcoin_audio.mp3"
    
    if not audio_path.exists():
        print(f"❌ Áudio não encontrado: {audio_path}")
        return 1
    
    try:
        creator = HeyGenV1Creator()
        
        print(f"📁 Áudio: {audio_path}")
        print(f"🤖 Avatar ID: {creator.avatar_id}")
        print(f"🎤 Voice ID: {creator.voice_id}")
        
        # Cria vídeo
        print("\n[1/3] Criando vídeo...")
        video_id = creator.create_talking_photo(str(audio_path))
        
        if not video_id:
            print("❌ Erro ao criar vídeo")
            return 1
        
        # Aguarda
        print(f"\n[2/3] Processando (ID: {video_id})...")
        video_url = creator.wait_for_video(video_id)
        
        if not video_url:
            print("❌ Erro no processamento")
            return 1
        
        # Baixa
        print("\n[3/3] Baixando...")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = project_root / "output" / "videos" / f"renato_heygen_{timestamp}.mp4"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if creator.download_video(video_url, str(output_path)):
            print(f"\n✅ SUCESSO! Vídeo: {output_path}")
            print(f"🔗 URL: {video_url}")
        else:
            print(f"❌ Erro ao baixar. URL: {video_url}")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        logging.exception("Detalhes:")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())