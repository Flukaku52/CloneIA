#!/usr/bin/env python3
"""
Testa API HeyGen com estrutura 2024/2025
"""

import requests
import json

def testar_api_heygen(api_key):
    """Testa diferentes endpoints da API HeyGen"""
    
    print("🔍 TESTANDO API HEYGEN 2024/2025")
    print("=" * 50)
    
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # 1. Teste básico - info da conta
    print("\n[1] Testando autenticação...")
    endpoints_auth = [
        "https://api.heygen.com/v1/user.info",
        "https://api.heygen.com/v2/user.info", 
        "https://api.heygen.com/v1/account",
        "https://api.heygen.com/v2/account"
    ]
    
    for endpoint in endpoints_auth:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Sucesso! Dados: {data}")
                break
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
    
    # 2. Teste - listar avatares
    print("\n[2] Testando lista de avatares...")
    endpoints_avatars = [
        "https://api.heygen.com/v1/avatars",
        "https://api.heygen.com/v2/avatars",
        "https://api.heygen.com/v1/avatar/list",
        "https://api.heygen.com/v2/avatar/list"
    ]
    
    for endpoint in endpoints_avatars:
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Avatares encontrados!")
                # Mostra alguns avatares
                avatars = data.get('data', [])
                for avatar in avatars[:3]:
                    print(f"      - {avatar.get('name', 'N/A')}: {avatar.get('avatar_id', 'N/A')}")
                break
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
    
    # 3. Teste - endpoints de vídeo
    print("\n[3] Testando endpoints de vídeo...")
    endpoints_video = [
        "https://api.heygen.com/v1/video/generate",
        "https://api.heygen.com/v2/video/generate",
        "https://api.heygen.com/v1/talking_photo",
        "https://api.heygen.com/v2/talking_photo"
    ]
    
    for endpoint in endpoints_video:
        try:
            # Teste só com GET para ver se endpoint existe
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code != 404:
                print(f"   ✅ Endpoint existe! (status: {response.status_code})")
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
    
    print("\n📋 RESULTADO:")
    print("Se algum teste passou, a API funciona!")
    print("Se todos deram 404, pode ser problema de plano ou endpoint.")

if __name__ == "__main__":
    # Teste com sua API key
    api_key = "OTU2YjcxM2ZhZGY2NDE5Mjg3MzYzMmZlNjEyYjZiNzUtMTc0OTY5NDg0MQ=="
    testar_api_heygen(api_key)