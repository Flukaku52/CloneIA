#!/usr/bin/env python3
"""
Gera reel com nova API key e avatar do HeyGen
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

def testar_e_gerar_videos():
    """Testa nova API e gera todos os vídeos"""
    
    # NOVAS CONFIGURAÇÕES
    api_key = "OTU2YjcxM2ZhZGY2NDE5Mjg3MzYzMmZlNjEyYjZiNzUtMTc0OTY5NDg0MQ=="
    avatar_id = "3034bbd37f2540ddb70c90c7f67b4f5c"
    
    project_root = Path(__file__).parent.resolve()
    audio_dir = project_root / "output" / "reel_renato_melhorado" / "segments"
    
    audio_files = [
        ("01_abertura_audio.mp3", "Abertura"),
        ("02_connecticut_vs_estados_pro-cripto_audio.mp3", "Connecticut"), 
        ("03_brasileiros_investindo_em_cripto_audio.mp3", "Brasileiros"),
        ("04_bitcoin_30_dias_acima_de_100k_audio.mp3", "Bitcoin"),
        ("05_fechamento_audio.mp3", "Fechamento")
    ]
    
    print("🚀 TESTANDO NOVA API HEYGEN!")
    print("=" * 60)
    print(f"🔑 Nova API Key: {api_key[:20]}...")
    print(f"🤖 Novo Avatar: {avatar_id}")
    print(f"📊 Segmentos para gerar: {len(audio_files)}")
    
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Primeiro, testa se a API está funcionando
    print("\n🔍 [TESTE] Verificando API...")
    try:
        test_response = requests.get(
            "https://api.heygen.com/v1/user.info",
            headers={"X-Api-Key": api_key},
            timeout=10
        )
        
        if test_response.status_code == 200:
            print("✅ API Key válida!")
            user_info = test_response.json()
            print(f"👤 Usuário: {user_info.get('data', {}).get('name', 'N/A')}")
        else:
            print(f"⚠️ API retornou: {test_response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Erro no teste: {str(e)}")
    
    # Agora tenta gerar os vídeos
    print(f"\n🎬 GERANDO {len(audio_files)} VÍDEOS:")
    video_jobs = []
    
    for i, (arquivo, nome) in enumerate(audio_files, 1):
        audio_path = audio_dir / arquivo
        
        if not audio_path.exists():
            print(f"❌ [{i}] {nome} - Áudio não encontrado")
            continue
        
        print(f"\n[{i}/{len(audio_files)}] 🎤 {nome}")
        
        try:
            # Lê e codifica o áudio
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Tenta diferentes estruturas de payload
            payloads_para_testar = [
                # Estrutura v1 talking photo
                {
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
                },
                # Estrutura alternativa
                {
                    "avatar": {
                        "avatar_id": avatar_id,
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "audio",
                        "audio_base64": audio_base64
                    },
                    "background": "#000000",
                    "ratio": "9:16"
                }
            ]
            
            endpoints_para_testar = [
                "https://api.heygen.com/v1/avatar/talking_photo",
                "https://api.heygen.com/v1/talking_photo",
                "https://api.heygen.com/v1/video"
            ]
            
            video_created = False
            
            for endpoint in endpoints_para_testar:
                for j, payload in enumerate(payloads_para_testar):
                    try:
                        print(f"   🔄 Testando endpoint {endpoint} (payload {j+1})")
                        
                        response = requests.post(
                            endpoint,
                            headers=headers,
                            json=payload,
                            timeout=60
                        )
                        
                        print(f"   📊 Status: {response.status_code}")
                        
                        if response.status_code in [200, 201]:
                            result = response.json()
                            video_id = result.get('data', {}).get('id') or result.get('data', {}).get('video_id')
                            
                            if video_id:
                                print(f"   ✅ Vídeo criado! ID: {video_id}")
                                video_jobs.append({
                                    'id': video_id,
                                    'nome': nome,
                                    'arquivo': arquivo,
                                    'endpoint': endpoint
                                })
                                video_created = True
                                break
                            else:
                                print(f"   ⚠️ Resposta sem video_id: {result}")
                        else:
                            print(f"   ❌ Erro: {response.text[:100]}...")
                    
                    except Exception as e:
                        print(f"   ⚠️ Erro na requisição: {str(e)}")
                
                if video_created:
                    break
            
            if not video_created:
                print(f"   ❌ Falha em todos os endpoints para {nome}")
                
        except Exception as e:
            print(f"   ❌ Erro geral: {str(e)}")
    
    if not video_jobs:
        print("\n❌ NENHUM VÍDEO FOI CRIADO")
        print("💡 Tente usar a interface web: https://app.heygen.com")
        return False
    
    print(f"\n🎬 {len(video_jobs)} VÍDEOS EM PROCESSAMENTO!")
    print("⏳ Aguardando...")
    
    # Monitora o processamento
    completed_videos = []
    max_wait = 900  # 15 minutos
    start_time = time.time()
    
    while video_jobs and (time.time() - start_time) < max_wait:
        for job in video_jobs[:]:
            try:
                # Verifica status
                status_response = requests.get(
                    f"https://api.heygen.com/v1/talking_photo/{job['id']}",
                    headers={"X-Api-Key": api_key},
                    timeout=30
                )
                
                if status_response.status_code == 200:
                    data = status_response.json().get('data', {})
                    status = data.get('status')
                    
                    if status == 'completed':
                        video_url = data.get('result_url')
                        if video_url:
                            print(f"✅ {job['nome']} - PRONTO!")
                            completed_videos.append({
                                'nome': job['nome'],
                                'url': video_url,
                                'arquivo': job['arquivo']
                            })
                            video_jobs.remove(job)
                    
                    elif status == 'failed':
                        print(f"❌ {job['nome']} - FALHOU!")
                        video_jobs.remove(job)
                    
                    else:
                        print(f"⏳ {job['nome']} - {status}")
                
            except Exception as e:
                print(f"⚠️ Erro verificando {job['nome']}: {str(e)}")
        
        if video_jobs:
            time.sleep(10)
    
    # Baixa os vídeos
    if completed_videos:
        print(f"\n📥 BAIXANDO {len(completed_videos)} VÍDEOS...")
        
        output_dir = project_root / "output" / "videos_heygen_nova_api"
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
                    print(f"   ❌ Erro no download")
                    
            except Exception as e:
                print(f"   ❌ Erro: {str(e)}")
        
        print(f"\n🎉 SUCESSO! {len(completed_videos)} vídeos gerados!")
        print(f"📁 Pasta: {output_dir}")
        print("\n🎬 PRÓXIMOS PASSOS:")
        print("1. Junte os vídeos na ordem: Abertura → Connecticut → Brasileiros → Bitcoin → Fechamento")
        print("2. Use cortes secos (sem transições)")
        print("3. Exporte em 9:16 para Reels")
        
        return True
    
    else:
        print("\n❌ Nenhum vídeo foi completado")
        return False

if __name__ == "__main__":
    success = testar_e_gerar_videos()
    sys.exit(0 if success else 1)