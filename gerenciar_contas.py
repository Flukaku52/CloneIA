#!/usr/bin/env python3
"""
Script para gerenciar contas do HeyGen.
"""
import os
import sys
import logging
import argparse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gerenciar_contas')

# Importar gerenciador de contas
try:
    from core.account_manager import AccountManager
    account_manager = AccountManager()
except ImportError:
    logger.error("Módulo account_manager não encontrado.")
    sys.exit(1)

def listar_contas():
    """
    Lista todas as contas HeyGen.
    """
    contas = account_manager.list_heygen_accounts()
    conta_ativa = account_manager.get_active_heygen_account_id()
    
    print("\nContas HeyGen disponíveis:")
    for conta_id, conta_info in contas.items():
        status = " (ATIVA)" if conta_id == conta_ativa else ""
        print(f"  - {conta_id}{status}: {conta_info.get('description', '')}")
        print(f"    API Key: {conta_info.get('api_key', '')[:10]}...")
        print(f"    Avatar ID: {conta_info.get('avatar_id', '')}")
    
    return True

def adicionar_conta(conta_id, api_key, avatar_id, descricao):
    """
    Adiciona uma nova conta HeyGen.
    
    Args:
        conta_id: ID da conta
        api_key: Chave de API
        avatar_id: ID do avatar
        descricao: Descrição da conta
        
    Returns:
        bool: True se a conta foi adicionada com sucesso, False caso contrário
    """
    if account_manager.add_heygen_account(conta_id, api_key, avatar_id, descricao):
        print(f"Conta {conta_id} adicionada com sucesso!")
        return True
    else:
        print(f"Falha ao adicionar conta {conta_id}.")
        return False

def remover_conta(conta_id):
    """
    Remove uma conta HeyGen.
    
    Args:
        conta_id: ID da conta
        
    Returns:
        bool: True se a conta foi removida com sucesso, False caso contrário
    """
    if account_manager.remove_heygen_account(conta_id):
        print(f"Conta {conta_id} removida com sucesso!")
        return True
    else:
        print(f"Falha ao remover conta {conta_id}.")
        return False

def definir_conta_ativa(conta_id):
    """
    Define a conta HeyGen ativa.
    
    Args:
        conta_id: ID da conta
        
    Returns:
        bool: True se a conta foi definida como ativa com sucesso, False caso contrário
    """
    if account_manager.set_active_heygen_account(conta_id):
        print(f"Conta {conta_id} definida como ativa com sucesso!")
        return True
    else:
        print(f"Falha ao definir conta {conta_id} como ativa.")
        return False

def main():
    """
    Função principal.
    """
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Gerenciador de contas HeyGen")
    subparsers = parser.add_subparsers(dest="comando", help="Comando a ser executado")
    
    # Comando para listar contas
    listar_parser = subparsers.add_parser("listar", help="Listar contas HeyGen")
    
    # Comando para adicionar conta
    adicionar_parser = subparsers.add_parser("adicionar", help="Adicionar conta HeyGen")
    adicionar_parser.add_argument("--id", required=True, help="ID da conta (ex: conta1, conta2, etc.)")
    adicionar_parser.add_argument("--api-key", required=True, help="Chave de API do HeyGen")
    adicionar_parser.add_argument("--avatar-id", required=True, help="ID do avatar do HeyGen")
    adicionar_parser.add_argument("--descricao", default="", help="Descrição da conta")
    
    # Comando para remover conta
    remover_parser = subparsers.add_parser("remover", help="Remover conta HeyGen")
    remover_parser.add_argument("--id", required=True, help="ID da conta a ser removida")
    
    # Comando para definir conta ativa
    ativar_parser = subparsers.add_parser("ativar", help="Definir conta HeyGen ativa")
    ativar_parser.add_argument("--id", required=True, help="ID da conta a ser ativada")
    
    args = parser.parse_args()
    
    # Executar comando
    if args.comando == "listar":
        listar_contas()
    elif args.comando == "adicionar":
        adicionar_conta(args.id, args.api_key, args.avatar_id, args.descricao)
    elif args.comando == "remover":
        remover_conta(args.id)
    elif args.comando == "ativar":
        definir_conta_ativa(args.id)
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
