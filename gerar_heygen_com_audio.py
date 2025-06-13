#!/usr/bin/env python3
"""
Gerador HeyGen usando upload de áudio do ElevenLabs
"""

import requests
import json
import time
import base64
from pathlib import Path

def gerar_videos_com_audio():
    """Gera vídeos usando os arquivos de áudio do ElevenLabs"""
    
    api_key = "OTU2YjcxM2ZhZGY2NDE5Mjg3MzYzMmZlNjEyYjZiNzUtMTc0OTY5NDg0MQ=="
    avatar_id = "3034bbd37f2540ddb70c90c7f67b4f5c"
    
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    project_root = Path(__file__).parent.resolve()
    audio_dir = project_root / "output" / "reel_renato_melhorado" / "segments"
    
    audio_files = [
        ("01_abertura_audio.mp3", "Abertura"),
        ("02_connecticut_vs_estados_pro-cripto_audio.mp3", "Connecticut"), 
        ("03_brasileiros_investindo_em_cripto_audio.mp3", "Brasileiros"),
        ("04_bitcoin_30_dias_acima_de_100k_audio.mp3", "Bitcoin"),
        ("05_fechamento_audio.mp3", "Fechamento")
    ]
    
    print("🚀 HEYGEN COM ÁUDIO ELEVENLABS!")
    print("=" * 60)
    print(f"🤖 Avatar: {avatar_id}")
    print(f"🎵 Usando áudios do ElevenLabs")
    print(f"📊 Vídeos para gerar: {len(audio_files)}")
    print()
    
    video_jobs = []
    
    for i, (arquivo, nome) in enumerate(audio_files, 1):
        audio_path = audio_dir / arquivo
        
        if not audio_path.exists():
            print(f"❌ Áudio não encontrado: {audio_path}")
            continue
            
        print(f"[{i}/{len(audio_files)}] 🎬 {nome}")
        print(f"   📁 {audio_path.name}")
        
        # Lê e codifica o áudio em base64
        try:
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            print(f"   📊 Áudio: {len(audio_data)} bytes")
            
        except Exception as e:
            print(f"   ❌ Erro lendo áudio: {str(e)}")
            continue
        
        # Payload usando áudio base64
        payload = {
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
        }
        
        try:
            print("   🔄 Enviando para HeyGen...")
            
            response = requests.post(
                "https://api.heygen.com/v2/video/generate",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                video_id = result.get('data', {}).get('video_id')
                
                if video_id:
                    print(f"   ✅ Vídeo criado! ID: {video_id}")
                    video_jobs.append({
                        'id': video_id,
                        'nome': nome,
                        'arquivo': arquivo
                    })
                else:
                    print(f"   ❌ Sem video_id: {result}")
            else:
                error_data = response.text
                print(f"   ❌ Erro: {error_data}")
                
        except Exception as e:
            print(f"   ❌ Erro na requisição: {str(e)}")
        
        # Pausa entre requisições
        time.sleep(3)
    
    if not video_jobs:
        print("\n❌ Nenhum vídeo foi criado")
        return False
    
    print(f"\n🎬 {len(video_jobs)} VÍDEOS CRIADOS!")
    print("⏳ Aguardando processamento...")
    
    # Monitora todos os vídeos
    completed_videos = []
    max_wait = 1800  # 30 minutos
    start_time = time.time()
    
    while video_jobs and (time.time() - start_time) < max_wait:
        for job in video_jobs[:]:
            try:
                # Verifica status
                status_response = requests.get(
                    f"https://api.heygen.com/v1/video_status.get?video_id={job['id']}",
                    headers={"X-Api-Key": api_key},
                    timeout=30
                )
                
                if status_response.status_code == 200:
                    data = status_response.json().get('data', {})
                    status = data.get('status')
                    
                    if status == 'completed':
                        video_url = data.get('video_url')
                        if video_url:
                            print(f"✅ {job['nome']} - PRONTO!")
                            completed_videos.append({
                                'nome': job['nome'],
                                'url': video_url,
                                'arquivo': job['arquivo']
                            })
                            video_jobs.remove(job)
                    
                    elif status == 'failed':
                        error = data.get('error', 'Erro desconhecido')
                        print(f"❌ {job['nome']} - FALHOU: {error}")
                        video_jobs.remove(job)
                    
                    else:
                        print(f"⏳ {job['nome']} - {status}")
                
            except Exception as e:
                print(f"⚠️ Erro verificando {job['nome']}: {str(e)}")
        
        if video_jobs:
            time.sleep(15)
    
    # Baixa os vídeos
    if completed_videos:
        print(f"\n📥 BAIXANDO {len(completed_videos)} VÍDEOS...")
        
        output_dir = project_root / "output" / "videos_heygen_final"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for video in completed_videos:
            try:
                print(f"📥 {video['nome']}")
                
                response = requests.get(video['url'], stream=True)
                if response.status_code == 200:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"{video['nome']}_{timestamp}.mp4"
                    output_path = output_dir / filename
                    
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"   ✅ {filename}")
                else:
                    print(f"   ❌ Erro no download: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Erro: {str(e)}")
        
        print(f"\n🎉 SUCESSO! {len(completed_videos)} vídeos gerados!")
        print(f"📁 Pasta: {output_dir}")
        print("\n🎬 PRÓXIMOS PASSOS:")
        print("1. Edite juntando na ordem: Abertura → Connecticut → Brasileiros → Bitcoin → Fechamento")
        print("2. Use cortes secos (sem transições)")
        print("3. Exporte em 9:16 para Reels")
        
        return True
    
    else:
        print("\n❌ Nenhum vídeo foi completado")
        return False

if __name__ == "__main__":
    success = gerar_videos_com_audio()
    if success:
        print("\n🎉 REEL GERADO COM SUCESSO!")
    else:
        print("\n❌ Falha na geração do reel")