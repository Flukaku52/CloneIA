#!/usr/bin/env python3
"""
Script usando API v2 do HeyGen com a chave correta
"""

import os
import sys
import json
import time
import base64
import requests
import logging
from pathlib import Path

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_heygen_video_v2():
    """Cria vídeo usando API v2 do HeyGen"""
    
    # Chave API correta
    api_key = "OGU5OTA4MGFhMTZkNDExNDhmNmZlNGI1ODY2ZDNhNGUtMTc0NzE5OTM4Mg=="
    avatar_id = "ad46ec4202394d9aa33bcf5974bac416"
    
    # Caminhos
    project_root = Path(__file__).parent.resolve()
    audio_path = project_root / "output" / "audio" / "renato_connecticut_bitcoin_audio.mp3"
    
    if not audio_path.exists():
        logging.error(f"Áudio não encontrado: {audio_path}")
        return False
    
    print("🎬 GERANDO VÍDEO NO HEYGEN v2")
    print("=" * 60)
    print(f"📁 Áudio: {audio_path}")
    print(f"🤖 Avatar: {avatar_id}")
    print(f"🔑 API Key: {api_key[:15]}...")
    
    headers = {
        "X-Api-Key": api_key
    }
    
    # 1. Upload do áudio primeiro
    print("\n[1/4] Fazendo upload do áudio...")
    
    try:
        # Prepare multipart form data correctly
        files = {
            'file': (audio_path.name, open(audio_path, 'rb'), 'audio/mpeg')
        }
        data = {
            'type': 'audio'
        }
        
        upload_response = requests.post(
            "https://upload.heygen.com/v1/asset",
            headers={"X-Api-Key": api_key},
            files=files,
            data=data,
            timeout=60
        )
        
        # Close the file
        files['file'][1].close()
        
        logging.info(f"Upload response: {upload_response.status_code}")
        logging.info(f"Upload content: {upload_response.text}")
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            asset_id = upload_data.get('data', {}).get('id')
            
            if not asset_id:
                print("❌ Erro: Não foi possível obter asset ID")
                return False
                
            print(f"✅ Áudio enviado! Asset ID: {asset_id}")
            
            # 2. Cria o vídeo
            print("\n[2/4] Criando vídeo...")
            
            payload = {
                "video_inputs": [{
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id,
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "audio", 
                        "audio_asset_id": asset_id
                    },
                    "background": {
                        "type": "color",
                        "value": "#000000"
                    }
                }],
                "dimension": {
                    "width": 1080,
                    "height": 1920
                },
                "aspect_ratio": "9:16",
                "test": False
            }
            
            create_headers = {
                "X-Api-Key": api_key,
                "Content-Type": "application/json"
            }
            
            create_response = requests.post(
                "https://api.heygen.com/v2/video/generate",
                headers=create_headers,
                json=payload,
                timeout=60
            )
            
            logging.info(f"Create response: {create_response.status_code}")
            logging.info(f"Create content: {create_response.text}")
            
            if create_response.status_code in [200, 201]:
                result = create_response.json()
                video_id = result.get('data', {}).get('video_id')
                
                if video_id:
                    print(f"✅ Vídeo criado! ID: {video_id}")
                    
                    # 3. Aguarda processamento
                    print(f"\n[3/4] Processando vídeo...")
                    
                    max_attempts = 60  # 10 minutos
                    for attempt in range(max_attempts):
                        time.sleep(10)
                        
                        status_response = requests.get(
                            f"https://api.heygen.com/v2/video_status.get?video_id={video_id}",
                            headers=headers,
                            timeout=30
                        )
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json().get('data', {})
                            status = status_data.get('status')
                            
                            print(f"   Status: {status}")
                            
                            if status == 'completed':
                                video_url = status_data.get('video_url')
                                
                                if video_url:
                                    # 4. Baixa o vídeo
                                    print(f"\n[4/4] Baixando vídeo...")
                                    
                                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                                    output_path = project_root / "output" / "videos" / f"renato_heygen_v2_{timestamp}.mp4"
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
                                error = status_data.get('error', 'Erro desconhecido')
                                print(f"❌ Falha no processamento: {error}")
                                return False
                    
                    print("❌ Timeout aguardando processamento")
                    return False
                else:
                    print("❌ Erro: Video ID não encontrado na resposta")
                    return False
            else:
                print(f"❌ Erro ao criar vídeo: {create_response.status_code}")
                print(f"Resposta: {create_response.text}")
                return False
        else:
            print(f"❌ Erro no upload: {upload_response.status_code}")
            print(f"Resposta: {upload_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        logging.exception("Detalhes do erro:")
        return False

if __name__ == "__main__":
    success = create_heygen_video_v2()
    sys.exit(0 if success else 1)