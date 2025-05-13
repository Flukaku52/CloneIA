#!/usr/bin/env python3
"""
Script para testar a geração completa de áudio e vídeo para o desafio.
"""
import os
import sys
import json
from datetime import datetime

# Adicionar o diretório raiz ao path do Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.audio import AudioGenerator
from core.text import TextProcessor
from core.utils import open_audio_file
from heygen_video_generator import HeyGenVideoGenerator

# Texto de entrada - desafio para os espectadores
input_text = """E aí cambada, tô de volta na área e bora de Rapidinha! Mas dessa vez eu tenho um desafio pra vocês, tem algo "diferente" nesse vídeo, você consegue adivinhar o que? Bota aí nos comentários pra ver se você acerta, no fim do vídeo eu dou a resposta!"""

# Timestamp para os arquivos
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
base_filename = f"desafio_completo_{timestamp}"

# Diretórios de saída
output_dir = os.path.join(os.getcwd(), "output")
audio_dir = os.path.join(output_dir, "audio")
video_dir = os.path.join(output_dir, "videos")

# Garantir que os diretórios existam
for directory in [output_dir, audio_dir, video_dir]:
    os.makedirs(directory, exist_ok=True)

# Etapa 1: Otimizar o texto para melhor entonação
print("\n=== Etapa 1: Otimizando o texto para melhor entonação ===")
processor = TextProcessor()

# Versão original do texto otimizado
optimized_text = processor.optimize_for_speech(input_text)
print(f"Texto otimizado padrão: {optimized_text}")

# Versão personalizada com ajustes manuais para melhor entonação
custom_text = "EAÍCAMBADA tô de volta na área e- bora de Rapidinha mas- DESSA VEZ eu tenho um DESAFIO pra vocês tem algo \"diferente\" nesse vídeo você consegue adivinhar o QUE Bota aí nos comentários pra ver se você ACERTA no fim do vídeo eu dou a resposta"
print(f"Texto otimizado personalizado: {custom_text}")

# Etapa 2: Gerar o áudio com o perfil FlukakuFluido
print("\n=== Etapa 2: Gerando áudio com o perfil FlukakuFluido ===")
audio_generator = AudioGenerator(voice_profile="fluido")

# Gerar o áudio com o texto personalizado
audio_path = os.path.join(audio_dir, f"{base_filename}.mp3")
audio_result = audio_generator.generate_audio(custom_text, audio_path, optimize=False)

if audio_result:
    print(f"Áudio gerado com sucesso: {audio_result}")

    # Abrir o arquivo de áudio
    print("Abrindo o arquivo de áudio...")
    open_audio_file(audio_result)

    # Exibir as configurações usadas
    config = audio_generator.voice_settings
    print("\nConfigurações de voz usadas:")
    print(json.dumps(config, indent=2))
else:
    print("Falha ao gerar o áudio.")
    sys.exit(1)

# Etapa 3: Gerar o vídeo com o HeyGen
print("\n=== Etapa 3: Gerando vídeo com o HeyGen ===")
heygen_generator = HeyGenVideoGenerator()

# Verificar se o avatar está configurado
if not heygen_generator.avatar_id:
    print("Avatar não configurado. Usando o ID padrão.")
    heygen_generator.avatar_id = "189d9626f12f473f8f6e927c5ec482fa"  # ID do avatar atual

print(f"Usando avatar com ID: {heygen_generator.avatar_id}")

# Gerar o vídeo
video_path = os.path.join(video_dir, f"{base_filename}.mp4")
video_result = heygen_generator.generate_video(
    script=custom_text,  # Texto para fallback, caso o áudio falhe
    audio_path=audio_result,  # Usar o áudio gerado
    output_path=video_path,
    folder_name="augment"  # Salvar na pasta "augment" do HeyGen
)

if video_result:
    print(f"Vídeo gerado com sucesso: {video_result}")
    print("\nProcesso completo! O vídeo do desafio foi gerado com sucesso.")
else:
    print("Falha ao gerar o vídeo.")
