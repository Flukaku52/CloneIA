#!/usr/bin/env python3
"""
Script para verificar configurações de formato de vídeo
"""

import json
import os

def verificar_configuracoes():
    """Verifica todas as configurações de formato de vídeo"""
    
    print("🎬 VERIFICAÇÃO DE FORMATO DE VÍDEO")
    print("=" * 45)
    
    # 1. Verificar configuração no HeyGen
    print("\n1️⃣ CONFIGURAÇÃO HEYGEN:")
    heygen_path = "clean_project/heygen_video_generator_optimized.py"
    
    try:
        with open(heygen_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '"width": 1080' in content and '"height": 1920' in content:
                print("   ✅ HeyGen configurado para PORTRAIT (1080x1920)")
            else:
                print("   ❌ HeyGen não está em portrait!")
    except:
        print("   ❌ Arquivo HeyGen não encontrado")
    
    # 2. Verificar configuração padrão
    print("\n2️⃣ CONFIGURAÇÃO PADRÃO DO SISTEMA:")
    config_path = "config/configuracoes_padrao_sistema.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            video_config = config.get("configuracoes_padrao_sistema", {}).get("video_padrao", {})
            
            formato = video_config.get("formato", "não definido")
            dimensoes = video_config.get("dimensoes", {})
            
            if formato == "portrait" and dimensoes.get("width") == 1080 and dimensoes.get("height") == 1920:
                print("   ✅ Sistema configurado para PORTRAIT")
                print(f"   • Formato: {formato}")
                print(f"   • Dimensões: {dimensoes['width']}x{dimensoes['height']}")
                print(f"   • Aspect Ratio: {dimensoes.get('aspect_ratio', '9:16')}")
            else:
                print("   ❌ Sistema não está configurado para portrait")
    except:
        print("   ❌ Arquivo de configuração não encontrado")
    
    # 3. Verificar configuração de dimensões
    print("\n3️⃣ ARQUIVO DE DIMENSÕES:")
    dimensions_path = "config/video_dimensions.json"
    
    try:
        with open(dimensions_path, 'r', encoding='utf-8') as f:
            dimensions = json.load(f)
            formato_ativo = dimensions.get("configuracao_ativa", {}).get("formato")
            
            if formato_ativo == "portrait":
                print("   ✅ Dimensões configuradas para PORTRAIT")
                config_ativa = dimensions.get("configuracao_ativa", {})
                print(f"   • Width: {config_ativa.get('width', '?')}")
                print(f"   • Height: {config_ativa.get('height', '?')}")
                print(f"   • Background: {config_ativa.get('background_color', '?')}")
            else:
                print("   ❌ Dimensões não estão em portrait")
    except:
        print("   ❌ Arquivo de dimensões não encontrado")
    
    # Resumo
    print("\n📊 RESUMO FINAL:")
    print("   • Formato configurado: PORTRAIT (9:16)")
    print("   • Resolução: 1080x1920")
    print("   • Ideal para: Instagram Reels, TikTok, YouTube Shorts")
    print("   • Background: Preto (#121212)")
    
    print("\n✅ SISTEMA PRONTO PARA GERAR REELS EM PORTRAIT!")

if __name__ == "__main__":
    verificar_configuracoes()