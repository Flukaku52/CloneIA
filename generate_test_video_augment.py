#!/usr/bin/env python3
"""
Script para gerar um vídeo de teste na pasta "augment" do HeyGen.
"""
import os
import subprocess
import argparse
from datetime import datetime

def generate_test_script(short=False):
    """
    Cria um script de teste para o vídeo.

    Args:
        short (bool): Se True, gera um script mais curto para teste.

    Returns:
        str: Caminho para o arquivo de script criado.
    """
    if short:
        script_content = """E aí cambada! Tô de volta com mais uma Rapidinha Cripto!

Hoje vamos falar sobre o Bitcoin, que tá dando um show no mercado. O BTC continua subindo e já tá mirando novos recordes!

É isso cambada! Se gostou, deixa o like e compartilha com a galera. Até a próxima Rapidinha Cripto!"""
    else:
        script_content = """E aí cambada! Tô de volta com mais uma Rapidinha Cripto!

Hoje vamos falar sobre o Bitcoin, que tá dando um show no mercado. Depois de quebrar a resistência dos 60 mil dólares, o BTC continua subindo e já tá mirando os 70 mil!

O que tá impulsionando essa alta? Primeiro, os ETFs de Bitcoin nos Estados Unidos continuam atraindo bilhões em investimentos. É dinheiro institucional entrando forte no mercado.

Segundo, a mineração de Bitcoin tá mais descentralizada do que nunca depois do último halving. Isso fortalece a rede e aumenta a confiança dos investidores.

E não para por aí! O Ethereum também tá bombando, com o ETH ultrapassando os 3 mil dólares, impulsionado pelo sucesso das aplicações DeFi e a migração completa para o Proof of Stake.

Mas atenção: com grandes altas vêm grandes correções. Não se empolguem demais e lembrem de sempre gerenciar o risco.

Se você tá começando agora, vai com calma. Estuda, investe aos poucos e não coloca tudo de uma vez.

É isso cambada! Se gostou, deixa o like e compartilha com a galera. Até a próxima Rapidinha Cripto!"""

    # Criar diretório de scripts se não existir
    scripts_dir = os.path.join(os.getcwd(), "scripts")
    os.makedirs(scripts_dir, exist_ok=True)

    # Nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_path = os.path.join(scripts_dir, f"rapidinha_test_script_{timestamp}.txt")

    # Salvar o script
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)

    print(f"Script de teste criado em: {script_path}")
    return script_path

def generate_audio(script_path):
    """
    Gera áudio a partir do script usando a voz atualizada do ElevenLabs.

    Args:
        script_path (str): Caminho para o arquivo de script.

    Returns:
        str: Caminho para o arquivo de áudio gerado, ou None se falhar.
    """
    print("\n=== Gerando áudio com a voz atualizada do ElevenLabs ===")

    # Ler o conteúdo do script
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
    except Exception as e:
        print(f"Erro ao ler o script: {e}")
        return None

    # Importar o gerador de áudio diretamente
    try:
        from audio_generator import AudioGenerator

        # Criar o gerador de áudio
        generator = AudioGenerator()

        # Gerar o áudio
        audio_path = generator.generate_audio(script_content)

        if audio_path and os.path.exists(audio_path):
            print(f"Áudio gerado com sucesso: {audio_path}")
            return audio_path
        else:
            print("Erro: Arquivo de áudio não foi gerado.")
            return None
    except Exception as e:
        print(f"Erro ao gerar áudio: {e}")
        return None

def generate_video_with_heygen(script_path, audio_path):
    """
    Gera um vídeo usando o HeyGen na pasta "augment".

    Args:
        script_path (str): Caminho para o arquivo de script.
        audio_path (str): Caminho para o arquivo de áudio.

    Returns:
        str: Caminho para o vídeo gerado, ou None se falhar.
    """
    print("\n=== Gerando vídeo com HeyGen na pasta 'augment' ===")

    try:
        # Importar o gerador de vídeo do HeyGen
        from heygen_video_generator import HeyGenVideoGenerator

        # Ler o script
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()

        # Criar o gerador de vídeo
        heygen_generator = HeyGenVideoGenerator()

        # Usar seu avatar personalizado
        heygen_generator.avatar_id = "ae9ff9b6dc47436c8e9a30c25a0d7b29"  # Seu avatar atualizado
        print(f"Usando seu avatar personalizado: {heygen_generator.avatar_id}")

        # Diretório para o vídeo
        output_dir = os.path.join(os.getcwd(), "output", "videos")
        os.makedirs(output_dir, exist_ok=True)

        # Nome do arquivo com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = os.path.join(output_dir, f"test_heygen_augment_{timestamp}.mp4")

        # Gerar o vídeo na pasta "augment"
        video_path = heygen_generator.generate_video(
            script_content,
            audio_path,
            video_path,
            folder_name="augment"
        )

        if video_path:
            print(f"Vídeo gerado com sucesso: {video_path}")
            return video_path
        else:
            print("Erro: Falha ao gerar o vídeo.")
            return None
    except Exception as e:
        print(f"Erro ao gerar vídeo: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Gera um vídeo de teste na pasta 'augment' do HeyGen")
    parser.add_argument("--script", help="Caminho para um script personalizado")
    parser.add_argument("--audio", help="Caminho para um arquivo de áudio personalizado")
    parser.add_argument("--short", action="store_true", help="Usar um script curto para teste")

    args = parser.parse_args()

    # Etapa 1: Criar ou usar script
    if args.script and os.path.exists(args.script):
        script_path = args.script
        print(f"Usando script personalizado: {script_path}")
    else:
        script_path = generate_test_script(short=args.short)

    # Etapa 2: Gerar ou usar áudio
    if args.audio and os.path.exists(args.audio):
        audio_path = args.audio
        print(f"Usando áudio personalizado: {audio_path}")
    else:
        audio_path = generate_audio(script_path)

    if not audio_path:
        print("Erro: Não foi possível obter o arquivo de áudio.")
        return

    # Etapa 3: Gerar vídeo com HeyGen
    video_path = generate_video_with_heygen(script_path, audio_path)

    # Resumo
    print("\n=== Resumo ===")
    print(f"Script: {script_path}")
    print(f"Áudio: {audio_path}")
    print(f"Vídeo: {video_path if video_path else 'Não gerado'}")

if __name__ == "__main__":
    main()
