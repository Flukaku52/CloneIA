#!/usr/bin/env python3
"""
Script para testar o verificador de notícias com dados simulados.
"""
import os
import sys
import json
import logging
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_verificador_noticias')

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar o verificador de notícias
from core.verificador_noticias import VerificadorNoticias

# Notícias simuladas para teste
NOTICIAS_SIMULADAS = [
    # Grupo 1: Notícias sobre Bitcoin atingindo novo recorde
    {
        "titulo": "Bitcoin atinge novo recorde histórico de $100.000",
        "resumo": "O Bitcoin atingiu um novo recorde histórico, ultrapassando os $100.000 pela primeira vez na história.",
        "link": "https://portal1.com/bitcoin-recorde",
        "data": "12 de maio de 2025",
        "data_iso": "2025-05-12T10:00:00",
        "portal": "Portal 1",
        "credibilidade": 8,
        "confiavel": True,
        "razoes_credibilidade": []
    },
    {
        "titulo": "Bitcoin supera $100k pela primeira vez",
        "resumo": "A principal criptomoeda do mercado atingiu a marca histórica de $100.000 nesta segunda-feira.",
        "link": "https://portal2.com/bitcoin-100k",
        "data": "12 de maio de 2025",
        "data_iso": "2025-05-12T11:30:00",
        "portal": "Portal 2",
        "credibilidade": 7,
        "confiavel": True,
        "razoes_credibilidade": []
    },
    {
        "titulo": "Bitcoin quebra barreira dos $100.000 e estabelece novo ATH",
        "resumo": "O Bitcoin finalmente quebrou a barreira psicológica dos $100.000, estabelecendo um novo all-time high.",
        "link": "https://portal3.com/bitcoin-ath",
        "data": "12 de maio de 2025",
        "data_iso": "2025-05-12T09:45:00",
        "portal": "Portal 3",
        "credibilidade": 9,
        "confiavel": True,
        "razoes_credibilidade": []
    },

    # Grupo 2: Notícias sobre Ethereum seguindo Bitcoin
    {
        "titulo": "Ethereum segue os passos do Bitcoin e valoriza 15%",
        "resumo": "O Ethereum seguiu os passos do Bitcoin e valorizou 15% nas últimas 24 horas, atingindo $8.500.",
        "link": "https://portal1.com/ethereum-valoriza",
        "data": "12 de maio de 2025",
        "data_iso": "2025-05-12T14:00:00",
        "portal": "Portal 1",
        "credibilidade": 8,
        "confiavel": True,
        "razoes_credibilidade": []
    },
    {
        "titulo": "ETH sobe 15% após alta do BTC",
        "resumo": "O Ethereum (ETH) subiu 15% após a alta do Bitcoin, atingindo o valor de $8.500.",
        "link": "https://portal4.com/eth-sobe",
        "data": "12 de maio de 2025",
        "data_iso": "2025-05-12T15:20:00",
        "portal": "Portal 4",
        "credibilidade": 7,
        "confiavel": True,
        "razoes_credibilidade": []
    },
    {
        "titulo": "Ethereum valoriza 15% e atinge $8.500",
        "resumo": "A segunda maior criptomoeda do mercado valorizou 15% nas últimas 24 horas, atingindo o valor de $8.500.",
        "link": "https://portal3.com/ethereum-valoriza",
        "data": "12 de maio de 2025",
        "data_iso": "2025-05-12T14:30:00",
        "portal": "Portal 3",
        "credibilidade": 8,
        "confiavel": True,
        "razoes_credibilidade": []
    },

    # Grupo 3: Notícia única sobre Cardano
    {
        "titulo": "Cardano implementa nova atualização de rede",
        "resumo": "A blockchain Cardano implementou uma nova atualização de rede que promete melhorar a escalabilidade.",
        "link": "https://portal5.com/cardano-atualizacao",
        "data": "11 de maio de 2025",
        "data_iso": "2025-05-11T08:30:00",
        "portal": "Portal 5",
        "credibilidade": 6,
        "confiavel": True,
        "razoes_credibilidade": []
    },

    # Grupo 4: Notícias contraditórias sobre regulamentação
    {
        "titulo": "EUA aprova nova regulamentação favorável para criptomoedas",
        "resumo": "O governo dos EUA aprovou uma nova regulamentação que é considerada favorável para o mercado de criptomoedas.",
        "link": "https://portal2.com/eua-regulamentacao",
        "data": "10 de maio de 2025",
        "data_iso": "2025-05-10T16:45:00",
        "portal": "Portal 2",
        "credibilidade": 7,
        "confiavel": True,
        "razoes_credibilidade": []
    },
    {
        "titulo": "Nova regulamentação dos EUA impõe restrições ao mercado cripto",
        "resumo": "A nova regulamentação aprovada pelo governo dos EUA impõe várias restrições ao mercado de criptomoedas.",
        "link": "https://portal6.com/eua-restricoes",
        "data": "10 de maio de 2025",
        "data_iso": "2025-05-10T18:15:00",
        "portal": "Portal 6",
        "credibilidade": 6,
        "confiavel": True,
        "razoes_credibilidade": []
    },

    # Grupo 5: Notícia sensacionalista (baixa credibilidade)
    {
        "titulo": "BITCOIN VAI CHEGAR A $1 MILHÃO EM 2025!!!",
        "resumo": "Especialistas garantem que o Bitcoin vai chegar a $1 milhão até o final de 2025! Não perca essa oportunidade única!",
        "link": "https://portal-suspeito.com/bitcoin-1milhao",
        "data": "09 de maio de 2025",
        "data_iso": "2025-05-09T12:00:00",
        "portal": "Portal Suspeito",
        "credibilidade": 3,
        "confiavel": False,
        "razoes_credibilidade": ["Título sensacionalista", "Contém termos sensacionalistas"]
    }
]

