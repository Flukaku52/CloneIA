#!/usr/bin/env python3
"""
Gerador de Reel com roteiro correto e voz 9.7/10
Inclui cortes entre cada notícia
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Adiciona o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

from core.audio import AudioGenerator
from core.utils import load_heygen_api_key, ensure_directory

# Script do reel dividido por segmentos
REEL_SEGMENTS = [
    {
        "id": "intro",
        "title": "Abertura",
        "text": "E aí cambada! Já tô de volta por aqui e bora pras notícias."
    },
    {
        "id": "noticia1",
        "title": "Empresas e Bitcoin", 
        "text": """Empresas já têm mais de 3% do supply de BTC.

Seguinte: segundo o banco Standard Chartered, 61 empresas que têm ações em bolsa já acumulam 3,2% de todo o Bitcoin que vai existir no mundo.

Entre elas estão MicroStrategy, Tesla e outras gigantes que tão comprando BTC pra colocar em caixa, como reserva de valor.

Em vez de só dólar ou ouro, agora tem empresa diversificando com Bitcoin.
Isso reforça que o BTC não é mais só papo de investidor de rede social — tá virando um ativo institucional."""
    },
    {
        "id": "noticia2",
        "title": "Blockchain no Brasil",
        "text": """Blockchain pode modernizar abertura de empresas no Brasil.

Agora uma que pouca gente tá falando:
Tem projeto de lei no Congresso propondo que a gente use blockchain nos registros de abertura de empresas.

A ideia é garantir que os dados fiquem imutáveis e rastreáveis.
Menos chance de fraude, mais transparência, e processos mais rápidos.

Hoje abrir empresa no Brasil ainda tem muita burocracia e sistema velho.
Se isso andar, seria um baita uso prático de blockchain — além do mercado cripto — que realmente impacta a vida de quem empreende."""
    },
    {
        "id": "noticia3",
        "title": "Drex na Amazônia",
        "text": """Drex chega à Amazônia.

Agora presta atenção nessa aqui:
A Caixa Econômica Federal tá testando o Drex, o real digital, em comunidades da Amazônia que não têm nem internet.

A tecnologia permite que o morador faça pagamentos off-line, e quando o celular se conecta à rede, tudo é sincronizado.

É um avanço grande pra inclusão financeira — levar pagamento digital pra quem hoje tá fora do sistema.

Mas... a gente também tem que olhar pro outro lado dessa moeda.
Diferente do dinheiro físico — que você gasta sem deixar rastro — o Drex é uma moeda totalmente rastreável e programável.

Na prática, isso significa que o governo poderia, tecnicamente, monitorar e até controlar como você gasta seu dinheiro.

Então assim:
Tecnologia boa? Sim.
Mas liberdade financeira precisa estar no centro dessa conversa.
A gente tem que ficar muito atento pra isso não virar ferramenta de controle."""
    },
    {
        "id": "encerramento",
        "title": "Fechamento",
        "text": """Por hoje é isso, cambada.

