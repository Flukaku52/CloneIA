#!/usr/bin/env python3
"""
Script simplificado para gerar vídeo com HeyGen
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

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("🎬 GERANDO VÍDEO COM HEYGEN")
    print("=" * 60)
    
    # Caminho do áudio
    audio_path = project_root / "output" / "audio" / "renato_connecticut_bitcoin_audio.mp3"
    
    if not audio_path.exists():
        print(f"❌ Erro: Áudio não encontrado em {audio_path}")
        return 1
    
    print(f"✅ Áudio encontrado: {audio_path}")
    
    # Informações do HeyGen
    avatar_config_path = project_root / "config" / "avatares_sistema.json"
    
    if avatar_config_path.exists():
        with open(avatar_config_path, 'r', encoding='utf-8') as f:
            avatares = json.load(f)
            
        # Pega o avatar atual
        avatares_list = avatares.get('avatares_disponiveis', [])
        avatar_atual = next((a for a in avatares_list if a.get('status') == 'ativo'), avatares_list[0] if avatares_list else None)
        
        if avatar_atual:
            avatar_id = avatar_atual.get('id', avatar_atual.get('avatar_id'))
            avatar_nome = avatar_atual['nome']
        else:
            avatar_id = "bd9548bed4984738a93b0db0c6c3edc9"
            avatar_nome = "flukakudabet"
        
        print(f"🤖 Avatar: {avatar_nome} (ID: {avatar_id})")
    else:
        # Avatar padrão se não encontrar config
        avatar_id = "bd9548bed4984738a93b0db0c6c3edc9"
        avatar_nome = "flukakudabet"
        print(f"🤖 Avatar padrão: {avatar_nome} (ID: {avatar_id})")
    
    print("\n📋 INSTRUÇÕES PARA GERAR O VÍDEO NO HEYGEN:")
    print("=" * 60)
    print("1. Acesse https://app.heygen.com")
    print("2. Clique em 'Create Video' → 'Avatar'")
    print(f"3. Selecione o avatar: {avatar_nome}")
    print("4. Clique em 'Upload Audio'")
    print(f"5. Faça upload do arquivo: {audio_path}")
    print("6. Configure:")
    print("   - Aspect Ratio: 9:16 (Portrait)")
    print("   - Background: Escolha um fundo adequado")
    print("7. Clique em 'Generate'")
    print("8. Aguarde o processamento")
    print("9. Baixe o vídeo gerado")
    
    print("\n💡 DICAS:")
    print("- Use o perfil 2 do HeyGen se disponível")
    print("- O vídeo será em formato portrait para Reels/TikTok")
    print("- Duração estimada: ~2-3 minutos")
    
    # Salva as instruções em arquivo
    instrucoes_path = project_root / "output" / "INSTRUCOES_HEYGEN_RENATO.txt"
    with open(instrucoes_path, 'w', encoding='utf-8') as f:
        f.write(f"INSTRUÇÕES PARA GERAR VÍDEO NO HEYGEN\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Áudio: {audio_path}\n")
        f.write(f"Avatar: {avatar_nome} (ID: {avatar_id})\n")
        f.write(f"Formato: 9:16 (Portrait)\n\n")
        f.write("Passos:\n")
        f.write("1. Acesse https://app.heygen.com\n")
        f.write("2. Create Video → Avatar\n")
        f.write(f"3. Selecione avatar: {avatar_nome}\n")
        f.write("4. Upload Audio\n")
        f.write(f"5. Upload: {audio_path}\n")
        f.write("6. Configure formato 9:16\n")
        f.write("7. Generate\n")
        f.write("8. Baixe o vídeo\n")
    
    print(f"\n📄 Instruções salvas em: {instrucoes_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())