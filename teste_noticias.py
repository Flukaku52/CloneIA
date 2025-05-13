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
            "titulo": "Carteira de Bitcoin para idosos é lançada com interface simplificada",
            "link": "https://exemplo.com/noticia1",
            "data": f"{datas[0].day} de {_nome_mes(datas[0].month)} de {datas[0].year}",
            "data_iso": datas[0].isoformat(),
            "resumo": "Uma nova carteira de Bitcoin foi lançada especificamente para idosos, com interface simplificada e recursos de segurança adicionais para facilitar o uso por pessoas com pouca experiência em tecnologia.",
            "portal": "CriptoFácil"
        },
        {
            "titulo": "Caixa Econômica lança curso gratuito de criptomoedas para clientes",
            "link": "https://exemplo.com/noticia2",
            "data": f"{datas[1].day} de {_nome_mes(datas[1].month)} de {datas[1].year}",
            "data_iso": datas[1].isoformat(),
            "resumo": "A Caixa Econômica Federal anunciou o lançamento de um curso gratuito sobre criptomoedas para todos os seus clientes, com o objetivo de educar os brasileiros sobre investimentos digitais de forma segura.",
            "portal": "Portal do Bitcoin"
        },
        {
            "titulo": "Supermercados começam a aceitar pagamentos em Bitcoin em todo o Brasil",
            "link": "https://exemplo.com/noticia3",
            "data": f"{datas[2].day} de {_nome_mes(datas[2].month)} de {datas[2].year}",
            "data_iso": datas[2].isoformat(),
            "resumo": "Uma das maiores redes de supermercados do Brasil anunciou que começará a aceitar Bitcoin como forma de pagamento em todas as suas lojas a partir do próximo mês, sem taxas adicionais para os consumidores.",
            "portal": "Livecoins"
        },
        {
            "titulo": "Aposentados descobrem Bitcoin: número de investidores acima de 60 anos cresce 300%",
            "link": "https://exemplo.com/noticia4",
            "data": f"{datas[3].day} de {_nome_mes(datas[3].month)} de {datas[3].year}",
            "data_iso": datas[3].isoformat(),
            "resumo": "Um estudo recente revelou que o número de aposentados investindo em Bitcoin cresceu 300% nos últimos seis meses, com muitos buscando proteger suas economias contra a inflação.",
            "portal": "Cointelegraph Brasil"
        },
        {
            "titulo": "Governo lança programa 'Meu Primeiro Bitcoin' para jovens de baixa renda",
            "link": "https://exemplo.com/noticia5",
            "data": f"{datas[0].day} de {_nome_mes(datas[0].month)} de {datas[0].year}",
            "data_iso": datas[0].isoformat(),
            "resumo": "O governo federal anunciou o programa 'Meu Primeiro Bitcoin', que oferecerá educação financeira e uma pequena quantia em Bitcoin para jovens de baixa renda, com o objetivo de promover inclusão financeira.",
            "portal": "Portal do Bitcoin"
        },
        {
            "titulo": "Como proteger suas criptomoedas: guia completo para iniciantes",
            "link": "https://exemplo.com/noticia6",
            "data": f"{datas[4].day} de {_nome_mes(datas[4].month)} de {datas[4].year}",
            "data_iso": datas[4].isoformat(),
            "resumo": "Este guia explica de forma simples como proteger suas criptomoedas contra hackers e golpes, com dicas práticas que qualquer pessoa pode seguir, mesmo sem conhecimentos técnicos avançados.",
            "portal": "CriptoFácil"
        },
        {
            "titulo": "Bitcoin atinge US$ 125.000 após grandes empresas anunciarem novas compras",
            "link": "https://exemplo.com/noticia7",
            "data": f"{datas[1].day} de {_nome_mes(datas[1].month)} de {datas[1].year}",
            "data_iso": datas[1].isoformat(),
            "resumo": "O preço do Bitcoin ultrapassou US$ 125.000 após várias grandes empresas anunciarem novas compras da criptomoeda para suas reservas corporativas, estabelecendo um novo recorde histórico.",
            "portal": "Cointelegraph Brasil"
        },
        {
            "titulo": "Alerta: novo golpe no WhatsApp promete dobrar investimentos em Bitcoin",
            "link": "https://exemplo.com/noticia8",
            "data": f"{datas[0].day} de {_nome_mes(datas[0].month)} de {datas[0].year}",
            "data_iso": datas[0].isoformat(),
            "resumo": "A Polícia Federal alerta para um novo golpe que circula pelo WhatsApp prometendo dobrar investimentos em Bitcoin em 24 horas. Saiba como identificar e se proteger desta fraude que já fez milhares de vítimas.",
            "portal": "Livecoins"
        },
        {
            "titulo": "Escolas públicas incluirão educação sobre Bitcoin e criptomoedas no currículo",
            "link": "https://exemplo.com/noticia9",
            "data": f"{datas[2].day} de {_nome_mes(datas[2].month)} de {datas[2].year}",
            "data_iso": datas[2].isoformat(),
            "resumo": "O Ministério da Educação anunciou que escolas públicas de todo o país incluirão noções básicas sobre Bitcoin e criptomoedas no currículo de educação financeira a partir do próximo ano letivo.",
            "portal": "Portal do Bitcoin"
        },
        {
            "titulo": "Comprei R$ 100 em Bitcoin há 5 anos: quanto vale hoje e o que aprendi",
            "link": "https://exemplo.com/noticia10",
            "data": f"{datas[3].day} de {_nome_mes(datas[3].month)} de {datas[3].year}",
            "data_iso": datas[3].isoformat(),
            "resumo": "Um investidor brasileiro compartilha sua experiência após investir apenas R$ 100 em Bitcoin há 5 anos, mostrando quanto vale hoje seu investimento e as lições que aprendeu durante essa jornada.",
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
            "text": "Minha avó de 78 anos acabou de comprar seu primeiro Bitcoin usando a nova carteira para idosos! Ela disse que é mais fácil que usar o caixa eletrônico do banco 😂 #BitcoinParaTodos",
            "created_at": datas[0].isoformat(),
            "author_username": "neto_digital",
            "likes": 3520,
            "retweets": 1245,
            "url": "https://twitter.com/neto_digital/status/123456789"
        },
        {
            "id": "tweet2",
            "text": "ATENÇÃO: Estão circulando mensagens no WhatsApp prometendo dobrar seu Bitcoin em 24h. É GOLPE! Ninguém consegue garantir retornos assim. Sempre desconfie de promessas milagrosas.",
            "created_at": datas[1].isoformat(),
            "author_username": "seguranca_cripto",
            "likes": 4950,
            "retweets": 2480,
            "url": "https://twitter.com/seguranca_cripto/status/123456790"
        },
        {
            "id": "tweet3",
            "text": "Dica para quem está começando: você não precisa comprar 1 Bitcoin inteiro! Pode começar com R$50 ou R$100. É como comprar meio quilo de arroz em vez do pacote inteiro.",
            "created_at": datas[2].isoformat(),
            "author_username": "cripto_educador",
            "likes": 5220,
            "retweets": 2630,
            "url": "https://twitter.com/cripto_educador/status/123456791"
        },
        {
            "id": "tweet4",
            "text": "Fiz o curso gratuito de criptomoedas da Caixa e recomendo muito! Explicação bem simples, sem termos complicados. Perfeito para quem não entende nada do assunto.",
            "created_at": datas[3].isoformat(),
            "author_username": "maria_investidora",
            "likes": 2495,
            "retweets": 1232,
            "url": "https://twitter.com/maria_investidora/status/123456792"
        },
        {
            "id": "tweet5",
            "text": "Comprei um pão de queijo no supermercado pagando com Bitcoin! Processo super rápido, só escaneei o QR code e pronto. O futuro chegou e tem gosto de queijo 🧀 #BitcoinNoDiaADia",
            "created_at": datas[4].isoformat(),
            "author_username": "vida_cripto",
            "likes": 3780,
            "retweets": 1920,
            "url": "https://twitter.com/vida_cripto/status/123456793"
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
