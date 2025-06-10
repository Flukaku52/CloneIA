#!/usr/bin/env python3
"""
Script para limpar arquivos desnecessários do projeto CloneIA
"""

import os
import shutil
from pathlib import Path

def analisar_projeto():
    """Analisa todos os arquivos do projeto e categoriza"""
    
    # Arquivos ESSENCIAIS (nunca excluir)
    essenciais = {
        # Core do sistema
        "core/",
        "config/",
        "requirements.txt",
        "clean_project/",
        
        # Configurações importantes
        "config/voice_config.json",
        "config/avatar_config.json", 
        "config/heygen_profiles.json",
        "config/configuracoes_padrao_sistema.json",
        
        # Scripts principais
        "generate_reel_correto.py",
        "gerar_videos_reel.py",
        "juntar_videos_reel.py",
        
        # Outputs importantes
        "output/reel_correto/",
        
        # Estrutura básica
        "venv/",
        ".git/",
        "README.md"
    }
    
    # Arquivos TEMPORÁRIOS/LOGS (podem ser excluídos)
    excluir = []
    
    # Arquivos de análise/teste antigos
    excluir.extend([
        "analyze_voice_videos.py",
        "compare_voice_analysis.py", 
        "create_natural_profile.py",
        "voice_quality_analysis.py",
        "test_voice_script.py",
        "regenerar_encerramento.py"
    ])
    
    # Scripts de twist que não funcionaram
    excluir.extend([
        "criar_reel_twist.py",
        "criar_reel_twist_ffmpeg.py", 
        "criar_reel_twist_simples.py",
        "criar_reel_twist_basico.py",
        "melhorar_reel.py"
    ])
    
    # Scripts de reel antigos
    excluir.extend([
        "generate_reel_final.py"
    ])
    
    # Logs
    excluir.extend([
        "cloneia.log",
        "comparison_videos.log",
        "generate_encerramento.log", 
        "generate_reel_correto.log",
        "generate_reel_segments.log",
        "mesclar_audios.log"
    ])
    
    # Guias/documentação desnecessária 
    excluir.extend([
        "guia_amostras_elevenlabs.md",
        "guia_extracao_amostras_audacity.md",
        "guia_melhorias_baseado_nos_videos.md",
        "guia_perfil_misto.md", 
        "guia_testes_offline.md",
        "guia_uso_samples_curtos.md",
        "guia_uso_samples_elevenlabs.md",
        "guia_gravacao_samples.md"
    ])
    
    # READMEs redundantes
    excluir.extend([
        "README_final.md",
        "README_heygen.md", 
        "README_reference.md",
        "README_updated.md",
        "README_video.md"
    ])
    
    # Relatórios antigos
    excluir.extend([
        "elevenlabs_voices_report.json",
        "documentacao_funcionalidades_melhorias.md",
        "RESUMO_CONFIGURACOES.md",
        "PONTO_RESTAURACAO_v1.0.md"
    ])
    
    # Diretórios antigos/vazios
    excluir.extend([
        "old_tests/",
        "reference/", 
        "data/",
        "cache/",
        "scripts/"
    ])
    
    return essenciais, excluir

def limpar_projeto_seguro():
    """Executa limpeza segura do projeto"""
    
    print("🧹 LIMPEZA SEGURA DO PROJETO CloneIA")
    print("=" * 50)
    
    essenciais, excluir = analisar_projeto()
    
    # Mostrar o que será excluído
    print("📋 ARQUIVOS/PASTAS PARA EXCLUSÃO:")
    arquivos_encontrados = []
    tamanho_total = 0
    
    for item in excluir:
        if os.path.exists(item):
            arquivos_encontrados.append(item)
            if os.path.isfile(item):
                tamanho = os.path.getsize(item)
                tamanho_total += tamanho
                print(f"  📄 {item} ({tamanho/1024:.1f} KB)")
            else:
                print(f"  📁 {item}/")
    
    print(f"\n📊 Total: {len(arquivos_encontrados)} itens (~{tamanho_total/1024/1024:.1f} MB)")
    
    if not arquivos_encontrados:
        print("✅ Projeto já está limpo!")
        return
    
    # Executar automaticamente (já confirmado pelo usuário)
    print("\n✅ Executando limpeza automática (já confirmado)...")
    
    # Executar limpeza
    print("\n🗑️ Executando limpeza...")
    excluidos = 0
    
    for item in arquivos_encontrados:
        try:
            if os.path.isfile(item):
                os.remove(item)
                print(f"  ✅ Excluído: {item}")
                excluidos += 1
            elif os.path.isdir(item):
                shutil.rmtree(item)
                print(f"  ✅ Excluído: {item}/")
                excluidos += 1
        except Exception as e:
            print(f"  ❌ Erro ao excluir {item}: {str(e)}")
    
    print(f"\n🎉 Limpeza concluída! {excluidos} itens removidos")
    
    # Mostrar estrutura final essencial
    print("\n📁 ESTRUTURA FINAL ESSENCIAL:")
    print("📁 CloneIA/")
    print("  ├── 📁 core/           # Sistema principal")
    print("  ├── 📁 config/         # Configurações")
    print("  ├── 📁 clean_project/  # Versão otimizada")
    print("  ├── 📁 output/         # Resultados gerados")
    print("  ├── 📁 venv/           # Ambiente Python")
    print("  ├── 📄 requirements.txt")
    print("  ├── 📄 generate_reel_correto.py  # Script principal")
    print("  ├── 📄 gerar_videos_reel.py     # Geração de vídeos")
    print("  ├── 📄 juntar_videos_reel.py    # Junção final")
    print("  └── 📄 README.md")

def verificar_funcionamento():
    """Verifica se o projeto ainda funciona após limpeza"""
    
    print("\n🔍 VERIFICANDO FUNCIONAMENTO...")
    
    # Verificar arquivos essenciais
    essenciais_core = [
        "core/__init__.py",
        "core/audio.py", 
        "core/video.py",
        "core/text.py",
        "core/utils.py",
        "config/voice_config.json",
        "config/avatar_config.json"
    ]
    
    tudo_ok = True
    
    for arquivo in essenciais_core:
        if os.path.exists(arquivo):
            print(f"  ✅ {arquivo}")
        else:
            print(f"  ❌ {arquivo} - FALTANDO!")
            tudo_ok = False
    
    if tudo_ok:
        print("✅ Projeto funcional - todos os arquivos essenciais presentes")
    else:
        print("❌ ATENÇÃO: Alguns arquivos essenciais estão faltando!")

if __name__ == "__main__":
    limpar_projeto_seguro()
    verificar_funcionamento()