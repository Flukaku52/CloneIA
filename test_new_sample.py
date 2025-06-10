#!/usr/bin/env python3
"""
Script para testar cada novo sample individual conforme for gravado
Fornece feedback imediato sobre qualidade e teste de voz
"""

import os
import sys
import json
import subprocess
import tempfile
import wave
import numpy as np
from pathlib import Path
from datetime import datetime
import argparse

# Adiciona o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

from core.audio import AudioGenerator
from core.utils import load_voice_config

def extract_audio_from_video(video_path: str, output_path: str) -> bool:
    """Extrai áudio de vídeo"""
    try:
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vn', '-acodec', 'pcm_s16le',
            '-ar', '16000', '-ac', '1',
            output_path, '-y'
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except Exception as e:
        print(f"❌ Erro ao extrair áudio: {e}")
        return False

def analyze_sample_quality(audio_path: str) -> dict:
    """Analisa qualidade do sample"""
    try:
        with wave.open(audio_path, 'rb') as wav_file:
            frames = wav_file.readframes(-1)
            sound_info = np.frombuffer(frames, dtype=np.int16)
            frame_rate = wav_file.getframerate()
            duration = len(sound_info) / frame_rate
            
            if np.max(np.abs(sound_info)) > 0:
                sound_normalized = sound_info / np.max(np.abs(sound_info))
            else:
                return {}
            
            # Métricas de qualidade
            signal_to_noise = np.mean(np.abs(sound_normalized)) / (np.std(sound_normalized) + 1e-8)
            silence_threshold = 0.05
            silences = np.abs(sound_normalized) < silence_threshold
            silence_ratio = np.sum(silences) / len(silences)
            
            # Ruído de fundo
            start_noise = np.std(sound_normalized[:int(frame_rate * 0.5)]) if len(sound_normalized) > frame_rate else 0
            end_noise = np.std(sound_normalized[-int(frame_rate * 0.5):]) if len(sound_normalized) > frame_rate else 0
            background_noise = (start_noise + end_noise) / 2
            
            # Clipping
            clipping_ratio = np.sum(np.abs(sound_normalized) > 0.95) / len(sound_normalized)
            
            # Variação dinâmica
            tonal_variety = np.std(np.diff(sound_normalized))
            
            return {
                'duration': duration,
                'signal_to_noise': float(signal_to_noise),
                'silence_ratio': float(silence_ratio),
                'background_noise': float(background_noise),
                'clipping_ratio': float(clipping_ratio),
                'tonal_variety': float(tonal_variety)
            }
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        return {}

def evaluate_sample(analysis: dict) -> dict:
    """Avalia se o sample é adequado para ML"""
    if not analysis:
        return {'approved': False, 'score': 0, 'feedback': ['Falha na análise']}
    
    score = 0
    feedback = []
    issues = []
    
    # Duração (8-30 segundos ideal)
    duration = analysis['duration']
    if 8 <= duration <= 30:
        score += 30
        feedback.append(f"✅ Duração perfeita: {duration:.1f}s")
    elif 5 <= duration <= 40:
        score += 20
        feedback.append(f"📏 Duração aceitável: {duration:.1f}s")
    elif duration < 5:
        score -= 20
        issues.append(f"❌ Muito curto: {duration:.1f}s (mínimo 8s)")
    else:
        score -= 10
        issues.append(f"⚠️ Muito longo: {duration:.1f}s (máximo 30s)")
    
    # Relação sinal/ruído
    snr = analysis['signal_to_noise']
    if snr > 4:
        score += 25
        feedback.append(f"✅ Áudio limpo: S/N = {snr:.2f}")
    elif snr > 2:
        score += 15
        feedback.append(f"📊 Áudio bom: S/N = {snr:.2f}")
    else:
        score -= 15
        issues.append(f"❌ Áudio com ruído: S/N = {snr:.2f} (mínimo 2.0)")
    
    # Taxa de silêncio
    silence = analysis['silence_ratio']
    if 0.05 <= silence <= 0.25:
        score += 20
        feedback.append(f"✅ Fala contínua ideal: {silence:.2f} silêncio")
    elif silence <= 0.35:
        score += 10
        feedback.append(f"📊 Boa continuidade: {silence:.2f} silêncio")
    else:
        score -= 15
        issues.append(f"❌ Muito silêncio: {silence:.2f} (máximo 0.25)")
    
    # Ruído de fundo
    noise = analysis['background_noise']
    if noise < 0.02:
        score += 15
        feedback.append("✅ Sem ruído de fundo")
    elif noise < 0.05:
        score += 10
        feedback.append("📊 Pouco ruído de fundo")
    else:
        score -= 10
        issues.append(f"❌ Ruído de fundo detectado: {noise:.3f}")
    
    # Distorção/Clipping
    clipping = analysis['clipping_ratio']
    if clipping < 0.01:
        score += 10
        feedback.append("✅ Sem distorção")
    else:
        score -= 20
        issues.append(f"❌ Distorção detectada: {clipping:.3f}")
    
    # Variação tonal
    variety = analysis['tonal_variety']
    if variety > 0.02:
        score += 10
        feedback.append(f"✅ Boa expressividade: {variety:.3f}")
    else:
        issues.append(f"⚠️ Pouca variação tonal: {variety:.3f}")
    
    # Classificação final
    approved = score >= 60
    
    return {
        'approved': approved,
        'score': max(0, score),
        'feedback': feedback,
        'issues': issues,
        'recommendation': 'APROVADO para ML!' if approved else 'REGRAVE com melhorias'
    }

