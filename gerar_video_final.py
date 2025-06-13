#!/usr/bin/env python3
"""
Script final para gerar vídeo no HeyGen com estrutura correta da API
"""

import os
import sys
import json
import time
import base64
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

def create_heygen_video_v1():
    """Cria vídeo usando API v1 do HeyGen"""
    
    # Configurações - usando a chave API correta fornecida pelo usuário
    api_key = "OGU5OTA4MGFhMTZkNDExNDhmNmZlNGI1ODY2ZDNhNGUtMTc0NzE5OTM4Mg=="
    
    logging.info(f"Usando API key: {api_key[:10]}...")
    
    # IDs específicos fornecidos
    avatar_id = "ad46ec4202394d9aa33bcf5974bac416"
    
    # Caminhos
    project_root = Path(__file__).parent.resolve()
    audio_path = project_root / "output" / "audio" / "renato_connecticut_bitcoin_audio.mp3"
    
    if not audio_path.exists():
        logging.error(f"Áudio não encontrado: {audio_path}")
        return False
    
    print("🎬 GERANDO VÍDEO NO HEYGEN")
    print("=" * 60)
    print(f"📁 Áudio: {audio_path}")
    print(f"🤖 Avatar: {avatar_id}")
    
    # 1. Lê e codifica o áudio
    print("\n[1/4] Preparando áudio...")
    with open(audio_path, 'rb') as f:
        audio_data = f.read()
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    # 2. Cria o vídeo
    print("\n[2/4] Criando vídeo...")
    
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Payload para criação do vídeo (v1 API)
    payload = {
        "script": {
            "type": "audio",
            "audio_base64": audio_base64
        },
        "avatar": {
            "avatar_id": avatar_id,
            "avatar_style": "normal"
        },
        "background": {
            "type": "color",
            "value": "#000000"
        },
        "ratio": "9:16"
    }
    
    # Tenta primeiro com v1 endpoint
    create_url = "https://api.heygen.com/v1/video"
    
    response = requests.post(create_url, headers=headers, json=payload)
    
    if response.status_code not in [200, 201]:
        # Se v1 falhar, tenta estrutura alternativa
        logging.info("Tentando estrutura alternativa...")
        
        payload = {
            "avatar_id": avatar_id,
            "voice": {
                "type": "audio",
                "audio_base64": audio_base64
            },
            "background": "#000000",
            "ratio": "9:16"
        }
        
        response = requests.post(create_url, headers=headers, json=payload)
    
    if response.status_code in [200, 201]:
        result = response.json()
        video_id = result.get('data', {}).get('video_id') or result.get('data', {}).get('id')
        
        if video_id:
            print(f"✅ Vídeo criado! ID: {video_id}")
            
            # 3. Aguarda processamento
            print(f"\n[3/4] Processando vídeo...")
            
            max_attempts = 60  # 10 minutos
            for attempt in range(max_attempts):
                time.sleep(10)
                
                # Verifica status
                status_url = f"https://api.heygen.com/v1/video/{video_id}"
                status_response = requests.get(status_url, headers=headers)
                
                if status_response.status_code == 200:
                    status_data = status_response.json().get('data', {})
                    status = status_data.get('status')
                    
                    print(f"   Status: {status}")
                    
                    if status == 'completed':
                        video_url = status_data.get('video_url') or status_data.get('result_url')
                        
                        if video_url:
                            # 4. Baixa o vídeo
                            print(f"\n[4/4] Baixando vídeo...")
                            
                            timestamp = time.strftime("%Y%m%d_%H%M%S")
                            output_path = project_root / "output" / "videos" / f"renato_heygen_{timestamp}.mp4"
                            output_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            video_response = requests.get(video_url, stream=True)
                            
                            if video_response.status_code == 200:
                                with open(output_path, 'wb') as f:
                                    for chunk in video_response.iter_content(chunk_size=8192):
                                        f.write(chunk)
                                
                                print(f"\n✅ SUCESSO!")
                                print(f"📹 Vídeo salvo: {output_path}")
                                print(f"🔗 URL: {video_url}")
                                return True
                            else:
                                print(f"❌ Erro ao baixar vídeo")
                                print(f"💡 Baixe manualmente: {video_url}")
                                return False
                    
                    elif status == 'failed':
                        print(f"❌ Falha no processamento: {status_data.get('error', 'Erro desconhecido')}")
                        return False
            
            print("❌ Timeout aguardando processamento")
            return False
    
    else:
        print(f"❌ Erro ao criar vídeo: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        # Instruções manuais como fallback
        print("\n📋 ALTERNATIVA: Gere manualmente no HeyGen")
        print("=" * 60)
        print("1. Acesse https://app.heygen.com")
        print("2. Create Video → Upload Audio")
        print(f"3. Upload: {audio_path}")
        print(f"4. Selecione avatar ID: {avatar_id}")
        print("5. Formato: 9:16 (Portrait)")
        print("6. Generate e baixe o vídeo")
        
        return False

if __name__ == "__main__":
    success = create_heygen_video_v1()
    sys.exit(0 if success else 1)