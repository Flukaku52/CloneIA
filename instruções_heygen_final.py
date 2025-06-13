#!/usr/bin/env python3
"""
Instruções finais para gerar o reel no HeyGen
"""

import os
from pathlib import Path

def mostrar_instrucoes():
    """Mostra instruções otimizadas para HeyGen"""
    
    project_root = Path(__file__).parent.resolve()
    audio_dir = project_root / "output" / "reel_renato_melhorado" / "segments"
    
    audio_files = [
        ("01_abertura_audio.mp3", "Abertura"),
        ("02_connecticut_vs_estados_pro-cripto_audio.mp3", "Connecticut vs Estados Pro-Cripto"), 
        ("03_brasileiros_investindo_em_cripto_audio.mp3", "Brasileiros Investindo em Cripto"),
        ("04_bitcoin_30_dias_acima_de_100k_audio.mp3", "Bitcoin 30 Dias Acima de 100k"),
        ("05_fechamento_audio.mp3", "Fechamento")
    ]
    
    print("🚀 METE MARCHA! INSTRUÇÕES PARA HEYGEN")
    print("=" * 60)
    print("🎯 CONFIGURAÇÕES:")
    print("   • Avatar: 3034bbd37f2540ddb70c90c7f67b4f5c")
    print("   • Formato: 9:16 (Portrait)")
    print("   • Background: Escuro")
    print()
    
    print("🔥 PASSO A PASSO RÁPIDO:")
    print("1. Acesse: https://app.heygen.com")
    print("2. Create Video → Upload Audio")
    print("3. Para cada áudio abaixo:")
    print()
    
    for i, (arquivo, nome) in enumerate(audio_files, 1):
        audio_path = audio_dir / arquivo
        if audio_path.exists():
            print(f"   [{i}/5] {nome}")
            print(f"   📂 {audio_path}")
            print(f"   ➡️  Upload → Avatar: 3034bbd37f2540ddb70c90c7f67b4f5c → 9:16 → Generate")
            print()
        else:
            print(f"   ❌ ARQUIVO NÃO ENCONTRADO: {arquivo}")
            print()
    
    print("4. Baixe os 5 vídeos gerados")
    print("5. Edite juntando com CORTES SECOS")
    print()
    
    print("⚡ ORDEM DOS VÍDEOS:")
    print("   1. Abertura → 2. Connecticut → 3. Brasileiros → 4. Bitcoin → 5. Fechamento")
    print()
    
    print("🎬 SOFTWARE DE EDIÇÃO:")
    print("   • CapCut (mobile/desktop)")
    print("   • Premiere Pro")
    print("   • DaVinci Resolve")
    print()
    
    print("✅ DICAS IMPORTANTES:")
    print("   • Use CORTES SECOS (sem transições)")
    print("   • Mantenha formato 9:16")
    print("   • Background escuro para contraste")
    print("   • Teste o áudio antes de gerar")
    print()
    
    # Verifica se todos os arquivos existem
    missing_files = []
    for arquivo, nome in audio_files:
        audio_path = audio_dir / arquivo
        if not audio_path.exists():
            missing_files.append(arquivo)
    
    if missing_files:
        print("⚠️  ARQUIVOS EM FALTA:")
        for arquivo in missing_files:
            print(f"   • {arquivo}")
        print()
        print("💡 Execute primeiro: python gerar_reel_renato_melhorado.py")
    else:
        print("🎉 TODOS OS ÁUDIOS ESTÃO PRONTOS!")
        print("🚀 BORA GERAR NO HEYGEN!")
    
    print()
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    mostrar_instrucoes()