Sigo de olho. Até a próxima!"""
    }
]

class ReelCorretoGenerator:
    def __init__(self):
        self.audio_gen = AudioGenerator()
        self.heygen_api_key = load_heygen_api_key()
        self.output_dir = "output/reel_correto"
        ensure_directory(self.output_dir)
        ensure_directory(f"{self.output_dir}/segments")
        
        # Avatar HeyGen
        self.avatar_id = "bd9548bed4984738a93b0db0c6c3edc9"  # flukakudabet
        
    def generate_audio_segment(self, segment: dict) -> str:
        """Gera áudio para um segmento"""
        print(f"\n🎤 Gerando áudio: {segment['title']}")
        print(f"   📝 Preview: {segment['text'][:50]}...")
        
        audio_path = f"{self.output_dir}/segments/{segment['id']}_audio.mp3"
        result = self.audio_gen.generate_audio(
            segment['text'],
            audio_path,
            optimize=False  # Não otimizar para manter o texto natural
        )
        
        if result:
            # Calcula duração aproximada
            file_size = os.path.getsize(result) / 1024  # KB
            duration_estimate = file_size / 16  # Aproximadamente 16KB por segundo
            print(f"   ✅ Áudio gerado: {os.path.basename(result)}")
            print(f"   ⏱️ Duração estimada: {duration_estimate:.1f}s")
            return result
        else:
            print(f"   ❌ Erro ao gerar áudio")
            return None
    
    def generate_full_reel(self):
        """Gera o reel completo"""
        print("🎥 GERANDO REEL CORRETO")
        print("=" * 55)
        print(f"🎯 Perfil de voz: 9.7/10 (Novo Voice ID)")
        print(f"🤖 Avatar HeyGen: {self.avatar_id}")
        print(f"✂️ Cortes entre notícias: SIM")
        print(f"📊 Segmentos: {len(REEL_SEGMENTS)}")
        
        audio_paths = []
        total_duration = 0
        
        # 1. Gera áudios para todos os segmentos
        print("\n📊 FASE 1: Gerando áudios com perfil 9.7/10")
        for i, segment in enumerate(REEL_SEGMENTS, 1):
            print(f"\n[{i}/{len(REEL_SEGMENTS)}]", end="")
            audio_path = self.generate_audio_segment(segment)
            if audio_path:
                audio_paths.append({
                    'id': segment['id'],
                    'title': segment['title'],
                    'path': audio_path
                })
            else:
                print(f"❌ Falha no segmento {segment['id']}")
                return
        
        # 2. Estrutura de cortes
        print("\n\n📊 FASE 2: Estrutura de cortes")
        print("   ✂️ PONTOS DE CORTE:")
        for i in range(len(REEL_SEGMENTS) - 1):
            current = REEL_SEGMENTS[i]['title']
            next_seg = REEL_SEGMENTS[i+1]['title']
            print(f"      [{i+1}] {current} → 🔪 CORTE → {next_seg}")
        
        # 3. Instruções para HeyGen
        print(f"\n📊 FASE 3: Instruções para HeyGen")
        print(f"\n📋 PASSO A PASSO:")
        print(f"   1️⃣ Acesse HeyGen.com")
        print(f"   2️⃣ Para cada áudio abaixo:")
        print(f"      • Faça upload do áudio")
        print(f"      • Selecione avatar: {self.avatar_id}")
        print(f"      • Gere o vídeo")
        print(f"   3️⃣ Baixe cada vídeo gerado")
        
        print(f"\n📁 ÁUDIOS PARA HEYGEN:")
        for i, audio in enumerate(audio_paths, 1):
            print(f"   {i}. {audio['title']}")
            print(f"      📂 {audio['path']}")
        
        # 4. Instruções de edição
        print(f"\n✂️ EDIÇÃO FINAL:")
        print(f"   • Software recomendado: CapCut, Premiere, DaVinci")
        print(f"   • Tipo de corte: CORTE SECO (sem transição)")
        print(f"   • Ordem dos vídeos:")
        for i, segment in enumerate(REEL_SEGMENTS, 1):
            print(f"      {i}. {segment['title']}")
        
        # 5. Resumo
        print(f"\n📊 RESUMO FINAL:")
        print(f"   • Total de segmentos: {len(audio_paths)}")
        print(f"   • Qualidade de voz: 9.7/10")
        print(f"   • Estrutura: Abertura → 3 Notícias → Fechamento")
        print(f"   • Tempo estimado: 2-3 minutos")
        print(f"\n✅ Áudios prontos para processamento no HeyGen!")
        
        # 6. Criar arquivo de instruções
        instructions_path = f"{self.output_dir}/INSTRUCOES_EDICAO.txt"
        with open(instructions_path, 'w', encoding='utf-8') as f:
            f.write("INSTRUÇÕES DE EDIÇÃO DO REEL\n")
            f.write("============================\n\n")
            f.write("ORDEM DOS SEGMENTOS:\n")
            for i, segment in enumerate(REEL_SEGMENTS, 1):
                f.write(f"{i}. {segment['title']} ({segment['id']}_audio.mp3)\n")
            f.write("\nCORTES:\n")
            f.write("- Use CORTE SECO entre cada segmento\n")
            f.write("- Sem transições ou fades\n")
            f.write(f"\nAVATAR HEYGEN: {self.avatar_id}\n")
        
        print(f"\n📄 Instruções salvas em: {instructions_path}")

def main():
    generator = ReelCorretoGenerator()
    generator.generate_full_reel()

if __name__ == "__main__":
    main()