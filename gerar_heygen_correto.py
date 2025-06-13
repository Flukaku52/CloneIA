#!/usr/bin/env python3
"""
Gerador HeyGen v2 com estrutura correta (upload + generate)
"""

import requests
import json
import time
from pathlib import Path

def gerar_video_heygen_correto():
    """Gera vídeo usando processo correto: upload audio + generate video"""
    
    api_key = "OTU2YjcxM2ZhZGY2NDE5Mjg3MzYzMmZlNjEyYjZiNzUtMTc0OTY5NDg0MQ=="
    avatar_id = "3034bbd37f2540ddb70c90c7f67b4f5c"
    
    headers = {
        "X-Api-Key": api_key
    }
    
    print("🚀 HEYGEN v2 - PROCESSO CORRETO!")
    print("=" * 50)
    
    # Áudio de teste
    project_root = Path(__file__).parent.resolve()
    audio_path = project_root / "output" / "reel_renato_melhorado" / "segments" / "01_abertura_audio.mp3"
    
    if not audio_path.exists():
        print(f"❌ Áudio não encontrado: {audio_path}")
        return False
    
    print(f"📁 Áudio: {audio_path.name}")
    
    # ETAPA 1: Upload do áudio
    print("\n[1] 📤 Fazendo upload do áudio...")
    
    try:
        with open(audio_path, 'rb') as audio_file:
            files = {
                'file': (audio_path.name, audio_file, 'audio/mpeg')
            }
            
            upload_response = requests.post(
                "https://upload.heygen.com/v1/asset",
                headers={"X-Api-Key": api_key},
                files=files,
                timeout=60
            )
        
        print(f"📊 Upload status: {upload_response.status_code}")
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            audio_asset_id = upload_data.get('data', {}).get('id')
            
            if audio_asset_id:
                print(f"✅ Upload sucesso! Asset ID: {audio_asset_id}")
            else:
                print(f"❌ Sem asset ID na resposta: {upload_data}")
                return False
        else:
            print(f"❌ Erro upload: {upload_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no upload: {str(e)}")
        return False
    
    # ETAPA 2: Gera o vídeo
    print("\n[2] 🎬 Gerando vídeo...")
    
    payload = {
        "video_inputs": [{
            "character": {
                "type": "avatar",
                "avatar_id": avatar_id,
                "avatar_style": "normal"
            },
            "voice": {
                "type": "audio",
                "audio_asset_id": audio_asset_id
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
    
    try:
        generate_response = requests.post(
            "https://api.heygen.com/v2/video/generate",
            headers={
                "X-Api-Key": api_key,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )
        
        print(f"📊 Generate status: {generate_response.status_code}")
        
        if generate_response.status_code in [200, 201]:
            result = generate_response.json()
            video_id = result.get('data', {}).get('video_id')
            
            if video_id:
                print(f"✅ Vídeo criado! ID: {video_id}")
                
                # ETAPA 3: Monitora o processamento
                print("\n[3] ⏳ Monitorando processamento...")
                
                for attempt in range(60):  # 10 minutos
                    time.sleep(10)
                    
                    status_response = requests.get(
                        f"https://api.heygen.com/v2/video_status/{video_id}",
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
                                print(f"\n🎉 VÍDEO PRONTO!")
                                print(f"🔗 URL: {video_url}")
                                
                                # ETAPA 4: Baixa o vídeo
                                print("\n[4] 📥 Baixando vídeo...")
                                
                                video_response = requests.get(video_url, stream=True)
                                
                                if video_response.status_code == 200:
                                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                                    output_path = project_root / "output" / f"heygen_teste_{timestamp}.mp4"
                                    
                                    with open(output_path, 'wb') as f:
                                        for chunk in video_response.iter_content(chunk_size=8192):
                                            f.write(chunk)
                                    
                                    print(f"✅ SUCESSO! Vídeo salvo: {output_path}")
                                    return True
                                else:
                                    print(f"❌ Erro no download: {video_response.status_code}")
                                    print(f"💡 Baixe manualmente: {video_url}")
                                    return True  # Vídeo foi gerado, só não baixou
                        
                        elif status == 'failed':
                            error = status_data.get('error', 'Erro desconhecido')
                            print(f"❌ Falha no processamento: {error}")
                            return False
                    else:
                        print(f"   ⚠️ Erro verificando status: {status_response.status_code}")
                
                print("⏰ Timeout esperando processamento")
                return False
            else:
                print(f"❌ Sem video_id: {result}")
                return False
        else:
            print(f"❌ Erro generate: {generate_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na geração: {str(e)}")
        return False

if __name__ == "__main__":
    success = gerar_video_heygen_correto()
    
    if success:
        print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("Agora posso gerar todos os 5 vídeos automaticamente!")
    else:
        print("\n❌ Teste falhou")
        print("Pode precisar verificar conta ou permissões da API")