def main():
    """
    Função principal para testar o verificador de notícias.
    """
    logger.info("Testando o verificador de notícias com dados simulados...")

    # Criar o verificador
    verificador = VerificadorNoticias(limiar_similaridade=0.4)

    # Verificar as notícias
    noticias_verificadas = verificador.verificar_noticias(NOTICIAS_SIMULADAS)

    # Exibir resultados
    print(f"\nResultados da verificação cruzada de {len(NOTICIAS_SIMULADAS)} notícias simuladas:\n")

    for i, noticia in enumerate(noticias_verificadas, 1):
        # Mostrar informações de credibilidade
        credibilidade_info = f"[Credibilidade: {noticia.get('credibilidade')}/10]"

        # Adicionar informações de cruzamento, se disponíveis
        cruzamento_info = ""
        if noticia.get('cruzamento'):
            num_fontes = noticia['cruzamento'].get('num_fontes', 1)
            confirmado = noticia['cruzamento'].get('confirmado', False)

            if confirmado:
                cruzamento_info = f" [✓ Confirmada por {num_fontes} fontes]"
            else:
                cruzamento_info = f" [Fonte única]"

            if noticia['cruzamento'].get('tem_contradicoes', False):
                cruzamento_info += " [⚠️ Contradições detectadas]"

        # Mostrar credibilidade original vs. atual, se houver diferença
        if noticia.get('credibilidade_original') and noticia.get('credibilidade_original') != noticia.get('credibilidade'):
            credibilidade_info = f"[Credibilidade: {noticia.get('credibilidade_original')}/10 → {noticia.get('credibilidade')}/10]"

        print(f"{i}. {noticia['titulo']} {credibilidade_info}{cruzamento_info}")
        print(f"   Portal: {noticia['portal']}")
        print(f"   Data: {noticia['data']}")

        if noticia.get('resumo'):
            print(f"   Resumo: {noticia['resumo']}")

        # Mostrar razões de credibilidade, se houver
        if noticia.get('razoes_credibilidade'):
            print(f"   Observações: {', '.join(noticia['razoes_credibilidade'])}")

        # Mostrar fontes que confirmam a notícia, se houver
        if noticia.get('cruzamento') and noticia['cruzamento'].get('fontes', []):
            fontes = noticia['cruzamento']['fontes']
            if len(fontes) > 1:  # Só mostrar se houver mais de uma fonte
                print(f"   Fontes que confirmam: {', '.join(fontes)}")

        print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
