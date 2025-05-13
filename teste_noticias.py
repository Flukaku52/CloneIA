#!/usr/bin/env python3
"""
Script para testar a geração de scripts para a Rapidinha sem gerar áudios ou vídeos.
"""
import os
import sys
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('teste_noticias')

# Simular notícias para teste
def gerar_noticias_teste():
    """
    Gera notícias de teste para simular o que seria buscado online.
    
    Returns:
        list: Lista de notícias simuladas
    """
    return [
        {
            "titulo": "Bitcoin ultrapassa US$ 60.000 pela primeira vez em 2023",
            "link": "https://exemplo.com/noticia1",
            "data": "15 de novembro de 2023",
            "data_iso": "2023-11-15T10:30:00",
            "resumo": "O Bitcoin superou a marca de US$ 60.000 pela primeira vez este ano, impulsionado pela aprovação de ETFs e maior adoção institucional.",
            "portal": "CriptoFácil"
        },
        {
            "titulo": "Nubank expande carteira de Bitcoin para todos os clientes no Brasil",
            "link": "https://exemplo.com/noticia2",
            "data": "10 de novembro de 2023",
            "data_iso": "2023-11-10T14:20:00",
            "resumo": "O Nubank anunciou que todos os seus clientes no Brasil já podem comprar e vender Bitcoin diretamente pelo aplicativo, com taxas reduzidas.",
            "portal": "Portal do Bitcoin"
        },
        {
            "titulo": "Cidade brasileira começa a aceitar Bitcoin para pagamento de impostos",
            "link": "https://exemplo.com/noticia3",
            "data": "12 de novembro de 2023",
            "data_iso": "2023-11-12T09:15:00",
            "resumo": "Uma cidade no interior de São Paulo se tornou a primeira no Brasil a aceitar Bitcoin como forma de pagamento para impostos municipais.",
            "portal": "Livecoins"
        },
        {
            "titulo": "Entenda o que é staking e como ganhar renda passiva com criptomoedas",
            "link": "https://exemplo.com/noticia4",
            "data": "8 de novembro de 2023",
            "data_iso": "2023-11-08T16:45:00",
            "resumo": "O staking é uma forma de ganhar recompensas ao manter suas criptomoedas bloqueadas para ajudar a validar transações na rede blockchain.",
            "portal": "Cointelegraph Brasil"
        },
        {
            "titulo": "Banco Central anuncia testes com o Real Digital para 2024",
            "link": "https://exemplo.com/noticia5",
            "data": "14 de novembro de 2023",
            "data_iso": "2023-11-14T11:30:00",
            "resumo": "O Banco Central do Brasil anunciou que iniciará testes com o Real Digital, a CBDC brasileira, no primeiro trimestre de 2024.",
            "portal": "Portal do Bitcoin"
        },
        {
            "titulo": "Como comprar Bitcoin pela primeira vez: guia completo para iniciantes",
            "link": "https://exemplo.com/noticia6",
            "data": "7 de novembro de 2023",
            "data_iso": "2023-11-07T10:00:00",
            "resumo": "Este guia explica passo a passo como comprar Bitcoin pela primeira vez, desde a escolha da corretora até a segurança da carteira.",
            "portal": "CriptoFácil"
        },
        {
            "titulo": "Ethereum completa atualização que reduz taxas de transação",
            "link": "https://exemplo.com/noticia7",
            "data": "13 de novembro de 2023",
            "data_iso": "2023-11-13T15:20:00",
            "resumo": "A rede Ethereum completou uma atualização importante que promete reduzir significativamente as taxas de transação (gas fees).",
            "portal": "Cointelegraph Brasil"
        },
        {
            "titulo": "Golpes com criptomoedas aumentam 40% em 2023; saiba como se proteger",
            "link": "https://exemplo.com/noticia8",
            "data": "9 de novembro de 2023",
            "data_iso": "2023-11-09T13:10:00",
            "resumo": "Um relatório recente mostra que golpes envolvendo criptomoedas aumentaram 40% em 2023. Especialistas dão dicas de como se proteger.",
            "portal": "Livecoins"
        },
        {
            "titulo": "Mercado Pago lança compra e venda de Bitcoin no Brasil",
            "link": "https://exemplo.com/noticia9",
            "data": "11 de novembro de 2023",
            "data_iso": "2023-11-11T09:45:00",
            "resumo": "O Mercado Pago anunciou o lançamento de serviços de compra e venda de Bitcoin diretamente pelo aplicativo para todos os usuários no Brasil.",
            "portal": "Portal do Bitcoin"
        },
        {
            "titulo": "O que é DeFi? Entenda as finanças descentralizadas de forma simples",
            "link": "https://exemplo.com/noticia10",
            "data": "6 de novembro de 2023",
            "data_iso": "2023-11-06T14:30:00",
            "resumo": "DeFi, ou Finanças Descentralizadas, são protocolos financeiros construídos em blockchains que permitem empréstimos, trocas e investimentos sem intermediários.",
            "portal": "CriptoFácil"
        }
    ]

