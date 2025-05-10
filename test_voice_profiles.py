#!/usr/bin/env python3
"""
Script unificado para testar perfis de voz.
Permite testar diferentes perfis de voz, comparar configurações e gerar áudio/vídeo.
"""
import os
import sys
import json
import time
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_voice_profiles.log')
    ]
)
logger = logging.getLogger('test_voice_profiles')

# Importar os módulos necessários
try:
    from audio_generator import AudioGenerator, open_audio_file
    from heygen_video_generator import HeyGenVideoGenerator, open_video_file
    from core.text import TextProcessor
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    logger.error("Verifique se você está executando o script do diretório raiz do projeto.")
    sys.exit(1)

# Texto de exemplo para testes
DEFAULT_TEXT = """E aí CAMBADA! Tô de volta na área com energia!  
Bora de RAPIDINHA!  
Hoje eu tenho um desafio: tem algo diferente nesse vídeo... consegue adivinhar?  
Comenta aí!  
No fim do vídeo eu revelo o mistério!"""

# ID do avatar padrão
DEFAULT_AVATAR_ID = "ae9ff9b6dc47436c8e9a30c25a0d7b29"

# Pasta no HeyGen onde os vídeos serão salvos
DEFAULT_FOLDER_NAME = "augment"

def list_voice_profiles() -> List[str]:
    """
    Lista todos os perfis de voz disponíveis.
    
    Returns:
        List[str]: Lista de nomes de perfis disponíveis
    """
    config_dir = os.path.join(os.getcwd(), "config")
    profiles = []
    
    for filename in os.listdir(config_dir):
        if filename.startswith("voice_config_") and filename.endswith(".json"):
            profile_name = filename.replace("voice_config_", "").replace(".json", "")
            profiles.append(profile_name)
    
    return profiles

def get_current_profile() -> Dict[str, Any]:
    """
    Obtém o perfil de voz padrão atual.
    
    Returns:
        Dict[str, Any]: Configuração do perfil padrão
    """
    config_path = os.path.join(os.getcwd(), "config", "voice_config.json")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Erro ao carregar configuração padrão: {e}")
        return {}

def get_profile_config(profile_name: str) -> Dict[str, Any]:
    """
    Obtém a configuração de um perfil específico.
    
    Args:
        profile_name: Nome do perfil
        
    Returns:
        Dict[str, Any]: Configuração do perfil
    """
    config_path = os.path.join(os.getcwd(), "config", f"voice_config_{profile_name}.json")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Erro ao carregar configuração do perfil '{profile_name}': {e}")
        return {}

def compare_profiles(profiles: List[str]) -> None:
    """
    Compara as configurações de diferentes perfis de voz.
    
    Args:
        profiles: Lista de nomes de perfis para comparar
    """
    if not profiles:
        logger.info("Comparando todos os perfis disponíveis...")
        profiles = list_voice_profiles()
    
    logger.info(f"Comparando {len(profiles)} perfis: {', '.join(profiles)}")
    
    # Coletar configurações
    configs = {}
    for profile in profiles:
        config = get_profile_config(profile)
        if config:
            configs[profile] = config
    
    if not configs:
        logger.error("Nenhum perfil válido encontrado para comparação.")
        return
    
    # Exibir comparação
    logger.info("\n=== COMPARAÇÃO DE PERFIS DE VOZ ===")
    
    # Cabeçalho
    header = ["Parâmetro"] + list(configs.keys())
    logger.info(" | ".join(header))
    logger.info("-" * (len(" | ".join(header))))
    
    # Voice ID
    voice_ids = ["Voice ID"] + [config.get("voice_id", "N/A") for config in configs.values()]
    logger.info(" | ".join(voice_ids))
    
    # Voice Name
    voice_names = ["Voice Name"] + [config.get("voice_name", "N/A") for config in configs.values()]
    logger.info(" | ".join(voice_names))
    
    # Settings
    settings_keys = ["stability", "similarity_boost", "style", "use_speaker_boost", "model_id"]
    
    for key in settings_keys:
        values = [key]
        for config in configs.values():
            settings = config.get("settings", {})
            value = settings.get(key, "N/A")
            values.append(str(value))
        logger.info(" | ".join(values))
    
    # Análise
    logger.info("\n=== ANÁLISE DE DIFERENÇAS ===")
    
    for i, profile1 in enumerate(profiles):
        if profile1 not in configs:
            continue
            
        for profile2 in profiles[i+1:]:
            if profile2 not in configs:
                continue
                
            config1 = configs[profile1]
            config2 = configs[profile2]
            
            if "settings" in config1 and "settings" in config2:
                settings1 = config1["settings"]
                settings2 = config2["settings"]
                
                logger.info(f"\nDiferenças entre {profile1} e {profile2}:")
                
                for key in settings_keys:
                    if key in settings1 and key in settings2:
                        value1 = settings1[key]
                        value2 = settings2[key]
                        
                        if value1 != value2:
                            logger.info(f"- {key}: {value1} vs {value2}")

