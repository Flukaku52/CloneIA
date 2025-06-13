#!/usr/bin/env python3
"""
Instruções otimizadas para HeyGen Web Interface
"""

from pathlib import Path

def mostrar_instrucoes_otimizadas():
    """Mostra instruções super otimizadas para HeyGen"""
    
    project_root = Path(__file__).parent.resolve()
    audio_dir = project_root / "output" / "reel_renato_melhorado" / "segments"
    
    print("🚀 HEYGEN WEB - MODO TURBO!")
    print("=" * 60)
    print("✅ Sua conta tem 360 créditos API disponíveis")
    print("🎯 Avatar: 3034bbd37f2540ddb70c90c7f67b4f5c")
    print("📱 Formato: 9:16 Portrait")
    print()
    
    print("⚡ PROCESSO RÁPIDO:")
    print("1. https://app.heygen.com")
    print("2. Create Video → Avatar")
    print("3. Upload de áudio (drag & drop)")
    print("4. Selecionar avatar")
    print("5. Configure 9:16 → Generate")
    print("6. Repeat para os 5 áudios")
    print()
    
    print("📂 ÁUDIOS PARA UPLOAD (na ordem):")
    audio_files = [
        ("01_abertura_audio.mp3", "Abertura", "20s"),
        ("02_connecticut_vs_estados_pro-cripto_audio.mp3", "Connecticut", "257s"), 
        ("03_brasileiros_investindo_em_cripto_audio.mp3", "Brasileiros", "286s"),
        ("04_bitcoin_30_dias_acima_de_100k_audio.mp3", "Bitcoin", "213s"),
        ("05_fechamento_audio.mp3", "Fechamento", "64s")
    ]
    
    for i, (arquivo, nome, duracao) in enumerate(audio_files, 1):
        audio_path = audio_dir / arquivo
        if audio_path.exists():
            print(f"   [{i}] {nome} ({duracao})")
            print(f"       📁 {audio_path}")
            print(f"       🤖 Avatar: 3034bbd37f2540ddb70c90c7f67b4f5c")
            print(f"       📐 Formato: 9:16 Portrait")
            print()
    
    print("🎬 EDIÇÃO FINAL:")
    print("• Software: CapCut, Premiere, DaVinci")
    print("• Ordem: Abertura → Connecticut → Brasileiros → Bitcoin → Fechamento")  
    print("• Cortes: SECOS (sem transições)")
    print("• Duração final: ~2-3 minutos")
    print()
    
    print("💡 DICAS PRO:")
    print("• Faça todos os uploads de uma vez")
    print("• Use batch processing se disponível")
    print("• Background escuro (#000000)")
    print("• Teste um áudio primeiro se quiser")
    print()
    
    print("⏱️ TEMPO ESTIMADO:")
    print("• Upload + Generate: ~5-10 min por vídeo")
    print("• Total para 5 vídeos: ~30-50 minutos")
    print("• Edição final: ~15-30 minutos")
    print()
    
    print("🎯 RESULTADO FINAL:")
    print("• Reel com timing perfeito")
    print("• Abertura natural: 'E aí cambada! Olha eu aí de novo'")
    print("• Fechamento com pausas rítmicas")
    print("• Qualidade profissional")
    print()
    
    print("🚀 BORA! SUA CONTA ESTÁ PRONTA!")

if __name__ == "__main__":
    mostrar_instrucoes_otimizadas()