# Simular tweets para teste
def gerar_tweets_teste():
    """
    Gera tweets de teste para simular o que seria buscado online.
    
    Returns:
        list: Lista de tweets simulados
    """
    return [
        {
            "id": "tweet1",
            "text": "Acabei de comprar meu primeiro Bitcoin! Processo super simples pela @binance. Recomendo para quem quer começar no mundo cripto!",
            "created_at": "2023-11-15T08:30:00",
            "author_username": "usuario_cripto",
            "likes": 120,
            "retweets": 45,
            "url": "https://twitter.com/usuario_cripto/status/123456789"
        },
        {
            "id": "tweet2",
            "text": "O Bitcoin está em alta hoje! Já ultrapassou os US$ 60.000 e parece que vai continuar subindo. Quem comprou no fundo de 2022 está comemorando!",
            "created_at": "2023-11-15T09:15:00",
            "author_username": "analista_bitcoin",
            "likes": 350,
            "retweets": 180,
            "url": "https://twitter.com/analista_bitcoin/status/123456790"
        },
        {
            "id": "tweet3",
            "text": "Dica para iniciantes: nunca invista em cripto mais do que você pode perder. Comece com valores pequenos e vá aprendendo aos poucos.",
            "created_at": "2023-11-14T16:45:00",
            "author_username": "cripto_educador",
            "likes": 520,
            "retweets": 230,
            "url": "https://twitter.com/cripto_educador/status/123456791"
        },
        {
            "id": "tweet4",
            "text": "O staking de Ethereum está rendendo cerca de 4% ao ano. É uma ótima forma de ganhar renda passiva enquanto segura seus ETH.",
            "created_at": "2023-11-14T11:20:00",
            "author_username": "eth_brasil",
            "likes": 95,
            "retweets": 32,
            "url": "https://twitter.com/eth_brasil/status/123456792"
        },
        {
            "id": "tweet5",
            "text": "O Nubank acaba de liberar a compra de Bitcoin para todos os clientes! Testei e é super fácil de usar. Ótimo para quem está começando.",
            "created_at": "2023-11-13T14:10:00",
            "author_username": "tech_influencer",
            "likes": 780,
            "retweets": 320,
            "url": "https://twitter.com/tech_influencer/status/123456793"
        }
    ]

def testar_geracao_script():
    """
    Testa a geração de scripts para a Rapidinha usando notícias e tweets simulados.
    """
    try:
        # Importar o gerador de scripts
        from gerador_script_rapidinha import GeradorScriptRapidinha
        
        # Criar o gerador
        gerador = GeradorScriptRapidinha()
        
        # Substituir os métodos de busca por versões que retornam dados simulados
        gerador.noticias_scraper.buscar_todas_noticias = lambda *args, **kwargs: gerar_noticias_teste()
        gerador.twitter_scraper.buscar_tweets_por_termos = lambda *args, **kwargs: gerar_tweets_teste()[:3]
        gerador.twitter_scraper.buscar_tweets_por_contas = lambda *args, **kwargs: gerar_tweets_teste()[3:]
        
        # Gerar o script
        script = gerador.gerar_script(num_noticias=5, num_tweets=2)
        
        # Exibir o script
        print("\n" + "="*50)
        print("SCRIPT GERADO PARA A RAPIDINHA (SIMULAÇÃO)")
        print("="*50 + "\n")
        print(script)
        print("\n" + "="*50)
        
        # Salvar o script
        data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"teste_rapidinha_{data_hora}.txt"
        caminho_script = os.path.join("output", "scripts", nome_arquivo)
        
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(caminho_script), exist_ok=True)
        
        with open(caminho_script, 'w', encoding='utf-8') as f:
            f.write(script)
        
        print(f"\nScript salvo em: {caminho_script}")
        
        return 0
    except Exception as e:
        logger.error(f"Erro ao testar geração de script: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(testar_geracao_script())