def generate_audio(text: str, profile_name: Optional[str] = None, optimize: bool = True, 
                  dry_run: bool = False, play: bool = True) -> Optional[str]:
    """
    Gera áudio com o perfil de voz especificado.
    
    Args:
        text: Texto a ser convertido em áudio
        profile_name: Nome do perfil a ser usado (None para usar o padrão)
        optimize: Se True, otimiza o texto para fala
        dry_run: Se True, simula a geração sem fazer chamadas de API
        play: Se True, reproduz o áudio após a geração
        
    Returns:
        Optional[str]: Caminho para o arquivo de áudio gerado, ou None se falhar
    """
    logger.info(f"Gerando áudio com o perfil '{profile_name or 'padrão'}'...")
    
    # Inicializar o gerador de áudio com o perfil especificado
    audio_generator = AudioGenerator(voice_profile=profile_name)
    
    # Otimizar o texto se solicitado
    if optimize:
        processor = TextProcessor()
        optimized_text = processor.optimize_for_speech(text)
        logger.info(f"Texto original: {text[:50]}...")
        logger.info(f"Texto otimizado: {optimized_text[:50]}...")
    else:
        optimized_text = text
    
    # Gerar nome para o arquivo de áudio
    timestamp = int(time.time())
    profile_suffix = profile_name or "padrao"
    output_dir = os.path.join(os.getcwd(), "output", "audio")
    os.makedirs(output_dir, exist_ok=True)
    audio_path = os.path.join(output_dir, f"audio_{profile_suffix}_{timestamp}.mp3")
    
    # Gerar o áudio
    audio_path = audio_generator.generate_audio(optimized_text, audio_path, optimize=False, dry_run=dry_run)
    
    if audio_path:
        logger.info(f"Áudio gerado com sucesso: {audio_path}")
        
        # Exibir as configurações usadas
        config = audio_generator.voice_settings
        logger.info(f"Configurações de voz usadas para '{profile_name or 'padrão'}':")
        logger.info(json.dumps(config, indent=2))
        
        # Reproduzir o áudio se solicitado
        if play and not dry_run:
            logger.info("Reproduzindo o áudio gerado...")
            open_audio_file(audio_path)
        
        return audio_path
    else:
        logger.error(f"Falha ao gerar áudio com o perfil '{profile_name or 'padrão'}'.")
        return None

def generate_video(text: str, audio_path: Optional[str] = None, avatar_id: str = DEFAULT_AVATAR_ID, 
                  folder_name: str = DEFAULT_FOLDER_NAME, play: bool = True) -> Optional[str]:
    """
    Gera vídeo com o avatar e áudio especificados.
    
    Args:
        text: Texto do script (para fallback)
        audio_path: Caminho para o arquivo de áudio (None para gerar áudio diretamente)
        avatar_id: ID do avatar a ser usado
        folder_name: Nome da pasta no HeyGen onde o vídeo será salvo
        play: Se True, reproduz o vídeo após a geração
        
    Returns:
        Optional[str]: Caminho para o arquivo de vídeo gerado, ou None se falhar
    """
    logger.info("Gerando vídeo com o HeyGen...")
    
    # Inicializar o gerador de vídeo
    video_generator = HeyGenVideoGenerator()
    
    # Gerar nome para o arquivo de vídeo
    timestamp = int(time.time())
    output_dir = os.path.join(os.getcwd(), "output", "videos")
    os.makedirs(output_dir, exist_ok=True)
    video_path = os.path.join(output_dir, f"video_test_{timestamp}.mp4")
    
    # Gerar o vídeo
    video_path = video_generator.generate_video(
        script=text,
        audio_path=audio_path,
        output_path=video_path,
        avatar_id=avatar_id,
        folder_name=folder_name
    )
    
    if video_path:
        logger.info(f"Vídeo gerado com sucesso: {video_path}")
        
        # Reproduzir o vídeo se solicitado
        if play:
            logger.info("Reproduzindo o vídeo gerado...")
            open_video_file(video_path)
        
        return video_path
    else:
        logger.error("Falha ao gerar vídeo.")
        return None

