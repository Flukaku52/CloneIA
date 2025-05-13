#!/usr/bin/env python3
"""
Script de instalação e configuração do sistema FlukakuIA.
"""
import os
import sys
import subprocess
import logging
import argparse
import shutil
import platform

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('setup')

def instalar_dependencias():
    """
    Instala as dependências necessárias.
    
    Returns:
        bool: True se as dependências foram instaladas com sucesso, False caso contrário
    """
    logger.info("Instalando dependências...")
    
    # Lista de dependências
    dependencias = [
        "requests",
        "python-dotenv",
        "fpdf",
        "markdown"
    ]
    
    # Instalar cada dependência
    for dependencia in dependencias:
        try:
            logger.info(f"Instalando {dependencia}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dependencia])
            logger.info(f"Dependência instalada: {dependencia}")
        except Exception as e:
            logger.error(f"Erro ao instalar dependência {dependencia}: {e}")
            return False
    
    logger.info("Todas as dependências foram instaladas com sucesso.")
    return True

def criar_estrutura_diretorios():
    """
    Cria a estrutura de diretórios necessária.
    
    Returns:
        bool: True se a estrutura foi criada com sucesso, False caso contrário
    """
    logger.info("Criando estrutura de diretórios...")
    
    # Lista de diretórios
    diretorios = [
        "output/audio",
        "output/videos",
        "scripts",
        "config",
        "backups",
        "core"
    ]
    
    # Criar cada diretório
    for diretorio in diretorios:
        try:
            if not os.path.exists(diretorio):
                os.makedirs(diretorio)
                logger.info(f"Diretório criado: {diretorio}")
            else:
                logger.info(f"Diretório já existe: {diretorio}")
        except Exception as e:
            logger.error(f"Erro ao criar diretório {diretorio}: {e}")
            return False
    
    logger.info("Estrutura de diretórios criada com sucesso.")
    return True

def configurar_env(elevenlabs_api_key=None, heygen_api_key=None):
    """
    Configura o arquivo .env com as chaves de API.
    
    Args:
        elevenlabs_api_key: Chave de API do ElevenLabs
        heygen_api_key: Chave de API do HeyGen
        
    Returns:
        bool: True se o arquivo foi configurado com sucesso, False caso contrário
    """
    logger.info("Configurando arquivo .env...")
    
    # Verificar se o arquivo já existe
    if os.path.exists(".env"):
        logger.info("Arquivo .env já existe. Fazendo backup...")
        shutil.copy2(".env", ".env.bak")
    
    # Obter chaves de API
    if not elevenlabs_api_key:
        elevenlabs_api_key = input("Digite a chave de API do ElevenLabs (deixe em branco para usar o valor padrão): ")
        if not elevenlabs_api_key:
            elevenlabs_api_key = "sk_2eeadfe816f7442422d9a3a508e5d912797de421403ba9d6"
    
    if not heygen_api_key:
        heygen_api_key = input("Digite a chave de API do HeyGen (deixe em branco para usar o valor padrão): ")
        if not heygen_api_key:
            heygen_api_key = "OTU2YjcxM2ZhZGY2NDE5Mjg3MzYzMmZlNjEyYjZiNzUtMTc0Njc1NzMxNQ=="
    
    # Criar arquivo .env
    try:
        with open(".env", "w") as f:
            f.write("# Chaves de API para serviços\n")
            f.write(f"ELEVENLABS_API_KEY={elevenlabs_api_key}\n")
            f.write(f"HEYGEN_API_KEY={heygen_api_key}\n")
        
        logger.info("Arquivo .env configurado com sucesso.")
        return True
    except Exception as e:
        logger.error(f"Erro ao configurar arquivo .env: {e}")
        return False

def configurar_git():
    """
    Configura o repositório Git.
    
    Returns:
        bool: True se o repositório foi configurado com sucesso, False caso contrário
    """
    logger.info("Configurando repositório Git...")
    
    try:
        # Verificar se já é um repositório Git
        resultado = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if resultado.returncode == 0:
            logger.info("Já é um repositório Git.")
        else:
            # Inicializar repositório
            subprocess.check_call(["git", "init"])
            logger.info("Repositório Git inicializado.")
            
            # Adicionar arquivos
            subprocess.check_call(["git", "add", "."])
            
            # Commit inicial
            subprocess.check_call(["git", "commit", "-m", "Configuração inicial do sistema FlukakuIA"])
            logger.info("Commit inicial realizado.")
        
        logger.info("Repositório Git configurado com sucesso.")
        return True
    except Exception as e:
        logger.error(f"Erro ao configurar repositório Git: {e}")
        return False

def configurar_permissoes():
    """
    Configura as permissões dos scripts.
    
    Returns:
        bool: True se as permissões foram configuradas com sucesso, False caso contrário
    """
    # Verificar se estamos no Windows
    if platform.system() == "Windows":
        logger.info("Configuração de permissões não é necessária no Windows.")
        return True
    
    logger.info("Configurando permissões dos scripts...")
    
    # Lista de scripts
    scripts = [
        "gerar_reels_simples.py",
        "processar_script_com_cortes.py",
        "backup_codigo.py",
        "verificar_integridade.py",
        "setup.py"
    ]
    
    # Configurar permissões de cada script
    for script in scripts:
        try:
            if os.path.exists(script):
                os.chmod(script, 0o755)
                logger.info(f"Permissões configuradas: {script}")
            else:
                logger.warning(f"Script não encontrado: {script}")
        except Exception as e:
            logger.error(f"Erro ao configurar permissões do script {script}: {e}")
            return False
    
    logger.info("Permissões configuradas com sucesso.")
    return True

def setup(elevenlabs_api_key=None, heygen_api_key=None, skip_git=False, skip_deps=False):
    """
    Configura o sistema FlukakuIA.
    
    Args:
        elevenlabs_api_key: Chave de API do ElevenLabs
        heygen_api_key: Chave de API do HeyGen
        skip_git: Se True, pula a configuração do Git
        skip_deps: Se True, pula a instalação de dependências
        
    Returns:
        bool: True se o sistema foi configurado com sucesso, False caso contrário
    """
    logger.info("Iniciando configuração do sistema FlukakuIA...")
    
    # Criar estrutura de diretórios
    if not criar_estrutura_diretorios():
        return False
    
    # Instalar dependências
    if not skip_deps and not instalar_dependencias():
        return False
    
    # Configurar arquivo .env
    if not configurar_env(elevenlabs_api_key, heygen_api_key):
        return False
    
    # Configurar repositório Git
    if not skip_git and not configurar_git():
        return False
    
    # Configurar permissões
    if not configurar_permissoes():
        return False
    
    logger.info("Sistema FlukakuIA configurado com sucesso!")
    return True

def main():
    """
    Função principal.
    """
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Configuração do sistema FlukakuIA")
    parser.add_argument("--elevenlabs-api-key", help="Chave de API do ElevenLabs")
    parser.add_argument("--heygen-api-key", help="Chave de API do HeyGen")
    parser.add_argument("--skip-git", action="store_true", help="Pular configuração do Git")
    parser.add_argument("--skip-deps", action="store_true", help="Pular instalação de dependências")
    parser.add_argument("--verbose", action="store_true", help="Exibir informações detalhadas")
    
    args = parser.parse_args()
    
    # Configurar nível de log
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Configurar sistema
    if setup(args.elevenlabs_api_key, args.heygen_api_key, args.skip_git, args.skip_deps):
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
