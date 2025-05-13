#!/usr/bin/env python3
"""
Script para testar a geração de vídeo com um avatar específico usando a nova chave de API.
"""
import os
import json
import requests
import time
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
API_KEY = os.getenv("HEYGEN_API_KEY")
AVATAR_ID = "189d9626f12f473f8f6e927c5ec482fa"  # ID do avatar atual
VOICE_ID = "7e4e469711394247bb252ff848ac061d"  # ID da voz em português
SCRIPT = "E aí cambada! Este é um teste da API do HeyGen para o quadro Rapidinha Cripto. Estamos testando a geração de vídeo com o meu avatar personalizado."

# Diretório para salvar o vídeo
output_dir = os.path.join(os.getcwd(), "output", "videos")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"rapidinha_heygen_{int(time.time())}.mp4")

def generate_video():
    """
    Gera um vídeo usando o avatar específico e a voz em português.

    Returns:
        str: Caminho para o vídeo gerado, ou None se falhar.
    """
    # URLs base da API
    api_base_url = "https://api.heygen.com/v1"
    video_url = "https://api.heygen.com/v2/video/generate"

    # Configurar cabeçalhos
    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }

    # Configurar dados do vídeo
    video_data = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": AVATAR_ID,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": SCRIPT,
                    "voice_id": VOICE_ID
                },
                "background": {
                    "type": "color",
                    "value": "#121212"  # Cor de fundo (preto)
                }
            }
        ],
        "dimension": {
            "width": 1280,
            "height": 720
        },
        "caption": False
    }

    try:
        print(f"Usando avatar ID: {AVATAR_ID}")
        print(f"Usando voz ID: {VOICE_ID}")
        print("Gerando vídeo com o HeyGen...")
        print(f"Dados da requisição: {json.dumps(video_data, indent=2)}")

        # Criar o vídeo
        video_response = requests.post(video_url, headers=headers, json=video_data)
        print(f"Status code: {video_response.status_code}")

        if video_response.status_code == 200:
            video_result = video_response.json()
            print(f"Resposta: {json.dumps(video_result, indent=2)}")

            # Verificar se o ID do vídeo está na resposta
            if "data" in video_result and "video_id" in video_result["data"]:
                video_id = video_result["data"]["video_id"]
            else:
                print("Falha ao criar vídeo. Nenhum ID de vídeo retornado.")
                print(f"Resposta completa: {video_result}")
                return None
        else:
            print(f"Erro: {video_response.status_code}")
            print(f"Resposta: {video_response.text}")
            return None

        # Verificar o status do vídeo e baixá-lo quando estiver pronto
        print(f"Vídeo em processamento (ID: {video_id}). Aguardando conclusão...")

        status_url = f"{api_base_url}/video_status.get?video_id={video_id}"
        max_attempts = 60  # 5 minutos (5 segundos por tentativa)

        for attempt in range(max_attempts):
            status_response = requests.get(status_url, headers=headers)
            status_response.raise_for_status()

            status_result = status_response.json()
            status = status_result.get("data", {}).get("status")

            if status == "completed":
                # Vídeo pronto, baixar
                video_url = status_result.get("data", {}).get("video_url")

                if video_url:
                    try:
                        print(f"Vídeo pronto! Baixando de {video_url}...")
                        video_content_response = requests.get(video_url)
                        video_content_response.raise_for_status()

                        with open(output_path, 'wb') as f:
                            f.write(video_content_response.content)

                        print(f"Vídeo salvo em {output_path}")

                        # Salvar uma cópia do vídeo com o ID para referência
                        video_id_path = os.path.join(os.path.dirname(output_path), f"heygen_{video_id}.mp4")
                        with open(video_id_path, 'wb') as f:
                            f.write(video_content_response.content)

                        print(f"Cópia do vídeo salva em {video_id_path}")

                        return output_path
                    except Exception as e:
                        print(f"Erro ao baixar o vídeo: {e}")
                        return None
                else:
                    print("URL do vídeo não encontrada na resposta.")
                    return None

            elif status == "failed":
                error = status_result.get("data", {}).get("error")
                print(f"Falha ao processar o vídeo: {error}")
                return None

            # Aguardar 5 segundos antes de verificar novamente
            print(f"Status do vídeo: {status}. Verificando novamente em 5 segundos...")
            time.sleep(5)

        print("Tempo limite excedido ao aguardar o processamento do vídeo.")
        return None

    except Exception as e:
        print(f"Erro ao gerar vídeo: {e}")
        return None

if __name__ == "__main__":
    print("\n=== Testando geração de vídeo com avatar específico ===\n")

    # Verificar se a chave da API está configurada
    if not API_KEY:
        print("API key do HeyGen não configurada. Verifique o arquivo .env")
        exit(1)

    print(f"API key do HeyGen: {API_KEY[:5]}...{API_KEY[-5:]}")

    # Gerar vídeo
    video_path = generate_video()

    if video_path:
        print(f"\nVídeo gerado com sucesso! Salvo em: {video_path}")
    else:
        print("\nFalha ao gerar o vídeo.")

    print("\n=== Teste concluído ===\n")
