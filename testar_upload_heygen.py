#!/usr/bin/env python3
"""
Testa diferentes formas de upload no HeyGen
"""

import requests
import json
from pathlib import Path

def testar_uploads():
    """Testa diferentes estruturas de upload"""
    
    api_key = "OTU2YjcxM2ZhZGY2NDE5Mjg3MzYzMmZlNjEyYjZiNzUtMTc0OTY5NDg0MQ=="
    
    project_root = Path(__file__).parent.resolve()
    audio_path = project_root / "output" / "reel_renato_melhorado" / "segments" / "01_abertura_audio.mp3"
    
    if not audio_path.exists():
        print(f"❌ Áudio não encontrado: {audio_path}")
        return
    
    print("🔄 TESTANDO DIFERENTES UPLOADS")
    print("=" * 50)
    
    # Teste 1: Upload v1 asset
    print("\n[1] Testando upload.heygen.com/v1/asset...")
    try:
        with open(audio_path, 'rb') as f:
            files = {'file': (audio_path.name, f, 'audio/mpeg')}
            data = {'type': 'audio'}
            
            response = requests.post(
                "https://upload.heygen.com/v1/asset",
                headers={"X-Api-Key": api_key},
                files=files,
                data=data,
                timeout=60
            )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Erro: {str(e)}")
    
    # Teste 2: Upload direto na API v2
    print("\n[2] Testando api.heygen.com/v2/assets...")
    try:
        with open(audio_path, 'rb') as f:
            files = {'file': (audio_path.name, f, 'audio/mpeg')}
            
            response = requests.post(
                "https://api.heygen.com/v2/assets",
                headers={"X-Api-Key": api_key},
                files=files,
                timeout=60
            )
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Erro: {str(e)}")
    
    # Teste 3: Upload com multipart diferente
    print("\n[3] Testando estrutura multipart completa...")
    try:
        files = {
            'asset': (audio_path.name, open(audio_path, 'rb'), 'audio/mpeg')
        }
        data = {
            'type': 'audio'
        }
        
        response = requests.post(
            "https://upload.heygen.com/v1/asset",
            headers={"X-Api-Key": api_key},
            files=files,
            data=data,
            timeout=60
        )
        
        files['asset'][1].close()  # Fecha o arquivo
        
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Erro: {str(e)}")
    
    # Teste 4: Verifica se tem outros endpoints
    print("\n[4] Testando endpoints alternativos...")
    endpoints_upload = [
        "https://api.heygen.com/v1/upload",
        "https://api.heygen.com/v2/upload", 
        "https://api.heygen.com/v1/assets",
        "https://upload.heygen.com/v2/asset"
    ]
    
    for endpoint in endpoints_upload:
        try:
            response = requests.get(
                endpoint,
                headers={"X-Api-Key": api_key},
                timeout=10
            )
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code != 404:
                print(f"      Response: {response.text[:100]}...")
        except Exception as e:
            print(f"   {endpoint}: Erro - {str(e)}")
    
    # Teste 5: Verifica quota/limites da conta
    print("\n[5] Verificando conta e limites...")
    try:
        response = requests.get(
            "https://api.heygen.com/v2/user/remaining_quota",
            headers={"X-Api-Key": api_key, "Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            quota_data = response.json()
            print(f"   Quota: {quota_data}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Erro: {str(e)}")

if __name__ == "__main__":
    testar_uploads()