#!/usr/bin/env python3
"""
Script para limpar outputs antigos mantendo apenas o essencial
"""

import os
import shutil
from pathlib import Path

def analisar_outputs():
    """Analisa pasta output e categoriza o que manter/excluir"""
    
    # MANTER (arquivos essenciais/finais)
    manter = [
        # Reel final funcional - MANTER
        "output/reel_correto/segments/",  # Áudios finais usados
        "output/reel_correto/videos/intro_video.mp4",
        "output/reel_correto/videos/noticia1_video.mp4", 
        "output/reel_correto/videos/noticia2_video.mp4",
        "output/reel_correto/videos/noticia3_video.mp4",
        "output/reel_correto/videos/encerramento_video.mp4",
        "output/reel_correto/videos/videos_info.json",
        "output/reel_correto/reel_completo.mp4",  # Reel final
        "output/reel_correto/INSTRUCOES_EDICAO.txt",
        
        # Estrutura de pastas vazias para futuro uso
        "output/audio/",
        "output/videos/",
        "output/samples/"
    ]
    
    # EXCLUIR (testes antigos, duplicatas, temporários)
    excluir = []
    
    # Testes de áudio antigos
    excluir.extend([
        "output/audio/",  # Todos os testes antigos
        "output/teste_audio/",  # Pasta inteira de testes
    ])
    
    # Reel antigo/obsoleto
    excluir.extend([
        "output/reel_final/",  # Versão antiga
    ])
    
    # Arquivos duplicados/temporários do reel_correto
    excluir.extend([
        "output/reel_correto/audio/",  # Versões antigas dos áudios
        "output/reel_correto/reel_com_transicoes.mp4",  # Funcionou mas não é a final
        "output/reel_correto/reel_twist_basico.mp4",  # Não funcionou bem
        "output/reel_correto/reel_twist_simples.mp4",  # Não funcionou
        "output/reel_correto/relatorio_*.txt",  # Relatórios antigos
    ])
    
    # Vídeos HeyGen duplicados (com IDs)
    pattern_heygen = "output/reel_correto/videos/heygen_*.mp4"
    
    # Upload temporário
    excluir.extend([
        "output/elevenlabs_upload/",
    ])
    
    return manter, excluir, pattern_heygen

def calcular_tamanho_pasta(pasta):
    """Calcula tamanho total de uma pasta"""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(pasta):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total += os.path.getsize(filepath)
    except:
        pass
    return total

def limpar_outputs():
    """Executa limpeza inteligente dos outputs"""
    
    print("🧹 LIMPEZA INTELIGENTE DOS OUTPUTS")
    print("=" * 50)
    
    manter, excluir, pattern_heygen = analisar_outputs()
    
    # Analisar o que será excluído
    print("📋 ANÁLISE DOS OUTPUTS:")
    
    total_tamanho = 0
    itens_excluir = []
    
    # Verificar pastas/arquivos para excluir
    for item in excluir:
        if os.path.exists(item):
            if os.path.isdir(item):
                tamanho = calcular_tamanho_pasta(item)
                total_tamanho += tamanho
                itens_excluir.append((item, tamanho, "pasta"))
                print(f"  📁 {item} ({tamanho/1024/1024:.1f} MB)")
            elif os.path.isfile(item):
                tamanho = os.path.getsize(item)
                total_tamanho += tamanho
                itens_excluir.append((item, tamanho, "arquivo"))
                print(f"  📄 {item} ({tamanho/1024:.1f} KB)")
    
    # Verificar vídeos HeyGen duplicados
    videos_heygen = []
    videos_dir = "output/reel_correto/videos/"
    if os.path.exists(videos_dir):
        for arquivo in os.listdir(videos_dir):
            if arquivo.startswith("heygen_") and arquivo.endswith(".mp4"):
                filepath = os.path.join(videos_dir, arquivo)
                tamanho = os.path.getsize(filepath)
                total_tamanho += tamanho
                videos_heygen.append((filepath, tamanho))
                print(f"  📹 {filepath} ({tamanho/1024/1024:.1f} MB)")
    
    print(f"\n📊 RESUMO:")
    print(f"  • Pastas/arquivos antigos: {len(itens_excluir)}")
    print(f"  • Vídeos HeyGen duplicados: {len(videos_heygen)}")
    print(f"  • Espaço total liberado: {total_tamanho/1024/1024:.1f} MB")
    
    print(f"\n✅ ARQUIVOS QUE SERÃO MANTIDOS:")
    print(f"  • Reel final completo: reel_completo.mp4")
    print(f"  • 5 vídeos individuais: intro, noticia1-3, encerramento")
    print(f"  • 5 áudios finais em segments/")
    print(f"  • Instruções de edição")
    
    if not itens_excluir and not videos_heygen:
        print("✅ Outputs já estão limpos!")
        return
    
    # Executar limpeza
    print(f"\n🗑️ EXECUTANDO LIMPEZA...")
    excluidos = 0
    
    # Excluir pastas/arquivos
    for item, tamanho, tipo in itens_excluir:
        try:
            if tipo == "pasta":
                shutil.rmtree(item)
                print(f"  ✅ Pasta excluída: {item}")
            else:
                os.remove(item)
                print(f"  ✅ Arquivo excluído: {item}")
            excluidos += 1
        except Exception as e:
            print(f"  ❌ Erro ao excluir {item}: {str(e)}")
    
    # Excluir vídeos HeyGen duplicados
    for filepath, tamanho in videos_heygen:
        try:
            os.remove(filepath)
            print(f"  ✅ Vídeo duplicado excluído: {os.path.basename(filepath)}")
            excluidos += 1
        except Exception as e:
            print(f"  ❌ Erro ao excluir {filepath}: {str(e)}")
    
    # Criar pastas essenciais vazias se não existirem
    pastas_essenciais = ["output/audio", "output/videos", "output/samples"]
    for pasta in pastas_essenciais:
        os.makedirs(pasta, exist_ok=True)
    
    print(f"\n🎉 LIMPEZA CONCLUÍDA!")
    print(f"  • {excluidos} itens removidos")
    print(f"  • {total_tamanho/1024/1024:.1f} MB liberados")
    
    print(f"\n📁 ESTRUTURA FINAL DOS OUTPUTS:")
    print(f"📁 output/")
    print(f"  ├── 📁 audio/          # (vazia - para futuros áudios)")
    print(f"  ├── 📁 videos/         # (vazia - para futuros vídeos)")  
    print(f"  ├── 📁 samples/        # (vazia - para samples de voz)")
    print(f"  └── 📁 reel_correto/   # SEU REEL FINALIZADO")
    print(f"      ├── 📄 reel_completo.mp4      # REEL FINAL")
    print(f"      ├── 📄 INSTRUCOES_EDICAO.txt")
    print(f"      ├── 📁 segments/              # 5 áudios finais")
    print(f"      └── 📁 videos/                # 5 vídeos individuais")

if __name__ == "__main__":
    limpar_outputs()