#!/usr/bin/env python3
"""
Script para juntar todos os vídeos do reel com cortes secos
"""

import os
import subprocess
from pathlib import Path

def juntar_videos_reel():
    videos_dir = "/Users/renatosantannasilva/Documents/augment-projects/CloneIA/output/reel_correto/videos"
    output_path = "/Users/renatosantannasilva/Documents/augment-projects/CloneIA/output/reel_correto/reel_completo.mp4"
    
    # Lista dos vídeos na ordem correta
    videos_ordem = [
        "intro_video.mp4",
        "noticia1_video.mp4", 
        "noticia2_video.mp4",
        "noticia3_video.mp4",
        "encerramento_video.mp4"
    ]
    
    print("🎬 Juntando vídeos do reel...")
    
    # Verificar se todos os vídeos existem
    for video in videos_ordem:
        video_path = os.path.join(videos_dir, video)
        if not os.path.exists(video_path):
            print(f"❌ Vídeo não encontrado: {video}")
            return False
            
    print("✅ Todos os vídeos encontrados!")
    
    # Criar arquivo de lista para o FFmpeg
    list_file = os.path.join(videos_dir, "videos_list.txt")
    with open(list_file, 'w') as f:
        for video in videos_ordem:
            video_path = os.path.join(videos_dir, video)
            f.write(f"file '{video_path}'\n")
    
    print("📝 Lista de vídeos criada")
    
    # Comando FFmpeg para concatenar
    cmd = [
        "ffmpeg", "-y",  # -y para sobrescrever
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",  # Copiar sem recodificar para cortes secos
        output_path
    ]
    
    print("🔧 Executando FFmpeg...")
    print(f"Comando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ Reel completo criado: {output_path}")
            
            # Verificar tamanho do arquivo
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                print(f"📊 Tamanho: {file_size:.1f} MB")
                return True
            else:
                print("❌ Arquivo não foi criado")
                return False
        else:
            print("❌ Erro no FFmpeg:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout: FFmpeg demorou muito")
        return False
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False
    finally:
        # Limpar arquivo temporário
        if os.path.exists(list_file):
            os.remove(list_file)

if __name__ == "__main__":
    sucesso = juntar_videos_reel()
    if sucesso:
        print("\n🎉 REEL COMPLETO PRONTO!")
        print("📁 Arquivo: output/reel_correto/reel_completo.mp4")
        print("🎬 Agora você pode revisar e publicar!")
    else:
        print("\n❌ Falha na junção. Use CapCut manualmente.")