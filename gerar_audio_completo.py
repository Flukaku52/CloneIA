#!/usr/bin/env python3
"""
Gera áudio completo do roteiro com quebras entre notícias
"""

import requests
import json
import time
from pathlib import Path

def gerar_audio_roteiro_completo():
    """Gera áudio único do roteiro completo com pausas"""
    
    # Configurações ElevenLabs
    api_key = "sk_d4e4dde07c2c95dac15248131f2781ef15b5781579b75527"
    voice_id = "25NR0sM9ehsgXaoknsxO"
    
    # Roteiro completo com quebras de 5 linhas entre notícias e 3 antes do "Sigo de olho"
    roteiro_completo = """E aí cambada! Olha eu aí de novo. Bora pras novas!





O estado de Conecticut aprovou uma lei que impede o governo estadual e prefeituras de comprar, manter ou investir em criptomoedas. E também veta o uso de cripto como forma de pagamento em serviço público. Enquanto isso, estados como Texas, Wyoming e Colorado estão liberando o uso de cripto e blockchain no setor público. O argumento oficial é proteger o contribuinte da volatilidade. Mas quando o governo corre pra proibir um tipo de dinheiro, é porque ele não quer perder o controle sobre como você transaciona. Curioso. Para o Drex, por exemplo, ninguém reclama. Mas pra uma moeda descentralizada que você controla? Aí já vira perigo!





Olha esse dado que pouca gente sabe: quinze por cento dos brasileiros já investiram em criptomoedas. Pra você ter uma ideia, isso é mais do que: quatorze por cento que investem em dólar, doze por cento em renda fixa, nove por cento em ouro, e só seis por cento em ações. Ou seja: cripto já tá mais presente na carteira do brasileiro médio do que boa parte dos investimentos tradicionais. Só a boa e velha poupança ainda lidera, com cinquenta e dois por cento. Mas a tendência é clara: cada vez mais gente tá buscando alternativas fora do sistema financeiro tradicional. E isso, querendo ou não, é um movimento que combina muito com a proposta das criptos: dar mais autonomia pro cidadão sobre o próprio dinheiro.





E agora falando de preço, o Bitcoin passou trinta dias seguidos acima de cem mil dólares. Algo inédito no mercado. Mesmo essa semana ele tendo sofrido uma queda e assustado muita gente, ele se segurou bem ali nos cem mil e já recuperou quase tudo, voltando pros cento e dez. Isso mostra que não é só hype de gráfico. O BTC já tem consistência pra se manter em patamares altos, apontando pra maturidade e confiança. Enquanto governos tentam segurar ou proibir, o mercado segue validando uma moeda que não depende de bancos centrais.





Por hoje é isso cambada. Governos tentando segurar a revolução. Brasileiros investindo além do tradicional. E o Bitcoin mostrando pra que veio.


Sigo de olho."""
    
    print("🎵 GERANDO ÁUDIO COMPLETO DO ROTEIRO")
    print("=" * 60)
    print(f"🎤 Voice ID: {voice_id}")
    print(f"📝 Caracteres: {len(roteiro_completo)}")
    print()
    
    # Configurações de voz
    voice_settings = {
        "stability": 0.2,
        "similarity_boost": 0.7,
        "style": 0.0,
        "use_speaker_boost": True
    }
    
    # Payload para ElevenLabs
    payload = {
        "text": roteiro_completo,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": voice_settings
    }
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    try:
        print("🔄 Enviando para ElevenLabs...")
        
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            json=payload,
            headers=headers,
            timeout=300  # 5 minutos para áudio longo
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            # Salva o áudio
            project_root = Path(__file__).parent.resolve()
            output_dir = project_root / "output" / "audio_completo"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"roteiro_completo_{timestamp}.mp3"
            output_path = output_dir / filename
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ ÁUDIO GERADO COM SUCESSO!")
            print(f"📁 Arquivo: {output_path}")
            print(f"📊 Tamanho: {len(response.content)} bytes")
            print()
            print("🎬 PRÓXIMOS PASSOS:")
            print("1. Use este áudio no HeyGen para gerar vídeo único")
            print("2. Avatar ID: 3034bbd37f2540ddb70c90c7f67b4f5c")
            print("3. Formato: 9:16 Portrait")
            print("4. Background: #000000")
            
            return output_path
            
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {str(e)}")
        return None

if __name__ == "__main__":
    audio_path = gerar_audio_roteiro_completo()
    
    if audio_path:
        print(f"\n🎉 ÁUDIO COMPLETO PRONTO!")
        print(f"📁 {audio_path}")
    else:
        print("\n❌ Falha na geração do áudio")