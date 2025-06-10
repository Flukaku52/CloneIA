#!/usr/bin/env python3
"""
Script para analisar e comparar especificamente os "Fala cambada" 
dos vídeos originais com o áudio gerado
"""

import os
import sys
import json
import subprocess
import tempfile
import wave
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Adiciona o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

def extract_audio_segment(video_path: str, start_time: float, duration: float, output_path: str) -> bool:
    """
    Extrai um segmento específico de áudio de um vídeo
    """
    try:
        cmd = [
            'ffmpeg', '-i', video_path,
            '-ss', str(start_time),
            '-t', str(duration),
            '-vn', '-acodec', 'pcm_s16le',
            '-ar', '16000', '-ac', '1',
            output_path, '-y'
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except Exception as e:
        print(f"❌ Erro ao extrair segmento: {e}")
        return False

def analyze_audio_prosody(audio_path: str) -> Dict[str, float]:
    """
    Analisa características prosódicas detalhadas do áudio
    """
    try:
        with wave.open(audio_path, 'rb') as wav_file:
            frames = wav_file.readframes(-1)
            sound_info = np.frombuffer(frames, dtype=np.int16)
            frame_rate = wav_file.getframerate()
            duration = len(sound_info) / frame_rate
            
            # Normaliza o áudio
            sound_normalized = sound_info / np.max(np.abs(sound_info))
            
            # Calcula energia
            energy = np.sum(sound_normalized ** 2) / len(sound_normalized)
            
            # Calcula taxa de variação (ritmo)
            diff = np.diff(np.abs(sound_normalized))
            rhythm_rate = np.std(diff)
            
            # Detecta picos (entusiasmo)
            peaks = np.where(np.abs(sound_normalized) > 0.8)[0]
            peak_density = len(peaks) / len(sound_normalized)
            
            # Calcula tempo de ataque inicial (quão rápido começa)
            attack_frames = 0
            for i, sample in enumerate(np.abs(sound_normalized)):
                if sample > 0.5:
                    attack_frames = i
                    break
            attack_time = attack_frames / frame_rate
            
            # Velocidade de fala (baseada em cruzamentos por zero)
            zero_crossings = np.where(np.diff(np.sign(sound_normalized)))[0]
            speech_rate = len(zero_crossings) / duration
            
            return {
                'duration': duration,
                'energy': float(energy),
                'rhythm_rate': float(rhythm_rate),
                'peak_density': float(peak_density),
                'attack_time': float(attack_time),
                'speech_rate': float(speech_rate),
                'mean_amplitude': float(np.mean(np.abs(sound_normalized))),
                'max_amplitude': float(np.max(np.abs(sound_normalized)))
            }
    except Exception as e:
        print(f"❌ Erro ao analisar prosódia: {e}")
        return {}

def find_fala_cambada_videos() -> List[str]:
    """
    Identifica quais vídeos provavelmente contêm "Fala cambada"
    """
    videos_dir = Path("reference/videos")
    # Vídeos que provavelmente começam com "Fala cambada" (reels e vídeos curtos)
    priority_patterns = ["reel", "FILE 2025-05-03", "FILE 2025-05-07"]
    
    video_files = []
    for pattern in priority_patterns:
        video_files.extend(videos_dir.glob(f"*{pattern}*.mp4"))
    
    # Remove duplicatas
    return list(set(video_files))

def analyze_original_greetings():
    """
    Analisa as saudações originais dos vídeos
    """
    print("🎬 Analisando saudações originais dos vídeos...")
    
    video_files = find_fala_cambada_videos()
    print(f"📹 Analisando {len(video_files)} vídeos que podem conter 'Fala cambada'")
    
    temp_dir = tempfile.mkdtemp()
    greeting_analyses = []
    
    for i, video_file in enumerate(video_files[:8], 1):  # Analisa primeiros 8
        print(f"\n🎥 Vídeo {i}: {video_file.name}")
        
        # Extrai primeiro 3 segundos (onde geralmente está a saudação)
        temp_audio = os.path.join(temp_dir, f"greeting_{i}.wav")
        if extract_audio_segment(str(video_file), 0, 3.0, temp_audio):
            analysis = analyze_audio_prosody(temp_audio)
            if analysis:
                analysis['video_name'] = video_file.name
                greeting_analyses.append(analysis)
                print(f"   ✅ Análise da saudação:")
                print(f"      - Duração: {analysis['duration']:.2f}s")
                print(f"      - Energia: {analysis['energy']:.3f}")
                print(f"      - Ritmo: {analysis['rhythm_rate']:.3f}")
                print(f"      - Densidade de picos: {analysis['peak_density']:.3f}")
                print(f"      - Tempo de ataque: {analysis['attack_time']:.3f}s")
                print(f"      - Taxa de fala: {analysis['speech_rate']:.0f} Hz")
    
    return greeting_analyses

def analyze_generated_audio(audio_path: str) -> Dict[str, float]:
    """
    Analisa o áudio gerado
    """
    print(f"\n🎧 Analisando áudio gerado: {audio_path}")
    
    # Extrai primeiros 2 segundos (saudação)
    temp_dir = tempfile.mkdtemp()
    temp_audio = os.path.join(temp_dir, "generated_greeting.wav")
    
    # Converte MP3 para WAV
    cmd = [
        'ffmpeg', '-i', audio_path,
        '-ss', '0', '-t', '2',
        '-acodec', 'pcm_s16le',
        '-ar', '16000', '-ac', '1',
        temp_audio, '-y'
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return analyze_audio_prosody(temp_audio)
    except Exception as e:
        print(f"❌ Erro ao analisar áudio gerado: {e}")
        return {}

def compare_and_suggest_improvements(original_analyses: List[Dict], generated_analysis: Dict) -> Dict[str, Any]:
    """
    Compara e sugere melhorias baseadas na diferença
    """
    if not original_analyses or not generated_analysis:
        return {}
    
    # Calcula médias dos originais
    avg_original = {
        'energy': np.mean([a['energy'] for a in original_analyses]),
        'rhythm_rate': np.mean([a['rhythm_rate'] for a in original_analyses]),
        'peak_density': np.mean([a['peak_density'] for a in original_analyses]),
        'attack_time': np.mean([a['attack_time'] for a in original_analyses]),
        'speech_rate': np.mean([a['speech_rate'] for a in original_analyses])
    }
    
    # Calcula diferenças
    differences = {
        'energy_diff': generated_analysis['energy'] - avg_original['energy'],
        'rhythm_diff': generated_analysis['rhythm_rate'] - avg_original['rhythm_rate'],
        'peak_diff': generated_analysis['peak_density'] - avg_original['peak_density'],
        'attack_diff': generated_analysis['attack_time'] - avg_original['attack_time'],
        'speech_rate_diff': generated_analysis['speech_rate'] - avg_original['speech_rate']
    }
    
    # Sugere ajustes
    suggestions = {
        'needs_more_energy': differences['energy_diff'] < -0.1,
        'needs_faster_attack': differences['attack_diff'] > 0.05,
        'needs_more_peaks': differences['peak_diff'] < -0.05,
        'needs_faster_speech': differences['speech_rate_diff'] < -500
    }
    
    return {
        'original_averages': avg_original,
        'generated_values': generated_analysis,
        'differences': differences,
        'suggestions': suggestions
    }

def main():
    print("🎙️ Análise Comparativa: 'Fala Cambada' Original vs Gerado")
    print("=" * 60)
    
    # Analisa saudações originais
    original_analyses = analyze_original_greetings()
    
    # Encontra o áudio gerado mais recente
    audio_dir = Path("output/audio")
    generated_files = list(audio_dir.glob("teste_voz_*.mp3"))
    if generated_files:
        latest_generated = max(generated_files, key=os.path.getmtime)
        print(f"\n📁 Analisando áudio gerado: {latest_generated.name}")
        
        generated_analysis = analyze_generated_audio(str(latest_generated))
        
        if original_analyses and generated_analysis:
            # Compara e sugere
            comparison = compare_and_suggest_improvements(original_analyses, generated_analysis)
            
            print("\n" + "=" * 60)
            print("📊 RESULTADO DA COMPARAÇÃO")
            print("=" * 60)
            
            print("\n🎯 Médias dos 'Fala Cambada' originais:")
            avg = comparison['original_averages']
            print(f"   - Energia: {avg['energy']:.3f}")
            print(f"   - Ritmo: {avg['rhythm_rate']:.3f}")
            print(f"   - Densidade de picos: {avg['peak_density']:.3f}")
            print(f"   - Tempo de ataque: {avg['attack_time']:.3f}s")
            print(f"   - Taxa de fala: {avg['speech_rate']:.0f} Hz")
            
            print("\n🤖 Valores do áudio gerado:")
            gen = comparison['generated_values']
            print(f"   - Energia: {gen['energy']:.3f}")
            print(f"   - Ritmo: {gen['rhythm_rate']:.3f}")
            print(f"   - Densidade de picos: {gen['peak_density']:.3f}")
            print(f"   - Tempo de ataque: {gen['attack_time']:.3f}s")
            print(f"   - Taxa de fala: {gen['speech_rate']:.0f} Hz")
            
            print("\n📈 Diferenças detectadas:")
            diff = comparison['differences']
            print(f"   - Energia: {diff['energy_diff']:+.3f} {'(precisa mais energia!)' if diff['energy_diff'] < 0 else ''}")
            print(f"   - Ritmo: {diff['rhythm_diff']:+.3f}")
            print(f"   - Picos: {diff['peak_diff']:+.3f} {'(precisa mais entusiasmo!)' if diff['peak_diff'] < 0 else ''}")
            print(f"   - Ataque: {diff['attack_diff']:+.3f}s {'(precisa começar mais rápido!)' if diff['attack_diff'] > 0 else ''}")
            print(f"   - Velocidade: {diff['speech_rate_diff']:+.0f} Hz {'(precisa falar mais rápido!)' if diff['speech_rate_diff'] < 0 else ''}")
            
            # Cria configuração otimizada
            print("\n🔧 Criando configuração otimizada baseada na análise...")
            
            # Ajusta parâmetros baseado nas diferenças
            new_config = {
                "voice_id": "oG30eP3GaYrCwnabbDCw",
                "voice_name": "FlukakuCambadaOptimized",
                "settings": {
                    "stability": 0.0 if comparison['suggestions']['needs_more_energy'] else 0.1,
                    "similarity_boost": 0.4 if comparison['suggestions']['needs_faster_speech'] else 0.5,
                    "style": 1.0,  # Máximo estilo sempre
                    "use_speaker_boost": True,
                    "model_id": "eleven_multilingual_v2"
                },
                "optimization_notes": {
                    "greeting_prefix": "FALA CAMBADAAA!!!",
                    "remove_spaces": True,
                    "add_emphasis": True,
                    "comparison_based": True
                },
                "prosody_targets": avg
            }
            
            # Salva configuração
            config_path = "config/voice_config_cambada_optimized.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, ensure_ascii=False, indent=4)
            
            print(f"\n✅ Nova configuração salva em: {config_path}")
            print("\n💡 Sugestões baseadas na análise:")
            if comparison['suggestions']['needs_more_energy']:
                print("   - ⚡ Precisa MUITO mais energia na saudação")
            if comparison['suggestions']['needs_faster_attack']:
                print("   - 🏃 Precisa começar mais rápido, sem hesitação")
            if comparison['suggestions']['needs_more_peaks']:
                print("   - 📢 Precisa mais picos de entusiasmo")
            if comparison['suggestions']['needs_faster_speech']:
                print("   - 💨 Precisa falar mais rápido")
    else:
        print("❌ Nenhum áudio gerado encontrado para comparar")

if __name__ == "__main__":
    main()