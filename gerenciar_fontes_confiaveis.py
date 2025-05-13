#!/usr/bin/env python3
"""
Script para gerenciar o banco de dados de fontes confiáveis.
"""
import os
import sys
import json
import argparse
import logging
from typing import Dict, Any, List, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gerenciar_fontes_confiaveis')

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar o gerenciador de fontes confiáveis
try:
    from core.trusted_sources_manager import TrustedSourcesManager
except ImportError:
    logger.error("Módulo trusted_sources_manager não encontrado. Verifique se o arquivo existe em core/trusted_sources_manager.py")
    sys.exit(1)

def listar_fontes(manager: TrustedSourcesManager, tipo: str = None) -> None:
    """
    Lista as fontes confiáveis.
    
    Args:
        manager: Gerenciador de fontes confiáveis
        tipo: Tipo de fonte ('twitter' ou 'website')
    """
    if tipo is None or tipo == "twitter":
        contas = manager.get_twitter_accounts()
        print(f"\nContas do Twitter ({len(contas)}):")
        print("-" * 80)
        for i, conta in enumerate(sorted(contas, key=lambda x: x.get("confiabilidade", 0), reverse=True), 1):
            print(f"{i}. @{conta['username']} - {conta.get('name', '')}")
            print(f"   Confiabilidade: {conta.get('confiabilidade', 0)}/10")
            print(f"   Categoria: {conta.get('categoria', 'N/A')}")
            print(f"   Idioma: {conta.get('idioma', 'N/A')}")
            print(f"   Tags: {', '.join(conta.get('tags', []))}")
            print()
    
    if tipo is None or tipo == "website":
        websites = manager.get_websites()
        print(f"\nWebsites ({len(websites)}):")
        print("-" * 80)
        for i, website in enumerate(sorted(websites, key=lambda x: x.get("confiabilidade", 0), reverse=True), 1):
            print(f"{i}. {website['nome']} - {website['url']}")
            print(f"   Confiabilidade: {website.get('confiabilidade', 0)}/10")
            print(f"   Categoria: {website.get('categoria', 'N/A')}")
            print(f"   Idioma: {website.get('idioma', 'N/A')}")
            print(f"   Tags: {', '.join(website.get('tags', []))}")
            print()

def adicionar_conta_twitter(manager: TrustedSourcesManager, username: str, nome: str, 
                           confiabilidade: int, categoria: str, idioma: str, 
                           descricao: str = "", tags: List[str] = None) -> None:
    """
    Adiciona uma nova conta do Twitter ao banco de dados.
    
    Args:
        manager: Gerenciador de fontes confiáveis
        username: Nome de usuário da conta
        nome: Nome completo da conta
        confiabilidade: Pontuação de confiabilidade (1-10)
        categoria: Categoria da conta
        idioma: Idioma principal da conta
        descricao: Descrição da conta
        tags: Lista de tags
    """
    # Validar confiabilidade
    confiabilidade = max(1, min(10, confiabilidade))
    
    # Criar objeto da conta
    conta = {
        "username": username,
        "name": nome,
        "description": descricao,
        "confiabilidade": confiabilidade,
        "categoria": categoria,
        "idioma": idioma,
        "tags": tags or []
    }
    
    # Adicionar ao banco de dados
    if manager.add_twitter_account(conta):
        print(f"Conta @{username} adicionada com sucesso!")
    else:
        print(f"Erro ao adicionar conta @{username}. Verifique se ela já existe.")

def adicionar_website(manager: TrustedSourcesManager, nome: str, url: str, 
                     confiabilidade: int, categoria: str, idioma: str, 
                     tags: List[str] = None) -> None:
    """
    Adiciona um novo website ao banco de dados.
    
    Args:
        manager: Gerenciador de fontes confiáveis
        nome: Nome do website
        url: URL do website
        confiabilidade: Pontuação de confiabilidade (1-10)
        categoria: Categoria do website
        idioma: Idioma principal do website
        tags: Lista de tags
    """
    # Validar confiabilidade
    confiabilidade = max(1, min(10, confiabilidade))
    
    # Criar objeto do website
    website = {
        "nome": nome,
        "url": url,
        "confiabilidade": confiabilidade,
        "categoria": categoria,
        "idioma": idioma,
        "tags": tags or []
    }
    
    # Adicionar ao banco de dados
    if manager.add_website(website):
        print(f"Website {nome} adicionado com sucesso!")
    else:
        print(f"Erro ao adicionar website {nome}. Verifique se ele já existe.")

def remover_fonte(manager: TrustedSourcesManager, tipo: str, identificador: str) -> None:
    """
    Remove uma fonte do banco de dados.
    
    Args:
        manager: Gerenciador de fontes confiáveis
        tipo: Tipo de fonte ('twitter' ou 'website')
        identificador: Identificador da fonte (username ou URL)
    """
    if tipo == "twitter":
        if manager.remove_twitter_account(identificador):
            print(f"Conta @{identificador} removida com sucesso!")
        else:
            print(f"Erro ao remover conta @{identificador}. Verifique se ela existe.")
    elif tipo == "website":
        if manager.remove_website(identificador):
            print(f"Website {identificador} removido com sucesso!")
        else:
            print(f"Erro ao remover website {identificador}. Verifique se ele existe.")
    else:
        print(f"Tipo de fonte inválido: {tipo}")

