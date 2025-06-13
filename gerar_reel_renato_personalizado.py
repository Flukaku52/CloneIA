#!/usr/bin/env python3
"""
Gera reel com o roteiro personalizado do Renato usando as configurações que funcionaram
"""

import os
import sys
import time
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

from core.audio import AudioGenerator
import logging

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def gerar_reel_personalizado():
    """Gera reel com roteiro personalizado do Renato"""
    
    # Roteiro personalizado
    roteiro_completo = """E aí cambada! Olha eu de volta aí e bora pras novas!

O estado de Connecticut aprovou uma lei que impede o governo estadual e prefeituras de comprar, manter ou investir em criptomoedas. E também veta o uso de cripto como forma de pagamento em serviço público.

Enquanto isso, estados como Texas, Wyoming e Colorado estão liberando o uso de cripto e blockchain no setor público.

O argumento oficial é proteger o contribuinte da volatilidade. Mas quando o governo corre pra proibir um tipo de dinheiro, é porque ele não quer perder o controle sobre como você transaciona.

Curioso: para o Drex, por exemplo, ninguém reclama. Mas pra uma moeda descentralizada que você controla? Aí já vira perigo.

Olha esse dado que pouca gente sabe: quinze por cento dos brasileiros já investiram em criptomoedas. Pra você ter uma ideia, isso é mais do que: quatorze por cento que investem em dólar, doze por cento em renda fixa, nove por cento em ouro, e só seis por cento em ações.

Ou seja: cripto já tá mais presente na carteira do brasileiro médio do que boa parte dos investimentos tradicionais.

Só a boa e velha poupança ainda lidera, com cinquenta e dois por cento. Mas a tendência é clara: cada vez mais gente tá buscando alternativas fora do sistema financeiro tradicional.

E isso, querendo ou não, é um movimento que combina muito com a proposta das criptos: dar mais autonomia pro cidadão sobre o próprio dinheiro.

E agora falando de preço, o Bitcoin passou trinta dias seguidos acima de cem mil dólares. Algo inédito no mercado. Mesmo essa semana ele tendo sofrido uma queda e assustado muita gente, ele se segurou bem ali nos cem mil e já recuperou quase tudo voltando pros cento e dez.

Isso mostra que não é só hype de gráfico. O BTC já tem consistência pra se manter em patamares altos, apontando pra maturidade e confiança.

Enquanto governos tentam segurar ou proibir, o mercado segue validando uma moeda que não depende de bancos centrais.

Por hoje é isso, cambada. Governos tentando segurar a revolução, brasileiros investindo além do tradicional, e o Bitcoin mostrando que existe. E que veio pra ficar.

Sigo de olho."""

    # Divide em segmentos para o HeyGen
    segmentos = [
        {
            "nome": "Abertura",
            "texto": "E aí cambada! Olha eu de volta aí e bora pras novas!"
        },
        {
            "nome": "Connecticut vs Estados Pro-Cripto",
            "texto": """O estado de Connecticut aprovou uma lei que impede o governo estadual e prefeituras de comprar, manter ou investir em criptomoedas. E também veta o uso de cripto como forma de pagamento em serviço público.

Enquanto isso, estados como Texas, Wyoming e Colorado estão liberando o uso de cripto e blockchain no setor público.

O argumento oficial é proteger o contribuinte da volatilidade. Mas quando o governo corre pra proibir um tipo de dinheiro, é porque ele não quer perder o controle sobre como você transaciona.

Curioso: para o Drex, por exemplo, ninguém reclama. Mas pra uma moeda descentralizada que você controla? Aí já vira perigo."""
        },
        {
            "nome": "Brasileiros Investindo em Cripto",
            "texto": """Olha esse dado que pouca gente sabe: quinze por cento dos brasileiros já investiram em criptomoedas. Pra você ter uma ideia, isso é mais do que: quatorze por cento que investem em dólar, doze por cento em renda fixa, nove por cento em ouro, e só seis por cento em ações.

Ou seja: cripto já tá mais presente na carteira do brasileiro médio do que boa parte dos investimentos tradicionais.

Só a boa e velha poupança ainda lidera, com cinquenta e dois por cento. Mas a tendência é clara: cada vez mais gente tá buscando alternativas fora do sistema financeiro tradicional.

E isso, querendo ou não, é um movimento que combina muito com a proposta das criptos: dar mais autonomia pro cidadão sobre o próprio dinheiro."""
        },
        {
            "nome": "Bitcoin 30 Dias Acima de 100k",
            "texto": """E agora falando de preço, o Bitcoin passou trinta dias seguidos acima de cem mil dólares. Algo inédito no mercado. Mesmo essa semana ele tendo sofrido uma queda e assustado muita gente, ele se segurou bem ali nos cem mil e já recuperou quase tudo voltando pros cento e dez.

Isso mostra que não é só hype de gráfico. O BTC já tem consistência pra se manter em patamares altos, apontando pra maturidade e confiança.

Enquanto governos tentam segurar ou proibir, o mercado segue validando uma moeda que não depende de bancos centrais."""
        },
        {
            "nome": "Fechamento",
            "texto": """Por hoje é isso, cambada. Governos tentando segurar a revolução, brasileiros investindo além do tradicional, e o Bitcoin mostrando que existe. E que veio pra ficar.

Sigo de olho."""
        }
    ]

    print("🎥 GERANDO REEL PERSONALIZADO DO RENATO")
    print("=" * 60)
    print("🎯 Perfil de voz: FlukakuFluido (25NR0sM9ehsgXaoknsxO)")
    print("🤖 Avatar HeyGen: bd9548bed4984738a93b0db0c6c3edc9")
    print("✂️ Cortes entre segmentos: SIM")
    print(f"📊 Segmentos: {len(segmentos)}")
    
    # Inicializa o gerador de áudio
    audio_gen = AudioGenerator()
    
    # Diretório de saída
    output_dir = project_root / "output" / "reel_renato_personalizado" / "segments"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n📊 FASE 1: Gerando áudios personalizados")
    print()
    
    audio_files = []
    total_duration = 0
    
    for i, segmento in enumerate(segmentos, 1):
        print(f"[{i}/{len(segmentos)}]")
        print(f"🎤 Gerando áudio: {segmento['nome']}")
        
        # Preview do texto
        preview = segmento['texto'][:50] + "..." if len(segmento['texto']) > 50 else segmento['texto']
        print(f"   📝 Preview: {preview}")
        
        # Nome do arquivo
        filename = f"{i:02d}_{segmento['nome'].lower().replace(' ', '_')}_audio.mp3"
        audio_path = output_dir / filename
        
        # Gera áudio
        success = audio_gen.generate_audio(segmento['texto'], str(audio_path))
        
        if success:
            print(f"   ✅ Áudio gerado: {filename}")
            
            # Estima duração
            chars = len(segmento['texto'])
            estimated_duration = chars / 150 * 60  # ~150 chars por minuto
            total_duration += estimated_duration
            print(f"   ⏱️ Duração estimada: {estimated_duration:.1f}s")
            
            audio_files.append({
                'nome': segmento['nome'],
                'arquivo': filename,
                'path': str(audio_path),
                'duracao': estimated_duration
            })
        else:
            print(f"   ❌ Erro ao gerar áudio para: {segmento['nome']}")
            return False
        
        print()
    
    print("📊 FASE 2: Estrutura de cortes")
    print("   ✂️ PONTOS DE CORTE:")
    for i in range(len(audio_files) - 1):
        print(f"      [{i+1}] {audio_files[i]['nome']} → 🔪 CORTE → {audio_files[i+1]['nome']}")
    
    print("\n📊 FASE 3: Instruções para HeyGen")
    print()
    print("📋 PASSO A PASSO:")
    print("   1️⃣ Acesse HeyGen.com")
    print("   2️⃣ Para cada áudio abaixo:")
    print("      • Faça upload do áudio")
    print("      • Selecione avatar: bd9548bed4984738a93b0db0c6c3edc9")
    print("      • Configure formato 9:16 (Portrait)")
    print("      • Gere o vídeo")
    print("   3️⃣ Baixe cada vídeo gerado")
    
    print("\n📁 ÁUDIOS PARA HEYGEN:")
    for i, audio in enumerate(audio_files, 1):
        print(f"   {i}. {audio['nome']}")
        print(f"      📂 {audio['path']}")
    
    print("\n✂️ EDIÇÃO FINAL:")
    print("   • Software recomendado: CapCut, Premiere, DaVinci")
    print("   • Tipo de corte: CORTE SECO (sem transição)")
    print("   • Ordem dos vídeos:")
    for i, audio in enumerate(audio_files, 1):
        print(f"      {i}. {audio['nome']}")
    
    print(f"\n📊 RESUMO FINAL:")
    print(f"   • Total de segmentos: {len(audio_files)}")
    print(f"   • Qualidade de voz: FlukakuFluido")
    print(f"   • Estrutura: Abertura → 3 Tópicos → Fechamento")
    print(f"   • Tempo estimado: {total_duration/60:.1f} minutos")
    
    print("\n✅ Áudios do roteiro personalizado prontos para HeyGen!")
    
    # Salva instruções
    instrucoes_path = project_root / "output" / "reel_renato_personalizado" / "INSTRUCOES_HEYGEN.txt"
    with open(instrucoes_path, 'w', encoding='utf-8') as f:
        f.write("INSTRUÇÕES PARA GERAR VÍDEO NO HEYGEN - ROTEIRO PERSONALIZADO RENATO\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Avatar: bd9548bed4984738a93b0db0c6c3edc9\n")
        f.write(f"Formato: 9:16 (Portrait)\n")
        f.write(f"Total de segmentos: {len(audio_files)}\n\n")
        f.write("ARQUIVOS DE ÁUDIO:\n")
        for i, audio in enumerate(audio_files, 1):
            f.write(f"{i}. {audio['nome']}\n")
            f.write(f"   Arquivo: {audio['path']}\n")
            f.write(f"   Duração: {audio['duracao']:.1f}s\n\n")
        f.write("PASSOS:\n")
        f.write("1. Acesse https://app.heygen.com\n")
        f.write("2. Para cada áudio:\n")
        f.write("   - Create Video → Upload Audio\n")
        f.write("   - Selecione avatar: bd9548bed4984738a93b0db0c6c3edc9\n")
        f.write("   - Configure 9:16 (Portrait)\n")
        f.write("   - Generate\n")
        f.write("3. Baixe todos os vídeos\n")
        f.write("4. Edite juntando com cortes secos\n")
    
    print(f"📄 Instruções salvas em: {instrucoes_path}")
    
    return True

if __name__ == "__main__":
    success = gerar_reel_personalizado()
    sys.exit(0 if success else 1)