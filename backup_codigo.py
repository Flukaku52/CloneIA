#!/usr/bin/env python3
"""
Script para fazer backup do código antes de otimizações.
"""
import os
import sys
import shutil
import datetime
import argparse
import logging
import subprocess

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('backup_codigo')

def criar_backup(pasta_destino=None, incluir_timestamp=True):
    """
    Cria um backup do código atual.
    
    Args:
        pasta_destino: Pasta onde o backup será salvo (opcional)
        incluir_timestamp: Se True, inclui timestamp no nome da pasta de backup
        
    Returns:
        str: Caminho para o backup criado
    """
    # Definir pasta de destino
    if not pasta_destino:
        pasta_destino = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
    
    # Criar pasta de backups se não existir
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        logger.info(f"Pasta de backups criada: {pasta_destino}")
    
    # Definir nome do backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if incluir_timestamp:
        nome_backup = f"flukakuia_backup_{timestamp}"
    else:
        nome_backup = "flukakuia_backup_latest"
    
    caminho_backup = os.path.join(pasta_destino, nome_backup)
    
    # Verificar se já existe um backup com esse nome
    if os.path.exists(caminho_backup):
        if incluir_timestamp:
            # Se incluir timestamp, adicionar um sufixo
            i = 1
            while os.path.exists(f"{caminho_backup}_{i}"):
                i += 1
            caminho_backup = f"{caminho_backup}_{i}"
        else:
            # Se não incluir timestamp, remover o backup existente
            shutil.rmtree(caminho_backup)
    
    # Criar pasta do backup
    os.makedirs(caminho_backup)
    
    # Listar arquivos importantes para backup
    arquivos_importantes = [
        "gerar_reels_simples.py",
        "processar_script_com_cortes.py",
        "core/audio_generator.py",
        "core/content_splitter.py",
        ".env",
        "config/content_params.json"
    ]
    
    # Adicionar scripts de exemplo
    for arquivo in os.listdir("scripts"):
        if arquivo.endswith(".txt"):
            arquivos_importantes.append(f"scripts/{arquivo}")
    
    # Copiar arquivos
    for arquivo in arquivos_importantes:
        try:
            # Verificar se o arquivo existe
            if os.path.exists(arquivo):
                # Criar estrutura de diretórios no backup
                diretorio_destino = os.path.dirname(os.path.join(caminho_backup, arquivo))
                if not os.path.exists(diretorio_destino):
                    os.makedirs(diretorio_destino)
                
                # Copiar arquivo
                shutil.copy2(arquivo, os.path.join(caminho_backup, arquivo))
                logger.info(f"Arquivo copiado: {arquivo}")
            else:
                logger.warning(f"Arquivo não encontrado: {arquivo}")
        except Exception as e:
            logger.error(f"Erro ao copiar arquivo {arquivo}: {e}")
    
    # Criar arquivo de metadados
    try:
        # Obter informações do Git
        commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
        
        # Criar arquivo de metadados
        with open(os.path.join(caminho_backup, "backup_info.txt"), "w") as f:
            f.write(f"Data: {timestamp}\n")
            f.write(f"Commit: {commit_hash}\n")
            f.write(f"Branch: {branch}\n")
            f.write(f"Arquivos: {len(arquivos_importantes)}\n")
    except Exception as e:
        logger.error(f"Erro ao criar arquivo de metadados: {e}")
    
    logger.info(f"Backup criado com sucesso: {caminho_backup}")
    return caminho_backup

def restaurar_backup(caminho_backup, forcar=False):
    """
    Restaura um backup.
    
    Args:
        caminho_backup: Caminho para o backup a ser restaurado
        forcar: Se True, força a restauração mesmo se houver alterações não commitadas
        
    Returns:
        bool: True se o backup foi restaurado com sucesso, False caso contrário
    """
    # Verificar se o backup existe
    if not os.path.exists(caminho_backup):
        logger.error(f"Backup não encontrado: {caminho_backup}")
        return False
    
    # Verificar se há alterações não commitadas
    if not forcar:
        try:
            status = subprocess.check_output(["git", "status", "--porcelain"]).decode().strip()
            if status:
                logger.error("Há alterações não commitadas. Use --forcar para restaurar mesmo assim.")
                return False
        except Exception as e:
            logger.error(f"Erro ao verificar status do Git: {e}")
            return False
    
    # Listar arquivos no backup
    arquivos_backup = []
    for raiz, _, arquivos in os.walk(caminho_backup):
        for arquivo in arquivos:
            if arquivo != "backup_info.txt":
                caminho_completo = os.path.join(raiz, arquivo)
                caminho_relativo = os.path.relpath(caminho_completo, caminho_backup)
                arquivos_backup.append(caminho_relativo)
    
    # Restaurar arquivos
    for arquivo in arquivos_backup:
        try:
            # Criar estrutura de diretórios
            diretorio_destino = os.path.dirname(arquivo)
            if diretorio_destino and not os.path.exists(diretorio_destino):
                os.makedirs(diretorio_destino)
            
            # Copiar arquivo
            shutil.copy2(os.path.join(caminho_backup, arquivo), arquivo)
            logger.info(f"Arquivo restaurado: {arquivo}")
        except Exception as e:
            logger.error(f"Erro ao restaurar arquivo {arquivo}: {e}")
    
    logger.info(f"Backup restaurado com sucesso: {caminho_backup}")
    return True

def main():
    """
    Função principal.
    """
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Ferramenta de backup do código")
    subparsers = parser.add_subparsers(dest="comando", help="Comando a ser executado")
    
    # Comando de backup
    backup_parser = subparsers.add_parser("backup", help="Criar um backup do código")
    backup_parser.add_argument("--destino", help="Pasta onde o backup será salvo")
    backup_parser.add_argument("--sem-timestamp", action="store_true", help="Não incluir timestamp no nome da pasta de backup")
    
    # Comando de restauração
    restaurar_parser = subparsers.add_parser("restaurar", help="Restaurar um backup")
    restaurar_parser.add_argument("caminho", help="Caminho para o backup a ser restaurado")
    restaurar_parser.add_argument("--forcar", action="store_true", help="Forçar restauração mesmo se houver alterações não commitadas")
    
    # Comando de listagem
    listar_parser = subparsers.add_parser("listar", help="Listar backups disponíveis")
    listar_parser.add_argument("--destino", help="Pasta onde os backups estão salvos")
    
    args = parser.parse_args()
    
    # Executar comando
    if args.comando == "backup":
        criar_backup(args.destino, not args.sem_timestamp)
    elif args.comando == "restaurar":
        restaurar_backup(args.caminho, args.forcar)
    elif args.comando == "listar":
        pasta_destino = args.destino or os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
        if os.path.exists(pasta_destino):
            backups = [d for d in os.listdir(pasta_destino) if os.path.isdir(os.path.join(pasta_destino, d))]
            if backups:
                print("Backups disponíveis:")
                for backup in sorted(backups):
                    info_path = os.path.join(pasta_destino, backup, "backup_info.txt")
                    if os.path.exists(info_path):
                        with open(info_path, "r") as f:
                            info = f.read()
                        print(f"\n{backup}:\n{info}")
                    else:
                        print(f"\n{backup}")
            else:
                print("Nenhum backup encontrado.")
        else:
            print(f"Pasta de backups não encontrada: {pasta_destino}")
    else:
        parser.print_help()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
