#!/usr/bin/env python3
"""
Script para gerar todos os vídeos do reel usando o avatar HeyGen
"""

import os
import sys
import time
import json
from pathlib import Path

sys.path.append('/Users/renatosantannasilva/Documents/augment-projects/CloneIA')

sys.path.append('/Users/renatosantannasilva/Documents/augment-projects/CloneIA/clean_project')
from heygen_video_generator_optimized import HeyGenVideoGenerator
from gerenciar_avatares import GerenciadorAvatares

def gerar_videos_reel():
    # Sistema de rotação de avatares
    gerenciador = GerenciadorAvatares()
    avatar_id = gerenciador.obter_proximo_avatar()
    
    if not avatar_id:
        print("❌ Nenhum avatar disponível! Execute 'python gerenciar_avatares.py' para adicionar.")
        return False
    
    print("🎬 Iniciando geração de vídeos do reel...")
    print(f"🤖 Avatar ID: {avatar_id}")
    
    # Segmentos de áudio
    segments_dir = "/Users/renatosantannasilva/Documents/augment-projects/CloneIA/output/reel_correto/segments"
    output_dir = "/Users/renatosantannasilva/Documents/augment-projects/CloneIA/output/reel_correto/videos"
    
    # Criar diretório de vídeos se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Lista dos segmentos na ordem correta
    segments = [
        {"file": "intro_audio.mp3", "name": "intro", "title": "Abertura"},
        {"file": "noticia1_audio.mp3", "name": "noticia1", "title": "Empresas e Bitcoin"},
        {"file": "noticia2_audio.mp3", "name": "noticia2", "title": "Blockchain no Brasil"},
        {"file": "noticia3_audio.mp3", "name": "noticia3", "title": "Drex na Amazônia"},
        {"file": "encerramento_audio_final.mp3", "name": "encerramento", "title": "Fechamento"}
    ]
    
    # Inicializar gerador de vídeo HeyGen
    video_gen = HeyGenVideoGenerator()
    
    generated_videos = []
    
    for i, segment in enumerate(segments, 1):
        audio_path = os.path.join(segments_dir, segment["file"])
        video_name = f"{segment['name']}_video.mp4"
        video_path = os.path.join(output_dir, video_name)
        
        print(f"\n📹 [{i}/5] Gerando: {segment['title']}")
        print(f"🎵 Áudio: {segment['file']}")
        print(f"🎬 Vídeo: {video_name}")
        
        if not os.path.exists(audio_path):
            print(f"❌ Arquivo de áudio não encontrado: {audio_path}")
            continue
            
        try:
            # Gerar vídeo (HeyGen precisa de um script vazio, só o áudio)
            result = video_gen.generate_video(
                script="",  # Script vazio pois vamos usar apenas o áudio
                audio_path=audio_path,
                output_path=video_path,
                avatar_id=avatar_id
            )
            
            if result and os.path.exists(video_path):
                print(f"✅ Vídeo gerado: {video_path}")
                generated_videos.append({
                    "segment": segment["name"],
                    "title": segment["title"],
                    "video_path": video_path,
                    "audio_path": audio_path
                })
            else:
                print(f"❌ Erro ao gerar vídeo para: {segment['title']}")
                
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            
        # Pausa entre gerações para não sobrecarregar a API
        if i < len(segments):
            print("⏳ Aguardando 5 segundos...")
            time.sleep(5)
    
    print(f"\n🎉 Geração concluída!")
    print(f"📊 Vídeos gerados: {len(generated_videos)}/{len(segments)}")
    
    if generated_videos:
        print("\n📋 RESUMO DOS VÍDEOS GERADOS:")
        for video in generated_videos:
            print(f"  • {video['title']}: {video['video_path']}")
            
        # Salvar informações para possível junção automática
        info_path = os.path.join(output_dir, "videos_info.json")
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(generated_videos, f, indent=2, ensure_ascii=False)
            
        print(f"\n📝 Informações salvas em: {info_path}")
        print("\n🎬 PRÓXIMOS PASSOS:")
        print("1. Verificar qualidade dos vídeos gerados")
        print("2. Usar CapCut para juntar com cortes secos")
        print("3. Ou aguardar tentativa de junção automática")
        
    return generated_videos

if __name__ == "__main__":
    gerar_videos_reel()