#!/usr/bin/env python3
"""
Gerador HeyGen usando API v2 que funciona
"""

import requests
import json
import base64
import time
from pathlib import Path

def gerar_videos_heygen_v2():
    """Gera vídeos usando API v2 do HeyGen"""
    
    api_key = "OTU2YjcxM2ZhZGY2NDE5Mjg3MzYzMmZlNjEyYjZiNzUtMTc0OTY5NDg0MQ=="
    avatar_id = "3034bbd37f2540ddb70c90c7f67b4f5c"
    
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    print("🚀 GERANDO COM API v2 DO HEYGEN!")
    print("=" * 50)
    
    # 1. Primeiro, confirma que temos avatares
    print("\n[1] Verificando avatares...")
    try:
        avatars_response = requests.get(
            "https://api.heygen.com/v2/avatars",
            headers=headers,
            timeout=10
        )
        
        if avatars_response.status_code == 200:
            avatars_data = avatars_response.json()
            print("✅ Avatares carregados!")
            
            # Procura o avatar específico
            avatar_encontrado = False
            if 'data' in avatars_data:
                for avatar in avatars_data['data']:
                    if avatar.get('avatar_id') == avatar_id:
                        print(f"✅ Avatar encontrado: {avatar.get('name', 'N/A')}")
                        avatar_encontrado = True
                        break
            
            if not avatar_encontrado:
                print(f"⚠️ Avatar {avatar_id} não encontrado. Usando primeiro disponível...")
                if avatars_data.get('data'):
                    avatar_id = avatars_data['data'][0].get('avatar_id')
                    print(f"🔄 Usando: {avatars_data['data'][0].get('name', 'N/A')}")
        else:
            print(f"❌ Erro ao carregar avatares: {avatars_response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    # 2. Tenta gerar um vídeo de teste
    print(f"\n[2] Testando geração de vídeo...")
    print(f"🤖 Avatar ID: {avatar_id}")
    
    # Carrega áudio de teste (o primeiro)
    project_root = Path(__file__).parent.resolve()
    audio_path = project_root / "output" / "reel_renato_melhorado" / "segments" / "01_abertura_audio.mp3"
    
    if not audio_path.exists():
        print(f"❌ Áudio não encontrado: {audio_path}")
        return False
    
    # Lê e codifica o áudio
    with open(audio_path, 'rb') as f:
        audio_data = f.read()
    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    # Testa diferentes estruturas de payload para v2
    payloads_v2 = [
        # Estrutura 1: Baseada na documentação atual
        {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "audio",
                    "audio_base64": audio_base64
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
        },
        
        # Estrutura 2: Mais simples
        {
            "avatar_id": avatar_id,
            "voice": {
                "type": "audio",
                "audio_base64": audio_base64
            },
            "background": "#000000",
            "dimension": "9:16"
        },
        
        # Estrutura 3: Mínima
        {
            "avatar_id": avatar_id,
            "audio_base64": audio_base64,
            "ratio": "9:16"
        }
    ]
    
    for i, payload in enumerate(payloads_v2, 1):
        print(f"\n🔄 Testando estrutura {i}...")
        try:
            response = requests.post(
                "https://api.heygen.com/v2/video/generate",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                video_id = result.get('data', {}).get('video_id') or result.get('data', {}).get('id')
                
                if video_id:
                    print(f"✅ SUCESSO! Vídeo criado: {video_id}")
                    print("⏳ Aguardando processamento...")
                    
                    # Monitora o processamento
                    for attempt in range(60):  # 10 minutos
                        time.sleep(10)
                        
                        # Verifica status
                        status_response = requests.get(
                            f"https://api.heygen.com/v2/video_status/{video_id}",
                            headers=headers,
                            timeout=30
                        )
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json().get('data', {})
                            status = status_data.get('status')
                            
                            print(f"⏳ Status: {status}")
                            
                            if status == 'completed':
                                video_url = status_data.get('video_url')
                                if video_url:
                                    print(f"🎉 VÍDEO PRONTO!")
                                    print(f"🔗 URL: {video_url}")
                                    
                                    # Baixa o vídeo
                                    print("📥 Baixando...")
                                    video_response = requests.get(video_url, stream=True)
                                    
                                    if video_response.status_code == 200:
                                        output_path = project_root / "output" / "teste_heygen_v2.mp4"
                                        with open(output_path, 'wb') as f:
                                            for chunk in video_response.iter_content(chunk_size=8192):
                                                f.write(chunk)
                                        
                                        print(f"✅ Sucesso! Vídeo salvo: {output_path}")
                                        return True
                            
                            elif status == 'failed':
                                error = status_data.get('error', 'Erro desconhecido')
                                print(f"❌ Falha: {error}")
                                break
                    
                    print("⏰ Timeout aguardando processamento")
                    break
                else:
                    print(f"❌ Sem video_id na resposta: {result}")
            
            elif response.status_code == 400:
                error_data = response.json()
                print(f"❌ Erro 400: {error_data}")
                print("💡 Pode ser problema no payload ou avatar")
            
            else:
                print(f"❌ Erro {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro na requisição: {str(e)}")
    
    print("\n❌ Todas as estruturas falharam")
    return False

if __name__ == "__main__":
    success = gerar_videos_heygen_v2()
    if success:
        print("\n🎉 SUCESSO! A API v2 funciona!")
        print("Agora podemos gerar todos os 5 vídeos automaticamente!")
    else:
        print("\n❌ API ainda não funcionou")
        print("Pode precisar ajustar payload ou verificar plano da conta")