def main():
    """
    Função principal que processa os argumentos da linha de comando e executa as ações solicitadas.
    """
    parser = argparse.ArgumentParser(description="Ferramenta unificada para testar perfis de voz")
    
    # Ações principais
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--list", action="store_true", help="Listar perfis disponíveis")
    action_group.add_argument("--current", action="store_true", help="Mostrar perfil padrão atual")
    action_group.add_argument("--compare", action="store_true", help="Comparar perfis de voz")
    action_group.add_argument("--audio", action="store_true", help="Gerar áudio com perfil especificado")
    action_group.add_argument("--video", action="store_true", help="Gerar vídeo com áudio gerado")
    
    # Opções para comparação
    parser.add_argument("--profiles", nargs="+", help="Perfis a serem comparados")
    
    # Opções para geração de áudio
    parser.add_argument("--profile", help="Perfil de voz a ser usado")
    parser.add_argument("--text", help="Texto a ser convertido em áudio")
    parser.add_argument("--no-optimize", action="store_true", help="Não otimizar o texto para fala")
    parser.add_argument("--dry-run", action="store_true", help="Simular a geração sem fazer chamadas de API")
    parser.add_argument("--no-play", action="store_true", help="Não reproduzir o áudio/vídeo após a geração")
    
    # Opções para geração de vídeo
    parser.add_argument("--audio-path", help="Caminho para o arquivo de áudio a ser usado no vídeo")
    parser.add_argument("--avatar-id", default=DEFAULT_AVATAR_ID, help="ID do avatar a ser usado")
    parser.add_argument("--folder-name", default=DEFAULT_FOLDER_NAME, help="Nome da pasta no HeyGen")
    
    args = parser.parse_args()
    
    # Listar perfis disponíveis
    if args.list:
        profiles = list_voice_profiles()
        logger.info(f"Perfis disponíveis ({len(profiles)}):")
        for profile in profiles:
            logger.info(f"- {profile}")
    
    # Mostrar perfil padrão atual
    elif args.current:
        current = get_current_profile()
        if current:
            logger.info("Perfil padrão atual:")
            logger.info(json.dumps(current, indent=2))
        else:
            logger.error("Não foi possível obter o perfil padrão atual.")
    
    # Comparar perfis de voz
    elif args.compare:
        compare_profiles(args.profiles)
    
    # Gerar áudio com perfil especificado
    elif args.audio:
        text = args.text or DEFAULT_TEXT
        audio_path = generate_audio(
            text=text,
            profile_name=args.profile,
            optimize=not args.no_optimize,
            dry_run=args.dry_run,
            play=not args.no_play
        )
        
        if audio_path:
            logger.info(f"Áudio gerado com sucesso: {audio_path}")
    
    # Gerar vídeo com áudio gerado
    elif args.video:
        text = args.text or DEFAULT_TEXT
        
        # Se não foi fornecido um caminho de áudio, gerar o áudio primeiro
        audio_path = args.audio_path
        if not audio_path:
            logger.info("Nenhum áudio fornecido. Gerando áudio primeiro...")
            audio_path = generate_audio(
                text=text,
                profile_name=args.profile,
                optimize=not args.no_optimize,
                dry_run=args.dry_run,
                play=False
            )
        
        # Gerar o vídeo
        if audio_path or args.dry_run:
            video_path = generate_video(
                text=text,
                audio_path=audio_path,
                avatar_id=args.avatar_id,
                folder_name=args.folder_name,
                play=not args.no_play
            )
            
            if video_path:
                logger.info(f"Vídeo gerado com sucesso: {video_path}")
        else:
            logger.error("Não foi possível gerar o áudio para o vídeo.")

if __name__ == "__main__":
    main()
