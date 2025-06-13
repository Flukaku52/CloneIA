#!/usr/bin/env python3
"""
Script para gerar vídeo no HeyGen com o áudio do Renato
"""

import os
import sys
import json
import time
import logging
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

from clean_project.heygen_video_generator_optimized import HeyGenVideoGenerator

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("🎬 GERANDO VÍDEO NO HEYGEN")
    print("=" * 60)
    
    # Caminho do áudio
    audio_path = project_root / "output" / "audio" / "renato_connecticut_bitcoin_audio.mp3"
    
    if not audio_path.exists():
        print(f"❌ Erro: Áudio não encontrado em {audio_path}")
        return 1
    
    # Inicializa o gerador HeyGen
    heygen = HeyGenVideoGenerator()
    
    print(f"📁 Áudio: {audio_path}")
    avatar_name = getattr(heygen, 'avatar_name', 'Desconhecido')
    print(f"🤖 Avatar: {avatar_name} (ID: {heygen.avatar_id})")
    print(f"🎯 Perfil HeyGen: {os.getenv('HEYGEN_PROFILE', 'Padrão')}")
    print("🔄 Enviando para HeyGen...")
    
    # Gera o vídeo
    output_dir = project_root / "output" / "videos"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"renato_connecticut_bitcoin_{timestamp}.mp4"
    
    try:
        # Cria o vídeo
        video_id = heygen.create_video_from_audio(str(audio_path))
        
        if video_id:
            print(f"✅ Vídeo criado! ID: {video_id}")
            print("⏳ Aguardando processamento...")
            
            # Aguarda o processamento
            video_url = heygen.wait_for_video(video_id)
            
            if video_url:
                print(f"✅ Vídeo processado!")
                print(f"🔗 URL: {video_url}")
                
                # Baixa o vídeo
                if heygen.download_video(video_url, str(output_path)):
                    print(f"✅ Vídeo baixado: {output_path}")
                    print("\n🎉 SUCESSO! Vídeo gerado com sucesso!")
                else:
                    print("❌ Erro ao baixar o vídeo")
                    print(f"💡 Baixe manualmente de: {video_url}")
            else:
                print("❌ Erro no processamento do vídeo")
        else:
            print("❌ Erro ao criar o vídeo")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())