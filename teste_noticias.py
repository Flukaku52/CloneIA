#!/usr/bin/env python3
"""
Script para testar a geração de scripts para a Rapidinha sem gerar áudios ou vídeos.
"""
import os
import sys
import logging
from datetime import datetime, timedelta

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
    Usa a data atual (12/05/2025) e gera notícias da última semana.

    Returns:
        list: Lista de notícias simuladas
    """
    # Data atual: 12/05/2025
    data_atual = datetime(2025, 5, 12)

    # Gerar datas da última semana
    datas = []
    for i in range(7):
        data = data_atual - timedelta(days=i)
        datas.append(data)

    return [
        {
            "titulo": "Bitcoin ultrapassa US$ 120.000 e atinge novo recorde histórico",
            "link": "https://exemplo.com/noticia1",
            "data": f"{datas[0].day} de {_nome_mes(datas[0].month)} de {datas[0].year}",
            "data_iso": datas[0].isoformat(),
            "resumo": "O Bitcoin superou a marca de US$ 120.000 pela primeira vez na história, impulsionado pela crescente adoção institucional e redução da oferta após o halving de 2024.",
            "portal": "CriptoFácil"
        },
        {
            "titulo": "Banco do Brasil lança plataforma de investimentos em criptomoedas para todos os clientes",
            "link": "https://exemplo.com/noticia2",
            "data": f"{datas[1].day} de {_nome_mes(datas[1].month)} de {datas[1].year}",
            "data_iso": datas[1].isoformat(),
            "resumo": "O Banco do Brasil anunciou que todos os seus clientes já podem investir em Bitcoin e outras criptomoedas diretamente pelo aplicativo do banco, com taxas reduzidas.",
            "portal": "Portal do Bitcoin"
        },
        {
            "titulo": "Mais de 50 cidades brasileiras já aceitam Bitcoin para pagamento de impostos",
            "link": "https://exemplo.com/noticia3",
            "data": f"{datas[2].day} de {_nome_mes(datas[2].month)} de {datas[2].year}",
            "data_iso": datas[2].isoformat(),
            "resumo": "Um levantamento recente mostra que mais de 50 cidades brasileiras já aceitam Bitcoin como forma de pagamento para impostos municipais, seguindo a tendência global de adoção de criptomoedas.",
            "portal": "Livecoins"
        },
        {
            "titulo": "Guia completo: como ganhar renda passiva com staking de criptomoedas em 2025",
            "link": "https://exemplo.com/noticia4",
            "data": f"{datas[3].day} de {_nome_mes(datas[3].month)} de {datas[3].year}",
            "data_iso": datas[3].isoformat(),
            "resumo": "Confira neste guia atualizado como fazer staking de criptomoedas em 2025 e ganhar rendimentos passivos que podem chegar a 15% ao ano, dependendo da moeda escolhida.",
            "portal": "Cointelegraph Brasil"
        },
        {
            "titulo": "Real Digital entra em operação oficial no Brasil após fase de testes",
            "link": "https://exemplo.com/noticia5",
            "data": f"{datas[2].day} de {_nome_mes(datas[2].month)} de {datas[2].year}",
            "data_iso": datas[2].isoformat(),
            "resumo": "O Banco Central do Brasil anunciou o lançamento oficial do Real Digital, a moeda digital do país, após dois anos de testes bem-sucedidos com instituições financeiras.",
            "portal": "Portal do Bitcoin"
        },
        {
            "titulo": "Bitcoin para iniciantes: como comprar sua primeira criptomoeda em 2025",
            "link": "https://exemplo.com/noticia6",
            "data": f"{datas[4].day} de {_nome_mes(datas[4].month)} de {datas[4].year}",
            "data_iso": datas[4].isoformat(),
            "resumo": "Este guia atualizado explica passo a passo como comprar Bitcoin pela primeira vez em 2025, com as melhores plataformas disponíveis no Brasil e dicas de segurança.",
            "portal": "CriptoFácil"
        },
        {
            "titulo": "Ethereum 3.0 é lançado com melhorias significativas de velocidade e eficiência",
            "link": "https://exemplo.com/noticia7",
            "data": f"{datas[1].day} de {_nome_mes(datas[1].month)} de {datas[1].year}",
            "data_iso": datas[1].isoformat(),
            "resumo": "A rede Ethereum completou sua atualização para a versão 3.0, trazendo melhorias que aumentam a velocidade das transações em até 10 vezes e reduzem as taxas em mais de 90%.",
            "portal": "Cointelegraph Brasil"
        },
        {
            "titulo": "Novo golpe com criptomoedas atinge milhares de brasileiros; saiba como se proteger",
            "link": "https://exemplo.com/noticia8",
            "data": f"{datas[0].day} de {_nome_mes(datas[0].month)} de {datas[0].year}",
            "data_iso": datas[0].isoformat(),
            "resumo": "Um novo esquema de fraude envolvendo falsos investimentos em criptomoedas já afetou mais de 10 mil brasileiros em 2025. Especialistas explicam como identificar e evitar cair nesse tipo de golpe.",
            "portal": "Livecoins"
        },
        {
            "titulo": "Pix agora permite transferências instantâneas usando Bitcoin e outras criptomoedas",
            "link": "https://exemplo.com/noticia9",
            "data": f"{datas[3].day} de {_nome_mes(datas[3].month)} de {datas[3].year}",
            "data_iso": datas[3].isoformat(),
            "resumo": "O Banco Central atualizou o sistema Pix para permitir transferências usando Bitcoin e outras criptomoedas, com conversão automática para reais no momento da transação.",
            "portal": "Portal do Bitcoin"
        },
        {
            "titulo": "NFTs em 2025: o que mudou e como investir nesse mercado renovado",
            "link": "https://exemplo.com/noticia10",
            "data": f"{datas[5].day} de {_nome_mes(datas[5].month)} de {datas[5].year}",
            "data_iso": datas[5].isoformat(),
            "resumo": "O mercado de NFTs passou por grandes transformações desde 2021 e agora oferece novas oportunidades de investimento, principalmente em setores como imóveis digitais e licenciamento de conteúdo.",
            "portal": "CriptoFácil"
        }
    ]

# Função auxiliar para obter o nome do mês
def _nome_mes(mes: int) -> str:
    """
    Retorna o nome do mês em português.

    Args:
        mes: Número do mês (1-12)

    Returns:
        str: Nome do mês em português
    """
    meses = [
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
    ]
    return meses[mes - 1] if 1 <= mes <= 12 else ""

# Simular tweets para teste
def gerar_tweets_teste():
    """
    Gera tweets de teste para simular o que seria buscado online.
    Usa a data atual (12/05/2025) e gera tweets da última semana.

    Returns:
        list: Lista de tweets simulados
    """
    # Data atual: 12/05/2025
    data_atual = datetime(2025, 5, 12)

    # Gerar datas da última semana
    datas = []
    for i in range(5):  # 5 tweets nos últimos 5 dias
        data = data_atual - timedelta(days=i)
        hora = 8 + i * 2  # Horas diferentes para cada tweet
        data = data.replace(hour=hora, minute=30)
        datas.append(data)

    return [
        {
            "id": "tweet1",
            "text": "Acabei de comprar mais Bitcoin a US$ 120K! Mesmo com o preço alto, acredito que ainda vai valorizar muito mais até o fim de 2025. #Bitcoin #Investimentos",
            "created_at": datas[0].isoformat(),
            "author_username": "usuario_cripto",
            "likes": 520,
            "retweets": 145,
            "url": "https://twitter.com/usuario_cripto/status/123456789"
        },
        {
            "id": "tweet2",
            "text": "O Bitcoin está em alta histórica! Já ultrapassou os US$ 120.000 e parece que vai continuar subindo. Quem comprou após o halving de 2024 já dobrou o investimento!",
            "created_at": datas[1].isoformat(),
            "author_username": "analista_bitcoin",
            "likes": 950,
            "retweets": 480,
            "url": "https://twitter.com/analista_bitcoin/status/123456790"
        },
        {
            "id": "tweet3",
            "text": "Dica para iniciantes em 2025: mesmo com Bitcoin em alta, nunca invista mais do que você pode perder. Comece com valores pequenos e vá aprendendo aos poucos.",
            "created_at": datas[2].isoformat(),
            "author_username": "cripto_educador",
            "likes": 1220,
            "retweets": 630,
            "url": "https://twitter.com/cripto_educador/status/123456791"
        },
        {
            "id": "tweet4",
            "text": "O staking de Ethereum 3.0 está rendendo cerca de 8% ao ano em 2025. É uma ótima forma de ganhar renda passiva enquanto segura seus ETH.",
            "created_at": datas[3].isoformat(),
            "author_username": "eth_brasil",
            "likes": 495,
            "retweets": 232,
            "url": "https://twitter.com/eth_brasil/status/123456792"
        },
        {
            "id": "tweet5",
            "text": "O Banco do Brasil acaba de lançar sua plataforma de investimentos em cripto! Testei e é super fácil de usar. Ótimo para quem está começando no mundo das criptomoedas.",
            "created_at": datas[4].isoformat(),
            "author_username": "tech_influencer",
            "likes": 1780,
            "retweets": 920,
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
