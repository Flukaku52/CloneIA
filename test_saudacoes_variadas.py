#!/usr/bin/env python3
"""
Script para testar as saudações variadas no gerenciador de conteúdo.
"""
import os
import sys
import logging
from typing import List

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_saudacoes_variadas')

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar o gerenciador de conteúdo
try:
    from core.content_manager import ContentManager
except ImportError:
    logger.error("Módulo content_manager não encontrado. Verifique se o arquivo existe em core/content_manager.py")
    sys.exit(1)

def testar_saudacoes(num_testes: int = 10) -> None:
    """
    Testa as saudações variadas gerando múltiplos scripts.
    
    Args:
        num_testes: Número de testes a realizar
    """
    # Criar o gerenciador de conteúdo
    manager = ContentManager()
    
    # Obter as saudações disponíveis
    saudacoes = manager.saudacoes_variadas
    
    print(f"Saudações disponíveis ({len(saudacoes)}):")
    for i, saudacao in enumerate(saudacoes, 1):
        print(f"{i}. {saudacao}")
    print()
    
    # Gerar múltiplos scripts para testar as saudações
    print(f"Gerando {num_testes} scripts com saudações aleatórias:")
    print("-" * 60)
    
    saudacoes_usadas = []
    
    for i in range(num_testes):
        # Gerar um script de exemplo
        titulo = f"Teste {i+1}: Bitcoin atinge novo recorde"
        conteudo = "Este é um teste de saudação variada."
        
        # Formatar o script
        script = manager.format_script(titulo, conteudo)
        
        # Extrair a primeira linha (que contém a saudação)
        primeira_linha = script.split('\n')[0]
        
        # Adicionar à lista de saudações usadas
        saudacoes_usadas.append(primeira_linha)
        
        # Exibir a primeira linha
        print(f"Script {i+1}: {primeira_linha}")
    
    print("-" * 60)
    
    # Analisar a distribuição das saudações
    print("\nDistribuição das saudações:")
    
    saudacoes_contagem = {}
    for saudacao in saudacoes_usadas:
        if saudacao in saudacoes_contagem:
            saudacoes_contagem[saudacao] += 1
        else:
            saudacoes_contagem[saudacao] = 1
    
    for saudacao, contagem in sorted(saudacoes_contagem.items(), key=lambda x: x[1], reverse=True):
        porcentagem = (contagem / num_testes) * 100
        print(f"{saudacao}: {contagem} vezes ({porcentagem:.1f}%)")

def main():
    """
    Função principal.
    """
    # Testar as saudações variadas
    testar_saudacoes(20)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
