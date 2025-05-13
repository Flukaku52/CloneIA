#!/usr/bin/env python3
"""
Script para testar a API do HeyGen.
"""
import os
import base64
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Obter a chave da API
api_key = os.environ.get("HEYGEN_API_KEY")
if not api_key or api_key == "sua_chave_aqui":
    # Usar a chave diretamente
    api_key = "OTU2YjcxM2ZhZGY2NDE5Mjg3MzYzMmZlNjEyYjZiNzUtMTc0Njc1NzMxNQ=="
print(f"API Key: {api_key}")

# Tentar decodificar a chave (se for Base64)
try:
    decoded = base64.b64decode(api_key).decode('utf-8')
    print(f"Decoded: {decoded}")
except Exception as e:
    print(f"Error decoding: {e}")

# Testar a API com a chave original
headers = {
    "X-Api-Key": api_key
}

print("\nTestando com a chave original:")
response = requests.get("https://api.heygen.com/v2/user/remaining_quota", headers=headers)
print(f"Status code: {response.status_code}")
print(f"Response: {response.text}")

# Testar a API com a chave decodificada (se for Base64)
try:
    decoded_key = base64.b64decode(api_key).decode('utf-8')
    headers_decoded = {
        "X-Api-Key": decoded_key
    }

    print("\nTestando com a chave decodificada:")
    response_decoded = requests.get("https://api.heygen.com/v2/user/remaining_quota", headers=headers_decoded)
    print(f"Status code: {response_decoded.status_code}")
    print(f"Response: {response_decoded.text}")
except Exception as e:
    print(f"Error testing with decoded key: {e}")

# Testar a API de upload
print("\nTestando a API de upload:")
upload_headers = {
    "Content-Type": "audio/mpeg",
    "X-Api-Key": api_key
}

# Criar um arquivo de áudio de teste
test_audio_path = "test_audio.mp3"
with open(test_audio_path, "wb") as f:
    f.write(b"Test audio content")

# Fazer upload do arquivo
with open(test_audio_path, "rb") as f:
    upload_response = requests.post("https://upload.heygen.com/v1/asset", headers=upload_headers, data=f)

print(f"Status code: {upload_response.status_code}")
print(f"Response: {upload_response.text}")

# Remover o arquivo de teste
import os
if os.path.exists(test_audio_path):
    os.remove(test_audio_path)

# Testar a API de avatares
print("\nTestando a API de avatares:")
avatars_response = requests.get("https://api.heygen.com/v2/avatars", headers=headers)
print(f"Status code: {avatars_response.status_code}")
print(f"Response: {avatars_response.text[:500]}...")  # Mostrar apenas os primeiros 500 caracteres