def atualizar_confiabilidade(manager: TrustedSourcesManager, tipo: str, identificador: str, 
                            confiabilidade: int) -> None:
    """
    Atualiza a pontuação de confiabilidade de uma fonte.
    
    Args:
        manager: Gerenciador de fontes confiáveis
        tipo: Tipo de fonte ('twitter' ou 'website')
        identificador: Identificador da fonte (username ou URL)
        confiabilidade: Nova pontuação de confiabilidade (1-10)
    """
    # Validar confiabilidade
    confiabilidade = max(1, min(10, confiabilidade))
    
    if tipo == "twitter":
        # Obter a conta atual
        conta = manager.get_twitter_account(identificador)
        if not conta:
            print(f"Conta @{identificador} não encontrada.")
            return
        
        # Atualizar confiabilidade
        conta["confiabilidade"] = confiabilidade
        
        # Salvar alterações
        if manager.update_twitter_account(identificador, conta):
            print(f"Confiabilidade da conta @{identificador} atualizada para {confiabilidade}/10.")
        else:
            print(f"Erro ao atualizar confiabilidade da conta @{identificador}.")
    
    elif tipo == "website":
        # Obter o website atual
        website = manager.get_website(identificador)
        if not website:
            print(f"Website {identificador} não encontrado.")
            return
        
        # Atualizar confiabilidade
        website["confiabilidade"] = confiabilidade
        
        # Salvar alterações
        if manager.update_website(identificador, website):
            print(f"Confiabilidade do website {identificador} atualizada para {confiabilidade}/10.")
        else:
            print(f"Erro ao atualizar confiabilidade do website {identificador}.")
    
    else:
        print(f"Tipo de fonte inválido: {tipo}")

def main():
    """
    Função principal.
    """
    parser = argparse.ArgumentParser(description="Gerenciador de fontes confiáveis")
    subparsers = parser.add_subparsers(dest="comando", help="Comando a executar")
    
    # Comando 'listar'
    listar_parser = subparsers.add_parser("listar", help="Listar fontes confiáveis")
    listar_parser.add_argument("--tipo", choices=["twitter", "website"], help="Tipo de fonte a listar")
    
    # Comando 'adicionar-twitter'
    add_twitter_parser = subparsers.add_parser("adicionar-twitter", help="Adicionar conta do Twitter")
    add_twitter_parser.add_argument("username", help="Nome de usuário da conta")
    add_twitter_parser.add_argument("nome", help="Nome completo da conta")
    add_twitter_parser.add_argument("--confiabilidade", type=int, default=7, help="Pontuação de confiabilidade (1-10)")
    add_twitter_parser.add_argument("--categoria", default="analista", help="Categoria da conta")
    add_twitter_parser.add_argument("--idioma", default="pt", help="Idioma principal da conta")
    add_twitter_parser.add_argument("--descricao", default="", help="Descrição da conta")
    add_twitter_parser.add_argument("--tags", nargs="+", default=[], help="Tags da conta")
    
    # Comando 'adicionar-website'
    add_website_parser = subparsers.add_parser("adicionar-website", help="Adicionar website")
    add_website_parser.add_argument("nome", help="Nome do website")
    add_website_parser.add_argument("url", help="URL do website")
    add_website_parser.add_argument("--confiabilidade", type=int, default=7, help="Pontuação de confiabilidade (1-10)")
    add_website_parser.add_argument("--categoria", default="notícias", help="Categoria do website")
    add_website_parser.add_argument("--idioma", default="pt", help="Idioma principal do website")
    add_website_parser.add_argument("--tags", nargs="+", default=[], help="Tags do website")
    
    # Comando 'remover'
    remover_parser = subparsers.add_parser("remover", help="Remover fonte")
    remover_parser.add_argument("tipo", choices=["twitter", "website"], help="Tipo de fonte")
    remover_parser.add_argument("identificador", help="Identificador da fonte (username ou URL)")
    
    # Comando 'atualizar-confiabilidade'
    atualizar_parser = subparsers.add_parser("atualizar-confiabilidade", help="Atualizar confiabilidade de uma fonte")
    atualizar_parser.add_argument("tipo", choices=["twitter", "website"], help="Tipo de fonte")
    atualizar_parser.add_argument("identificador", help="Identificador da fonte (username ou URL)")
    atualizar_parser.add_argument("confiabilidade", type=int, help="Nova pontuação de confiabilidade (1-10)")
    
    args = parser.parse_args()
    
    # Inicializar gerenciador
    manager = TrustedSourcesManager()
    
    # Executar comando
    if args.comando == "listar":
        listar_fontes(manager, args.tipo)
    
    elif args.comando == "adicionar-twitter":
        adicionar_conta_twitter(
            manager, args.username, args.nome, args.confiabilidade,
            args.categoria, args.idioma, args.descricao, args.tags
        )
    
    elif args.comando == "adicionar-website":
        adicionar_website(
            manager, args.nome, args.url, args.confiabilidade,
            args.categoria, args.idioma, args.tags
        )
    
    elif args.comando == "remover":
        remover_fonte(manager, args.tipo, args.identificador)
    
    elif args.comando == "atualizar-confiabilidade":
        atualizar_confiabilidade(manager, args.tipo, args.identificador, args.confiabilidade)
    
    else:
        parser.print_help()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
