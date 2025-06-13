#!/usr/bin/env python3
"""
Verifica voices disponíveis no HeyGen
"""

import requests
import json

def verificar_voices():
    """Verifica voices disponíveis na conta HeyGen"""
    
    api_key = "OTU2YjcxM2ZhZGY2NDE5Mjg3MzYzMmZlNjEyYjZiNzUtMTc0OTY5NDg0MQ=="
    
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    print("🔍 VERIFICANDO VOICES DISPONÍVEIS")
    print("=" * 50)
    
    # Verifica voices disponíveis
    try:
        response = requests.get(
            "https://api.heygen.com/v2/voices",
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            voices_data = response.json()
            print("✅ Voices carregadas!")
            
            if 'data' in voices_data:
                voices = voices_data['data']
                print(f"📋 Total de voices: {len(voices)}")
                print()
                
                # Lista as primeiras 10 voices
                for i, voice in enumerate(voices[:10], 1):
                    voice_id = voice.get('voice_id', 'N/A')
                    name = voice.get('name', 'N/A')
                    language = voice.get('language', 'N/A')
                    gender = voice.get('gender', 'N/A')
                    
                    print(f"[{i:2d}] {name}")
                    print(f"     ID: {voice_id}")
                    print(f"     Idioma: {language}")
                    print(f"     Gênero: {gender}")
                    print()
                
                # Procura por voices em português
                print("🇧🇷 VOICES EM PORTUGUÊS:")
                portuguese_voices = []
                for voice in voices:
                    language = voice.get('language', '').lower()
                    if 'portuguese' in language or 'pt' in language or 'brasil' in language.lower():
                        portuguese_voices.append(voice)
                
                if portuguese_voices:
                    for voice in portuguese_voices[:5]:
                        print(f"   • {voice.get('name', 'N/A')} ({voice.get('voice_id', 'N/A')})")
                else:
                    print("   ❌ Nenhuma voice em português encontrada")
                
                print()
                
                # Verifica se a voice ElevenLabs está disponível
                print("🔍 VERIFICANDO VOICE ELEVENLABS:")
                elevenlabs_voice = "25NR0sM9ehsgXaoknsxO"
                voice_encontrada = False
                
                for voice in voices:
                    if voice.get('voice_id') == elevenlabs_voice:
                        print(f"✅ Voice ElevenLabs encontrada: {voice.get('name', 'N/A')}")
                        voice_encontrada = True
                        break
                
                if not voice_encontrada:
                    print(f"❌ Voice {elevenlabs_voice} não encontrada")
                    print("💡 Precisamos usar uma voice nativa do HeyGen")
                    
                    # Sugere a primeira voice masculina em português
                    for voice in voices:
                        gender = voice.get('gender', '').lower()
                        language = voice.get('language', '').lower()
                        if 'male' in gender and ('portuguese' in language or 'pt' in language):
                            print(f"💡 Sugestão: {voice.get('name', 'N/A')} ({voice.get('voice_id', 'N/A')})")
                            break
                    else:
                        # Se não encontrar português, sugere a primeira masculina
                        for voice in voices:
                            gender = voice.get('gender', '').lower()
                            if 'male' in gender:
                                print(f"💡 Sugestão: {voice.get('name', 'N/A')} ({voice.get('voice_id', 'N/A')})")
                                break
            
            else:
                print("❌ Sem dados de voices na resposta")
                
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    verificar_voices()