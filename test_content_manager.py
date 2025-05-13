#!/usr/bin/env python3
"""
Script para testar o gerenciador de conteúdo.
"""
import os
import sys
import argparse
import logging
from typing import Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_content_manager')

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar o gerenciador de conteúdo
try:
    from core.content_manager import ContentManager
except ImportError:
    logger.error("Módulo content_manager não encontrado. Verifique se o arquivo existe em core/content_manager.py")
    sys.exit(1)

# Exemplo de conteúdo para teste
EXEMPLO_TITULO = "Notícia Cripto: Bitcoin atinge novo recorde histórico"
EXEMPLO_CONTEUDO = """
O Bitcoin acaba de atingir um novo recorde histórico, ultrapassando os $100.000 pela primeira vez.
Esta marca representa um momento significativo para a criptomoeda mais valiosa do mundo.

Analistas atribuem esta alta a vários fatores:
1. Aumento da adoção institucional
2. Redução da inflação global
3. Crescente interesse de investidores de varejo
4. Reconhecimento como reserva de valor

O movimento começou após grandes empresas anunciarem novas compras de Bitcoin para suas reservas corporativas.
Além disso, a recente aprovação de novos ETFs de Bitcoin nos Estados Unidos trouxe mais liquidez ao mercado.

Especialistas do mercado estão divididos sobre o futuro próximo. Alguns acreditam que veremos uma correção,
enquanto outros preveem que este é apenas o começo de um novo ciclo de alta que pode levar o Bitcoin a patamares ainda maiores.

O que é certo é que a volatilidade deve continuar, como é característico do mercado de criptomoedas.
"""

def exibir_info_script(info: Dict[str, Any]) -> None:
    """
    Exibe informações sobre o script.

    Args:
        info: Dicionário com informações do script
    """
    print("\nInformações do Script:")
    print(f"Número de palavras: {info['num_palavras']} (limite: {info['limite_palavras']})")

    duracao_min = info['duracao_estimada_segundos'] // 60
    duracao_seg = info['duracao_estimada_segundos'] % 60

    duracao_max_min = info['duracao_maxima_segundos'] // 60
    duracao_max_seg = info['duracao_maxima_segundos'] % 60

    print(f"Duração estimada: {duracao_min:.0f}m {duracao_seg:.0f}s (máximo: {duracao_max_min:.0f}m {duracao_max_seg:.0f}s)")

    status = "✅ Dentro do limite" if info['dentro_limite'] else "❌ Excede o limite"
    print(f"Status: {status}")

def main():
    """
    Função principal para testar o gerenciador de conteúdo.
    """
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Teste do gerenciador de conteúdo")
    parser.add_argument("--titulo", type=str, default=EXEMPLO_TITULO, help="Título do vídeo")
    parser.add_argument("--conteudo", type=str, default=EXEMPLO_CONTEUDO, help="Conteúdo principal do vídeo")
    parser.add_argument("--config", type=str, default="config/content_params.json", help="Caminho para o arquivo de configuração")

    args = parser.parse_args()

    logger.info("Testando o gerenciador de conteúdo...")

    # Criar o gerenciador de conteúdo
    manager = ContentManager(config_path=args.config)

    # Formatar o script
    script = manager.format_script(args.titulo, args.conteudo)

    # Validar o script
    valido, info = manager.validate_script_length(script)

    # Verificar palavras proibidas
    palavras_proibidas = manager.check_forbidden_words(script)

    # Exibir resultados
    print("\n" + "="*80)
    print(f"SCRIPT FORMATADO PARA RAPIDINHA (Saudação: '{manager.saudacao_padrao}')")
    print("="*80)
    print(script)
    print("="*80)

    # Exibir informações
    exibir_info_script(info)

    # Exibir aviso sobre palavras proibidas
    if palavras_proibidas:
        print(f"\n⚠️ ATENÇÃO: Script contém palavras proibidas: {', '.join(palavras_proibidas)}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
