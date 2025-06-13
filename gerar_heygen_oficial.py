#!/usr/bin/env python3
"""
Gerador HeyGen usando documentação oficial v2
"""

import requests
import json
import time
import base64
from pathlib import Path

def gerar_todos_videos_heygen():
    """Gera todos os 5 vídeos usando API oficial v2"""
    
    api_key = "OTU2YjcxM2ZhZGY2NDE5Mjg3MzYzMmZlNjEyYjZiNzUtMTc0OTY5NDg0MQ=="
    avatar_id = "3034bbd37f2540ddb70c90c7f67b4f5c"
    
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    project_root = Path(__file__).parent.resolve()
    audio_dir = project_root / "output" / "reel_renato_melhorado" / "segments"
    
    audio_files = [
        ("01_abertura_audio.mp3", "Abertura"),
        ("02_connecticut_vs_estados_pro-cripto_audio.mp3", "Connecticut"), 
        ("03_brasileiros_investindo_em_cripto_audio.mp3", "Brasileiros"),
        ("04_bitcoin_30_dias_acima_de_100k_audio.mp3", "Bitcoin"),
        ("05_fechamento_audio.mp3", "Fechamento")
    ]
    
    print("🚀 HEYGEN API v2 - DOCUMENTAÇÃO OFICIAL!")
    print("=" * 60)
    print(f"🤖 Avatar: {avatar_id}")
    print(f"📊 Vídeos para gerar: {len(audio_files)}")
    print("🎯 Formato: 9:16 Portrait (1080x1920)")
    
    # Como a API não aceita upload direto de áudio, vamos tentar duas abordagens:
    # 1. Usar texto extraído do áudio (para teste)
    # 2. Tentar converter áudio para URL pública
    
    video_jobs = []
    
    # Textos dos áudios (extraídos do roteiro)
    textos = [
        "E aí cambada! Olha eu aí de novo. Bora pras novas!",
        "O estado de Conecticut aprovou uma lei que impede o governo estadual e prefeituras de comprar, manter ou investir em criptomoedas. E também veta o uso de cripto como forma de pagamento em serviço público. Enquanto isso, estados como Texas, Wyoming e Colorado estão liberando o uso de cripto e blockchain no setor público. O argumento oficial é proteger o contribuinte da volatilidade. Mas quando o governo corre pra proibir um tipo de dinheiro, é porque ele não quer perder o controle sobre como você transaciona. Curioso. Para o Drex, por exemplo, ninguém reclama. Mas pra uma moeda descentralizada que você controla? Aí já vira perigo!",
        "Olha esse dado que pouca gente sabe: quinze por cento dos brasileiros já investiram em criptomoedas. Pra você ter uma ideia, isso é mais do que: quatorze por cento que investem em dólar, doze por cento em renda fixa, nove por cento em ouro, e só seis por cento em ações. Ou seja: cripto já tá mais presente na carteira do brasileiro médio do que boa parte dos investimentos tradicionais. Só a boa e velha poupança ainda lidera, com cinquenta e dois por cento. Mas a tendência é clara: cada vez mais gente tá buscando alternativas fora do sistema financeiro tradicional. E isso, querendo ou não, é um movimento que combina muito com a proposta das criptos: dar mais autonomia pro cidadão sobre o próprio dinheiro.",
        "E agora falando de preço, o Bitcoin passou trinta dias seguidos acima de cem mil dólares. Algo inédito no mercado. Mesmo essa semana ele tendo sofrido uma queda e assustado muita gente, ele se segurou bem ali nos cem mil e já recuperou quase tudo voltando pros cento e dez. Isso mostra que não é só hype de gráfico. O BTC já tem consistência pra se manter em patamares altos, apontando pra maturidade e confiança. Enquanto governos tentam segurar ou proibir, o mercado segue validando uma moeda que não depende de bancos centrais.",
        "Por hoje é isso cambada. Governos tentando segurar a revolução. Brasileiros investindo além do tradicional. E o Bitcoin mostrando pra que veio. Sigo de olho."
    ]
    
    for i, ((arquivo, nome), texto) in enumerate(zip(audio_files, textos), 1):
        print(f"\n[{i}/{len(audio_files)}] 🎬 {nome}")
        
        # Payload baseado na documentação oficial
        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": texto,
                    "voice_id": "25NR0sM9ehsgXaoknsxO"  # Nossa voice ID
                },
                "background": {
                    "type": "color",
                    "value": "#000000"
                }
            }],
            "dimension": {
                "width": 1080,
                "height": 1920
            }
        }
        
        try:
            print("   🔄 Enviando para HeyGen...")
            
            response = requests.post(
                "https://api.heygen.com/v2/video/generate",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                video_id = result.get('data', {}).get('video_id')
                
                if video_id:
                    print(f"   ✅ Vídeo criado! ID: {video_id}")
                    video_jobs.append({
                        'id': video_id,
                        'nome': nome,
                        'arquivo': arquivo
                    })
                else:
                    print(f"   ❌ Sem video_id: {result}")
            else:
                print(f"   ❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Erro na requisição: {str(e)}")
        
        # Pausa entre requisições
        time.sleep(2)
    
    if not video_jobs:
        print("\n❌ Nenhum vídeo foi criado")
        return False
    
    print(f"\n🎬 {len(video_jobs)} VÍDEOS CRIADOS!")
    print("⏳ Aguardando processamento...")
    
    # Monitora todos os vídeos
    completed_videos = []
    max_wait = 1800  # 30 minutos
    start_time = time.time()
    
    while video_jobs and (time.time() - start_time) < max_wait:
        for job in video_jobs[:]:
            try:
                # Verifica status usando endpoint da documentação
                status_response = requests.get(
                    f"https://api.heygen.com/v1/video_status.get?video_id={job['id']}",
                    headers=headers,
                    timeout=30
                )
                
                if status_response.status_code == 200:
                    data = status_response.json().get('data', {})
                    status = data.get('status')
                    
                    if status == 'completed':
                        video_url = data.get('video_url')
                        if video_url:
                            print(f"✅ {job['nome']} - PRONTO!")
                            completed_videos.append({
                                'nome': job['nome'],
                                'url': video_url,
                                'arquivo': job['arquivo']
                            })
                            video_jobs.remove(job)
                    
                    elif status == 'failed':
                        error = data.get('error', 'Erro desconhecido')
                        print(f"❌ {job['nome']} - FALHOU: {error}")
                        video_jobs.remove(job)
                    
                    else:
                        print(f"⏳ {job['nome']} - {status}")
                
            except Exception as e:
                print(f"⚠️ Erro verificando {job['nome']}: {str(e)}")
        
        if video_jobs:
            time.sleep(15)
    
    # Baixa os vídeos
    if completed_videos:
        print(f"\n📥 BAIXANDO {len(completed_videos)} VÍDEOS...")
        
        output_dir = project_root / "output" / "videos_heygen_oficial"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for video in completed_videos:
            try:
                print(f"📥 {video['nome']}")
                
                response = requests.get(video['url'], stream=True)
                if response.status_code == 200:
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"{video['nome']}_{timestamp}.mp4"
                    output_path = output_dir / filename
                    
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"   ✅ {filename}")
                else:
                    print(f"   ❌ Erro no download: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Erro: {str(e)}")
        
        print(f"\n🎉 SUCESSO! {len(completed_videos)} vídeos gerados!")
        print(f"📁 Pasta: {output_dir}")
        print("\n🎬 PRÓXIMOS PASSOS:")
        print("1. Os vídeos estão com marca d'água (Free Trial)")
        print("2. Edite juntando na ordem: Abertura → Connecticut → Brasileiros → Bitcoin → Fechamento")
        print("3. Use cortes secos (sem transições)")
        print("4. Exporte em 9:16 para Reels")
        
        return True
    
    else:
        print("\n❌ Nenhum vídeo foi completado")
        return False

if __name__ == "__main__":
    success = gerar_todos_videos_heygen()
    if success:
        print("\n🎉 REEL GERADO COM SUCESSO!")
    else:
        print("\n❌ Falha na geração do reel")