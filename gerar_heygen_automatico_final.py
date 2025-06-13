#!/usr/bin/env python3
"""
Gera vídeo automaticamente no HeyGen com as configurações que funcionaram
"""

import os
import sys
import json
import time
import requests
import logging
from pathlib import Path

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def gerar_videos_heygen():
    """Gera todos os 5 segmentos no HeyGen automaticamente"""
    
    # Configurações que funcionaram
    api_key = "OGU5OTA4MGFhMTZkNDExNDhmNmZlNGI1ODY2ZDNhNGUtMTc0NzE5OTM4Mg=="
    avatar_id = "bd9548bed4984738a93b0db0c6c3edc9"
    
    # Caminhos dos áudios
    project_root = Path(__file__).parent.resolve()
    audio_dir = project_root / "output" / "reel_renato_melhorado" / "segments"
    
    audio_files = [
        "01_abertura_audio.mp3",
        "02_connecticut_vs_estados_pro-cripto_audio.mp3", 
        "03_brasileiros_investindo_em_cripto_audio.mp3",
        "04_bitcoin_30_dias_acima_de_100k_audio.mp3",
        "05_fechamento_audio.mp3"
    ]
    
    print("🚀 GERANDO REEL NO HEYGEN - MODO TURBO!")
    print("=" * 60)
    print(f"🔑 API Key: {api_key[:15]}...")
    print(f"🤖 Avatar: {avatar_id}")
    print(f"📊 Total de segmentos: {len(audio_files)}")
    print("🎯 Formato: 9:16 Portrait")
    
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    video_jobs = []
    
    # Gera todos os vídeos
    for i, audio_file in enumerate(audio_files, 1):
        audio_path = audio_dir / audio_file
        
        if not audio_path.exists():
            print(f"❌ Áudio não encontrado: {audio_path}")
            continue
        
        print(f"\n[{i}/{len(audio_files)}] 🎬 Gerando: {audio_file}")
        
        try:
            # Lê o áudio
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            # Codifica em base64
            import base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Payload otimizado para API v1
            payload = {
                "avatar_id": avatar_id,
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
            
            # Cria o vídeo
            response = requests.post(
                "https://api.heygen.com/v1/avatar/talking_photo",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                video_id = result.get('data', {}).get('id')
                
                if video_id:
                    print(f"   ✅ Vídeo criado! ID: {video_id}")
                    video_jobs.append({
                        'id': video_id,
                        'nome': audio_file.replace('_audio.mp3', ''),
                        'audio_file': audio_file
                    })
                else:
                    print(f"   ❌ Erro: Video ID não encontrado")
            else:
                print(f"   ❌ Erro: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
    
    if not video_jobs:
        print("\n❌ Nenhum vídeo foi criado")
        return False
    
    print(f"\n🎬 {len(video_jobs)} vídeos em processamento!")
    print("⏳ Aguardando processamento...")
    
    # Aguarda todos os vídeos
    completed_videos = []
    max_wait = 900  # 15 minutos
    start_time = time.time()
    
    while video_jobs and (time.time() - start_time) < max_wait:
        for job in video_jobs[:]:  # Cópia da lista para poder remover itens
            try:
                # Verifica status
                status_response = requests.get(
                    f"https://api.heygen.com/v1/avatar/talking_photo/{job['id']}",
                    headers=headers,
                    timeout=30
                )
                
                if status_response.status_code == 200:
                    data = status_response.json().get('data', {})
                    status = data.get('status')
                    
                    if status == 'completed':
                        video_url = data.get('result_url')
                        if video_url:
                            print(f"✅ {job['nome']} - Processado!")
                            completed_videos.append({
                                'nome': job['nome'],
                                'url': video_url,
                                'audio_file': job['audio_file']
                            })
                            video_jobs.remove(job)
                    
                    elif status == 'failed':
                        print(f"❌ {job['nome']} - Falhou!")
                        video_jobs.remove(job)
                    
                    else:
                        print(f"⏳ {job['nome']} - Status: {status}")
                
            except Exception as e:
                print(f"⚠️ Erro ao verificar {job['nome']}: {str(e)}")
        
        if video_jobs:  # Se ainda há vídeos processando
            time.sleep(15)
    
    # Baixa os vídeos completados
    if completed_videos:
        print(f"\n📥 Baixando {len(completed_videos)} vídeos...")
        
        output_dir = project_root / "output" / "videos_heygen_final"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for video in completed_videos:
            try:
                print(f"📥 Baixando: {video['nome']}")
                
                response = requests.get(video['url'], stream=True)
                if response.status_code == 200:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"{video['nome']}_{timestamp}.mp4"
                    output_path = output_dir / filename
                    
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"   ✅ Salvo: {output_path}")
                else:
                    print(f"   ❌ Erro ao baixar: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Erro: {str(e)}")
        
        print(f"\n🎉 SUCESSO! {len(completed_videos)} vídeos gerados!")
        print(f"📁 Pasta: {output_dir}")
        print("\n🎬 PRÓXIMOS PASSOS:")
        print("1. Abra os vídeos em um editor (CapCut, Premiere, etc.)")
        print("2. Junte os 5 vídeos na ordem correta")
        print("3. Use cortes secos (sem transições)")
        print("4. Exporte em 9:16 para Reels/TikTok")
        
        return True
    
    else:
        print("\n❌ Nenhum vídeo foi completado")
        return False

if __name__ == "__main__":
    success = gerar_videos_heygen()
    sys.exit(0 if success else 1)