def test_sample_voice_generation(sample_path: str, test_text: str = None) -> str:
    """Testa geração de voz com o novo sample"""
    if not test_text:
        test_text = "Fala cambada! Tô testando esse novo sample aqui pra ver como ficou a voz."
    
    print(f"\n🎤 Testando geração de voz com o sample...")
    
    # Carrega configuração otimizada
    voice_config = load_voice_config("cambada_optimized")
    if not voice_config:
        voice_config = load_voice_config("ml_optimized")
    if not voice_config:
        voice_config = load_voice_config()
    
    # Inicializa gerador
    audio_gen = AudioGenerator()
    
    # Gera timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"output/audio/teste_sample_{timestamp}.mp3"
    
    try:
        audio_path = audio_gen.generate_audio(test_text, output_path)
        if audio_path and os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path) / 1024
            print(f"✅ Áudio de teste gerado: {audio_path}")
            print(f"📊 Tamanho: {file_size:.1f} KB")
            return audio_path
        else:
            print("❌ Falha na geração de áudio")
            return ""
    except Exception as e:
        print(f"❌ Erro: {e}")
        return ""

def save_sample_report(sample_path: str, analysis: dict, evaluation: dict) -> str:
    """Salva relatório do sample"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"sample_reports/report_{timestamp}.json"
    
    os.makedirs("sample_reports", exist_ok=True)
    
    report = {
        'timestamp': timestamp,
        'sample_path': sample_path,
        'analysis': analysis,
        'evaluation': evaluation,
        'approved': evaluation['approved']
    }
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report_path

def main():
    parser = argparse.ArgumentParser(description='Testa novo sample de voz')
    parser.add_argument('sample_path', help='Caminho para o arquivo de áudio/vídeo')
    parser.add_argument('--text', help='Texto personalizado para teste de voz')
    parser.add_argument('--no-voice-test', action='store_true', help='Pula teste de geração de voz')
    
    args = parser.parse_args()
    
    sample_path = Path(args.sample_path)
    if not sample_path.exists():
        print(f"❌ Arquivo não encontrado: {sample_path}")
        return
    
    print("🎙️ TESTE DE NOVO SAMPLE")
    print("=" * 50)
    print(f"📁 Arquivo: {sample_path.name}")
    
    # Extrai áudio se for vídeo
    temp_dir = tempfile.mkdtemp()
    if sample_path.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv']:
        print("🎬 Extraindo áudio do vídeo...")
        audio_path = os.path.join(temp_dir, "sample_audio.wav")
        if not extract_audio_from_video(str(sample_path), audio_path):
            print("❌ Falha na extração de áudio")
            return
    elif sample_path.suffix.lower() in ['.wav', '.mp3', '.m4a', '.opus', '.ogg', '.flac', '.aifc', '.aiff']:
        # Converte para WAV se necessário
        audio_path = os.path.join(temp_dir, "sample_audio.wav")
        try:
            cmd = ['ffmpeg', '-i', str(sample_path), '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', audio_path, '-y']
            subprocess.run(cmd, capture_output=True, check=True)
        except Exception as e:
            print(f"❌ Falha na conversão de áudio: {e}")
            return
    else:
        print("❌ Formato não suportado. Use: mp4, mov, avi, mkv, wav, mp3, m4a, opus, ogg, flac, aifc, aiff")
        return
    
    # Analisa qualidade
    print("\n🔍 Analisando qualidade do sample...")
    analysis = analyze_sample_quality(audio_path)
    
    if not analysis:
        print("❌ Falha na análise")
        return
    
    # Avalia sample
    evaluation = evaluate_sample(analysis)
    
    # Mostra resultados
    print(f"\n📊 RESULTADO DA ANÁLISE")
    print("=" * 50)
    print(f"🎯 Score: {evaluation['score']}/100")
    print(f"📋 Status: {evaluation['recommendation']}")
    
    if evaluation['feedback']:
        print(f"\n✅ Pontos Positivos:")
        for feedback in evaluation['feedback']:
            print(f"   {feedback}")
    
    if evaluation['issues']:
        print(f"\n⚠️ Problemas Encontrados:")
        for issue in evaluation['issues']:
            print(f"   {issue}")
    
    # Teste de voz (se aprovado e solicitado)
    if evaluation['approved'] and not args.no_voice_test:
        print(f"\n🎵 TESTE DE GERAÇÃO DE VOZ")
        print("=" * 50)
        test_audio = test_sample_voice_generation(str(sample_path), args.text)
        if test_audio:
            print(f"🎧 Escute o resultado e compare com sua voz original!")
    elif not evaluation['approved']:
        print(f"\n💡 RECOMENDAÇÕES PARA MELHORAR:")
        print("   • Grave em ambiente mais silencioso")
        print("   • Mantenha distância consistente do microfone")
        print("   • Fale de forma contínua, evite pausas longas")
        print("   • Duração ideal: 10-25 segundos")
        print("   • Regrave até conseguir score 60+")
    
    # Salva relatório
    report_path = save_sample_report(str(sample_path), analysis, evaluation)
    print(f"\n📄 Relatório salvo em: {report_path}")
    
    if evaluation['approved']:
        print(f"\n🎉 SAMPLE APROVADO! Pode usar para treinar o modelo.")
    else:
        print(f"\n🔄 Regrave seguindo as recomendações acima.")

if __name__ == "__main__":
    main()