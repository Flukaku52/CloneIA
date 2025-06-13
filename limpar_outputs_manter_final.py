#!/usr/bin/env python3
"""
Limpa todos os outputs, mantendo apenas os áudios finais que vamos usar
"""

import os
import shutil
from pathlib import Path

def limpar_outputs():
    """Remove outputs desnecessários, mantém só os finais"""
    
    project_root = Path(__file__).parent.resolve()
    output_dir = project_root / "output"
    
    if not output_dir.exists():
        print("📁 Diretório output não existe")
        return
    
    # Arquivos que vamos MANTER (finais melhorados)
    manter_dir = "reel_renato_melhorado"
    manter_arquivos = [
        "01_abertura_audio.mp3",
        "02_connecticut_vs_estados_pro-cripto_audio.mp3", 
        "03_brasileiros_investindo_em_cripto_audio.mp3",
        "04_bitcoin_30_dias_acima_de_100k_audio.mp3",
        "05_fechamento_audio.mp3"
    ]
    
    print("🧹 LIMPANDO OUTPUTS DESNECESSÁRIOS")
    print("=" * 50)
    
    # Lista tudo no output
    items_removidos = 0
    
    for item in output_dir.iterdir():
        if item.name == manter_dir:
            # Manter esta pasta, mas limpar dentro dela se necessário
            segments_dir = item / "segments"
            if segments_dir.exists():
                for arquivo in segments_dir.iterdir():
                    if arquivo.name not in manter_arquivos:
                        print(f"🗑️  Removendo: {arquivo.name}")
                        arquivo.unlink()
                        items_removidos += 1
                    else:
                        print(f"✅ Mantendo: {arquivo.name}")
            
            # Remove outros arquivos na pasta principal
            for arquivo in item.iterdir():
                if arquivo.name != "segments":
                    print(f"🗑️  Removendo: {item.name}/{arquivo.name}")
                    if arquivo.is_file():
                        arquivo.unlink()
                    elif arquivo.is_dir():
                        shutil.rmtree(arquivo)
                    items_removidos += 1
        else:
            # Remove completamente outras pastas/arquivos
            print(f"🗑️  Removendo pasta: {item.name}")
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
            items_removidos += 1
    
    print("\n📊 RESULTADO:")
    print(f"   • Items removidos: {items_removidos}")
    print(f"   • Mantidos: {len(manter_arquivos)} áudios finais")
    
    # Verifica se os arquivos finais existem
    final_dir = output_dir / manter_dir / "segments"
    if final_dir.exists():
        arquivos_existentes = [f for f in manter_arquivos if (final_dir / f).exists()]
        print(f"   • Arquivos finais confirmados: {len(arquivos_existentes)}/{len(manter_arquivos)}")
        
        if len(arquivos_existentes) == len(manter_arquivos):
            print("\n✅ SUCESSO! Apenas os áudios finais foram mantidos")
            print(f"📁 Localização: {final_dir}")
        else:
            print("\n⚠️  ATENÇÃO: Alguns arquivos finais estão faltando")
            faltando = [f for f in manter_arquivos if not (final_dir / f).exists()]
            for arquivo in faltando:
                print(f"   ❌ Faltando: {arquivo}")
    else:
        print("\n❌ ERRO: Diretório dos áudios finais não existe")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("   1. Use os 5 áudios finais no HeyGen")
    print("   2. Avatar: bd9548bed4984738a93b0db0c6c3edc9") 
    print("   3. Formato: 9:16 Portrait")
    print("   4. Edite juntando com cortes secos")

if __name__ == "__main__":
    limpar_outputs()