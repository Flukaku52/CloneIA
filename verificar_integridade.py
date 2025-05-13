#!/usr/bin/env python3
"""
Script para verificar a integridade do sistema FlukakuIA.
"""
import os
import sys
import importlib
import logging
import argparse
import subprocess

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('verificar_integridade')

def verificar_arquivos():
    """
    Verifica se todos os arquivos necessários estão presentes.
    
    Returns:
        bool: True se todos os arquivos estão presentes, False caso contrário
    """
    # Lista de arquivos essenciais
    arquivos_essenciais = [
        "gerar_reels_simples.py",
        "processar_script_com_cortes.py",
        "core/audio_generator.py",
        "core/content_splitter.py",
        ".env",
        "config/content_params.json"
    ]
    
    # Verificar cada arquivo
    arquivos_faltando = []
    for arquivo in arquivos_essenciais:
        if not os.path.exists(arquivo):
            arquivos_faltando.append(arquivo)
            logger.error(f"Arquivo essencial não encontrado: {arquivo}")
    
    # Verificar diretórios
    diretorios_essenciais = [
        "output/audio",
        "output/videos",
        "scripts"
    ]
    
    for diretorio in diretorios_essenciais:
        if not os.path.exists(diretorio):
            logger.warning(f"Diretório não encontrado: {diretorio}")
            try:
                os.makedirs(diretorio)
                logger.info(f"Diretório criado: {diretorio}")
            except Exception as e:
                logger.error(f"Erro ao criar diretório {diretorio}: {e}")
                arquivos_faltando.append(diretorio)
    
    # Verificar se há pelo menos um script de exemplo
    scripts = [f for f in os.listdir("scripts") if f.endswith(".txt")]
    if not scripts:
        logger.warning("Nenhum script de exemplo encontrado.")
    
    # Retornar resultado
    if arquivos_faltando:
        logger.error(f"Verificação de arquivos falhou. {len(arquivos_faltando)} arquivos faltando.")
        return False
    else:
        logger.info("Verificação de arquivos concluída com sucesso.")
        return True

def verificar_dependencias():
    """
    Verifica se todas as dependências Python estão instaladas.
    
    Returns:
        bool: True se todas as dependências estão instaladas, False caso contrário
    """
    # Lista de dependências
    dependencias = [
        "requests",
        "python-dotenv",
        "fpdf",
        "markdown"
    ]
    
    # Verificar cada dependência
    dependencias_faltando = []
    for dependencia in dependencias:
        try:
            importlib.import_module(dependencia)
            logger.info(f"Dependência encontrada: {dependencia}")
        except ImportError:
            dependencias_faltando.append(dependencia)
            logger.error(f"Dependência não encontrada: {dependencia}")
    
    # Retornar resultado
    if dependencias_faltando:
        logger.error(f"Verificação de dependências falhou. {len(dependencias_faltando)} dependências faltando.")
        return False
    else:
        logger.info("Verificação de dependências concluída com sucesso.")
        return True

def verificar_apis():
    """
    Verifica se as chaves de API estão configuradas.
    
    Returns:
        bool: True se as chaves de API estão configuradas, False caso contrário
    """
    # Carregar variáveis de ambiente
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.error("Não foi possível carregar o módulo python-dotenv.")
        return False
    
    # Verificar chaves de API
    chaves_api = {
        "ELEVENLABS_API_KEY": os.environ.get("ELEVENLABS_API_KEY"),
        "HEYGEN_API_KEY": os.environ.get("HEYGEN_API_KEY")
    }
    
    # Verificar cada chave
    chaves_faltando = []
    for nome, chave in chaves_api.items():
        if not chave or chave == "sua_chave_aqui":
            chaves_faltando.append(nome)
            logger.error(f"Chave de API não configurada: {nome}")
        else:
            logger.info(f"Chave de API configurada: {nome}")
    
    # Retornar resultado
    if chaves_faltando:
        logger.error(f"Verificação de APIs falhou. {len(chaves_faltando)} chaves faltando.")
        return False
    else:
        logger.info("Verificação de APIs concluída com sucesso.")
        return True

def verificar_git():
    """
    Verifica se o repositório Git está configurado corretamente.
    
    Returns:
        bool: True se o repositório Git está configurado corretamente, False caso contrário
    """
    try:
        # Verificar se é um repositório Git
        subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"])
        
        # Obter informações do repositório
        commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
        
        logger.info(f"Repositório Git configurado corretamente.")
        logger.info(f"Branch atual: {branch}")
        logger.info(f"Commit atual: {commit_hash}")
        
        # Verificar se há alterações não commitadas
        status = subprocess.check_output(["git", "status", "--porcelain"]).decode().strip()
        if status:
            logger.warning("Há alterações não commitadas no repositório.")
        
        return True
    except Exception as e:
        logger.error(f"Erro ao verificar repositório Git: {e}")
        return False

def verificar_integridade(corrigir=False):
    """
    Verifica a integridade do sistema FlukakuIA.
    
    Args:
        corrigir: Se True, tenta corrigir problemas encontrados
        
    Returns:
        bool: True se o sistema está íntegro, False caso contrário
    """
    logger.info("Iniciando verificação de integridade do sistema FlukakuIA...")
    
    # Verificar arquivos
    arquivos_ok = verificar_arquivos()
    
    # Verificar dependências
    dependencias_ok = verificar_dependencias()
    
    # Verificar APIs
    apis_ok = verificar_apis()
    
    # Verificar Git
    git_ok = verificar_git()
    
    # Verificar se tudo está ok
    tudo_ok = arquivos_ok and dependencias_ok and apis_ok and git_ok
    
    # Tentar corrigir problemas
    if not tudo_ok and corrigir:
        logger.info("Tentando corrigir problemas...")
        
        # Instalar dependências faltantes
        if not dependencias_ok:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "python-dotenv", "fpdf", "markdown"])
                logger.info("Dependências instaladas com sucesso.")
                dependencias_ok = True
            except Exception as e:
                logger.error(f"Erro ao instalar dependências: {e}")
        
        # Criar diretórios faltantes
        if not arquivos_ok:
            for diretorio in ["output/audio", "output/videos", "scripts"]:
                if not os.path.exists(diretorio):
                    try:
                        os.makedirs(diretorio)
                        logger.info(f"Diretório criado: {diretorio}")
                    except Exception as e:
                        logger.error(f"Erro ao criar diretório {diretorio}: {e}")
        
        # Verificar novamente
        tudo_ok = arquivos_ok and dependencias_ok and apis_ok and git_ok
    
    # Exibir resultado
    if tudo_ok:
        logger.info("Sistema FlukakuIA íntegro!")
    else:
        logger.error("Sistema FlukakuIA não está íntegro. Corrija os problemas antes de continuar.")
    
    return tudo_ok

def main():
    """
    Função principal.
    """
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Verificador de integridade do sistema FlukakuIA")
    parser.add_argument("--corrigir", action="store_true", help="Tentar corrigir problemas encontrados")
    parser.add_argument("--verbose", action="store_true", help="Exibir informações detalhadas")
    
    args = parser.parse_args()
    
    # Configurar nível de log
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Verificar integridade
    if verificar_integridade(args.corrigir):
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
