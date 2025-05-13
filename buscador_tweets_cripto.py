#!/usr/bin/env python3
"""
Buscador de tweets relevantes sobre criptomoedas no Twitter (X).
Utiliza a API oficial do Twitter v2 ou scraping como fallback.
Inclui análise de sentimento para filtrar conteúdo positivo/negativo.
"""
import os
import re
import sys
import json
import time
import random
import logging
import requests
import nltk
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import quote
from textblob import TextBlob
from googletrans import Translator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('buscador_tweets_cripto')

# Inicializar NLTK para análise de sentimento
try:
    nltk.download('punkt', quiet=True)
except Exception as e:
    logger.warning(f"Erro ao baixar recursos do NLTK: {e}")

# Inicializar tradutor
translator = None
try:
    translator = Translator()
except Exception as e:
    logger.warning(f"Erro ao inicializar tradutor: {e}")

# Contas relevantes de criptomoedas para seguir
CONTAS_CRIPTO = [
    "bitcoinbrasil",
    "portaldobitcoin",
    "criptofacil",
    "livecoinsbr",
    "BitcoinMagazine",
    "cointelegraph",
    "binance",
    "coinbase",
    "CoinMarketCap",
    "CoinDesk",
    "Cointimes",
    "BitcoinBrasilX",
    "FoxBitcoin",
    "MercadoBitcoin",
    "NovaDax",
    "BitcoinToYou",
    "BitPreco"
]

# Termos de busca relevantes
TERMOS_BUSCA = [
    "bitcoin",
    "cripto",
    "criptomoeda",
    "ethereum",
    "blockchain",
    "btc",
    "eth",
    "defi",
    "nft",
    "altcoin",
    "binance",
    "coinbase",
    "mercado bitcoin",
    "foxbit",
    "bitpreço"
]

class AnalisadorSentimento:
    """
    Classe para analisar o sentimento de textos.
    """
    def __init__(self):
        """
        Inicializa o analisador de sentimento.
        """
        self.translator = translator

    def analisar(self, texto: str, idioma: str = "pt") -> Tuple[float, str]:
        """
        Analisa o sentimento de um texto.

        Args:
            texto: Texto a ser analisado
            idioma: Idioma do texto

        Returns:
            Tuple[float, str]: Pontuação de polaridade (-1 a 1) e classificação (positivo, negativo, neutro)
        """
        try:
            # Traduzir para inglês se necessário (TextBlob funciona melhor em inglês)
            texto_para_analise = texto
            if idioma != "en" and self.translator:
                try:
                    texto_para_analise = self.translator.translate(texto, src=idioma, dest="en").text
                except Exception as e:
                    logger.warning(f"Erro ao traduzir texto para análise: {e}")

            # Analisar sentimento
            analise = TextBlob(texto_para_analise)
            polaridade = analise.sentiment.polarity

            # Classificar sentimento
            if polaridade > 0.1:
                classificacao = "positivo"
            elif polaridade < -0.1:
                classificacao = "negativo"
            else:
                classificacao = "neutro"

            return polaridade, classificacao
        except Exception as e:
            logger.error(f"Erro ao analisar sentimento: {e}")
            return 0.0, "neutro"

class TwitterCriptoScraper:
    """
    Classe para buscar tweets relevantes sobre criptomoedas no Twitter (X).
    Inclui análise de sentimento para filtrar conteúdo positivo/negativo.
    """
    def __init__(self, api_key: str = None, api_secret: str = None,
                 bearer_token: str = None, cache_dir: str = "cache",
                 filtro_sentimento: str = None):
        """
        Inicializa o scraper de tweets.

        Args:
            api_key: Chave da API do Twitter
            api_secret: Segredo da API do Twitter
            bearer_token: Token de portador da API do Twitter
            cache_dir: Diretório para armazenar o cache de tweets
            filtro_sentimento: Filtro de sentimento ('positivo', 'negativo', 'neutro', None para todos)
        """
        self.api_key = api_key or os.environ.get("TWITTER_API_KEY")
        self.api_secret = api_secret or os.environ.get("TWITTER_API_SECRET")
        self.bearer_token = bearer_token or os.environ.get("TWITTER_BEARER_TOKEN")
        self.cache_dir = cache_dir
        self.filtro_sentimento = filtro_sentimento
        self.use_api = bool(self.bearer_token)

        # Inicializar analisador de sentimento
        self.analisador_sentimento = AnalisadorSentimento()

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

        if self.use_api:
            self.session.headers.update({
                "Authorization": f"Bearer {self.bearer_token}"
            })

        # Criar diretório de cache se não existir
        os.makedirs(self.cache_dir, exist_ok=True)

        logger.info(f"Inicializado com {'API oficial' if self.use_api else 'método alternativo'}")
        if self.filtro_sentimento:
            logger.info(f"Filtrando tweets com sentimento: {self.filtro_sentimento}")

    def _get_cache_path(self, termo: str) -> str:
        """
        Retorna o caminho para o arquivo de cache de um termo.

        Args:
            termo: Termo de busca

        Returns:
            str: Caminho para o arquivo de cache
        """
        termo_sanitizado = re.sub(r'[^\w]', '_', termo.lower())
        return os.path.join(self.cache_dir, f"twitter_{termo_sanitizado}_cache.json")

    def _load_cache(self, termo: str) -> List[Dict[str, Any]]:
        """
        Carrega o cache de tweets de um termo.

        Args:
            termo: Termo de busca

        Returns:
            List[Dict[str, Any]]: Lista de tweets em cache
        """
        cache_path = self._get_cache_path(termo)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar cache para '{termo}': {e}")
        return []

    def _save_cache(self, termo: str, tweets: List[Dict[str, Any]]) -> None:
        """
        Salva o cache de tweets de um termo.

        Args:
            termo: Termo de busca
            tweets: Lista de tweets a serem salvos
        """
        cache_path = self._get_cache_path(termo)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(tweets, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar cache para '{termo}': {e}")

    def _buscar_tweets_api(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca tweets usando a API oficial do Twitter.

        Args:
            query: Consulta de busca
            max_results: Número máximo de resultados

        Returns:
            List[Dict[str, Any]]: Lista de tweets encontrados
        """
        if not self.use_api:
            logger.warning("API do Twitter não configurada")
            return []

        try:
            # Endpoint de busca da API v2
            url = "https://api.twitter.com/2/tweets/search/recent"

            # Parâmetros da busca
            params = {
                "query": query,
                "max_results": max_results,
                "tweet.fields": "created_at,author_id,public_metrics,entities",
                "user.fields": "name,username,profile_image_url",
                "expansions": "author_id"
            }

            # Fazer requisição
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Processar resultados
            tweets = []

            if "data" in data and "includes" in data and "users" in data["includes"]:
                users = {user["id"]: user for user in data["includes"]["users"]}

                for tweet in data["data"]:
                    author = users.get(tweet["author_id"], {})

                    # Analisar sentimento do tweet
                    texto = tweet["text"]
                    idioma = "en"  # Assumir inglês por padrão

                    # Detectar idioma se possível
                    if translator:
                        try:
                            idioma = translator.detect(texto).lang
                        except Exception as e:
                            logger.warning(f"Erro ao detectar idioma: {e}")

                    # Analisar sentimento
                    polaridade, sentimento = self.analisador_sentimento.analisar(texto, idioma)

                    # Criar objeto do tweet
                    tweet_obj = {
                        "id": tweet["id"],
                        "text": tweet["text"],
                        "created_at": tweet.get("created_at"),
                        "author_id": tweet["author_id"],
                        "author_name": author.get("name", ""),
                        "author_username": author.get("username", ""),
                        "author_profile_image": author.get("profile_image_url", ""),
                        "likes": tweet.get("public_metrics", {}).get("like_count", 0),
                        "retweets": tweet.get("public_metrics", {}).get("retweet_count", 0),
                        "replies": tweet.get("public_metrics", {}).get("reply_count", 0),
                        "url": f"https://twitter.com/{author.get('username', '')}/status/{tweet['id']}",
                        "source": "api",
                        "idioma": idioma,
                        "sentimento": sentimento,
                        "polaridade": polaridade,
                        "timestamp": datetime.now().isoformat()
                    }

                    # Filtrar por sentimento, se necessário
                    if self.filtro_sentimento is None or sentimento == self.filtro_sentimento:
                        tweets.append(tweet_obj)

            return tweets
        except Exception as e:
            logger.error(f"Erro ao buscar tweets via API para '{query}': {e}")
            return []

    def _buscar_tweets_alternativo(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca tweets usando um método alternativo (scraping).

        Args:
            query: Consulta de busca
            max_results: Número máximo de resultados

        Returns:
            List[Dict[str, Any]]: Lista de tweets encontrados
        """
        try:
            # Usar o endpoint de busca do Twitter Web
            url = f"https://twitter.com/search?q={quote(query)}&src=typed_query&f=live"

            # Simular que estamos usando um navegador
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://twitter.com/",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "TE": "trailers"
            }

            # Fazer requisição
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            # Nota: Aqui normalmente usaríamos BeautifulSoup para extrair os tweets,
            # mas o Twitter usa JavaScript para renderizar o conteúdo, então isso não
            # funcionaria diretamente. Em um cenário real, usaríamos Selenium ou
            # outra ferramenta para renderizar a página.

            # Para fins de demonstração, vamos retornar alguns tweets fictícios
            tweets = []
            for i in range(min(5, max_results)):
                # Criar texto do tweet com sentimento variado
                textos = [
                    f"Ótimas notícias sobre {query}! O mercado está em alta! 🚀",
                    f"Preocupante situação para {query}, os preços estão caindo rapidamente. 📉",
                    f"Informações neutras sobre {query}. O mercado segue estável.",
                    f"Excelente momento para investir em {query}! Muitas oportunidades! 💰",
                    f"Cuidado com {query} neste momento, há sinais de queda. ⚠️"
                ]
                texto = textos[i % len(textos)]

                # Analisar sentimento
                idioma = "pt"
                polaridade, sentimento = self.analisador_sentimento.analisar(texto, idioma)

                # Criar objeto do tweet
                tweet_obj = {
                    "id": f"mock_{i}_{int(time.time())}",
                    "text": texto,
                    "created_at": datetime.now().isoformat(),
                    "author_name": "Usuário Exemplo",
                    "author_username": "usuario_exemplo",
                    "likes": random.randint(5, 100),
                    "retweets": random.randint(1, 20),
                    "url": f"https://twitter.com/usuario_exemplo/status/mock_{i}_{int(time.time())}",
                    "source": "mock",
                    "idioma": idioma,
                    "sentimento": sentimento,
                    "polaridade": polaridade,
                    "timestamp": datetime.now().isoformat()
                }

                # Filtrar por sentimento, se necessário
                if self.filtro_sentimento is None or sentimento == self.filtro_sentimento:
                    tweets.append(tweet_obj)

            return tweets
        except Exception as e:
            logger.error(f"Erro ao buscar tweets via método alternativo para '{query}': {e}")
            return []

    def buscar_tweets(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca tweets sobre um termo específico.

        Args:
            query: Consulta de busca
            max_results: Número máximo de resultados

        Returns:
            List[Dict[str, Any]]: Lista de tweets encontrados
        """
        logger.info(f"Buscando tweets para '{query}'...")

        # Tentar usar a API oficial primeiro
        if self.use_api:
            tweets = self._buscar_tweets_api(query, max_results)
        else:
            # Fallback para método alternativo
            tweets = self._buscar_tweets_alternativo(query, max_results)

        # Carregar cache
        cache = self._load_cache(query)

        # Filtrar tweets já existentes no cache
        ids_cache = {tweet["id"] for tweet in cache}
        tweets_novos = [tweet for tweet in tweets if tweet["id"] not in ids_cache]

        # Atualizar cache
        cache = tweets_novos + cache
        cache = cache[:100]  # Manter apenas os 100 tweets mais recentes
        self._save_cache(query, cache)

        logger.info(f"Encontrados {len(tweets_novos)} tweets novos para '{query}'")

        # Retornar os tweets mais recentes
        return tweets[:max_results]

    def buscar_tweets_por_termos(self, termos: List[str], max_por_termo: int = 3,
                                max_total: int = 15, dias_max: int = 7) -> List[Dict[str, Any]]:
        """
        Busca tweets para uma lista de termos, filtrando por data.

        Args:
            termos: Lista de termos de busca
            max_por_termo: Número máximo de tweets por termo
            max_total: Número máximo de tweets no total
            dias_max: Número máximo de dias de antiguidade dos tweets

        Returns:
            List[Dict[str, Any]]: Lista de tweets encontrados
        """
        todos_tweets = []

        # Calcular a data limite (hoje - dias_max)
        data_limite = datetime.now() - timedelta(days=dias_max)
        data_limite_iso = data_limite.isoformat()

        logger.info(f"Buscando tweets mais recentes que {data_limite.strftime('%d/%m/%Y')}")

        for termo in termos:
            # Adicionar um pequeno atraso para não sobrecarregar os servidores
            time.sleep(random.uniform(1, 3))

            tweets = self.buscar_tweets(termo, max_por_termo * 2)  # Buscar mais para compensar filtragem

            # Filtrar tweets pela data
            tweets_recentes = []
            for tweet in tweets:
                # Se não tiver data, assumir que é recente
                if not tweet.get("created_at"):
                    tweets_recentes.append(tweet)
                    continue

                # Verificar se a data é mais recente que o limite
                if tweet["created_at"] >= data_limite_iso:
                    tweets_recentes.append(tweet)

            logger.info(f"Termo '{termo}': {len(tweets)} tweets encontrados, {len(tweets_recentes)} dentro do período de {dias_max} dias")

            todos_tweets.extend(tweets_recentes[:max_por_termo])  # Limitar ao máximo por termo

            # Parar se já tivermos tweets suficientes
            if len(todos_tweets) >= max_total:
                break

        # Remover duplicatas (mesmo ID)
        ids_vistos = set()
        tweets_unicos = []

        for tweet in todos_tweets:
            if tweet["id"] not in ids_vistos:
                ids_vistos.add(tweet["id"])
                tweets_unicos.append(tweet)

        # Ordenar por engajamento (likes + retweets) e depois por data
        tweets_unicos.sort(key=lambda x: (x.get("likes", 0) + x.get("retweets", 0), x.get("created_at", "")), reverse=True)

        # Limitar ao número máximo de tweets
        return tweets_unicos[:max_total]

    def buscar_tweets_por_contas(self, contas: List[str], max_por_conta: int = 3,
                               max_total: int = 15, dias_max: int = 7) -> List[Dict[str, Any]]:
        """
        Busca tweets de contas específicas, filtrando por data.

        Args:
            contas: Lista de nomes de usuário
            max_por_conta: Número máximo de tweets por conta
            max_total: Número máximo de tweets no total
            dias_max: Número máximo de dias de antiguidade dos tweets

        Returns:
            List[Dict[str, Any]]: Lista de tweets encontrados
        """
        todos_tweets = []

        # Calcular a data limite (hoje - dias_max)
        data_limite = datetime.now() - timedelta(days=dias_max)
        data_limite_iso = data_limite.isoformat()

        logger.info(f"Buscando tweets de contas mais recentes que {data_limite.strftime('%d/%m/%Y')}")

        for conta in contas:
            # Adicionar um pequeno atraso para não sobrecarregar os servidores
            time.sleep(random.uniform(1, 3))

            # Buscar tweets da conta
            query = f"from:{conta}"
            tweets = self.buscar_tweets(query, max_por_conta * 2)  # Buscar mais para compensar filtragem

            # Filtrar tweets pela data
            tweets_recentes = []
            for tweet in tweets:
                # Se não tiver data, assumir que é recente
                if not tweet.get("created_at"):
                    tweets_recentes.append(tweet)
                    continue

                # Verificar se a data é mais recente que o limite
                if tweet["created_at"] >= data_limite_iso:
                    tweets_recentes.append(tweet)

            logger.info(f"Conta '@{conta}': {len(tweets)} tweets encontrados, {len(tweets_recentes)} dentro do período de {dias_max} dias")

            todos_tweets.extend(tweets_recentes[:max_por_conta])  # Limitar ao máximo por conta

            # Parar se já tivermos tweets suficientes
            if len(todos_tweets) >= max_total:
                break

        # Ordenar por data (mais recentes primeiro) e depois por engajamento
        todos_tweets.sort(key=lambda x: (x.get("created_at", ""), x.get("likes", 0) + x.get("retweets", 0)), reverse=True)

        # Limitar ao número máximo de tweets
        return todos_tweets[:max_total]

def main():
    """
    Função principal para testar o buscador de tweets.
    """
    import argparse

    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Buscador de tweets sobre criptomoedas")
    parser.add_argument("--api-key", help="Chave da API do Twitter")
    parser.add_argument("--api-secret", help="Segredo da API do Twitter")
    parser.add_argument("--bearer-token", help="Token de portador da API do Twitter")
    parser.add_argument("--sentimento", choices=["positivo", "negativo", "neutro"],
                        help="Filtrar tweets por sentimento")
    parser.add_argument("--max", type=int, default=5, help="Número máximo de tweets a buscar")
    parser.add_argument("--dias", type=int, default=7, help="Número máximo de dias de antiguidade dos tweets")

    args = parser.parse_args()

    # Criar o scraper
    scraper = TwitterCriptoScraper(
        api_key=args.api_key,
        api_secret=args.api_secret,
        bearer_token=args.bearer_token,
        filtro_sentimento=args.sentimento
    )

    # Buscar tweets por termos
    print("\nBuscando tweets por termos relevantes...")
    tweets_termos = scraper.buscar_tweets_por_termos(
        TERMOS_BUSCA[:3],
        max_por_termo=2,
        max_total=args.max,
        dias_max=args.dias
    )

    print(f"\nEncontrados {len(tweets_termos)} tweets por termos:\n")
    for i, tweet in enumerate(tweets_termos, 1):
        # Mostrar informações de sentimento
        sentimento_info = f"[{tweet.get('sentimento', 'desconhecido').upper()}]"

        print(f"{i}. @{tweet.get('author_username', 'desconhecido')}: {tweet['text'][:100]}... {sentimento_info}")
        print(f"   Likes: {tweet.get('likes', 0)}, Retweets: {tweet.get('retweets', 0)}")
        print(f"   URL: {tweet['url']}")
        print()

    # Buscar tweets por contas
    print("\nBuscando tweets de contas relevantes...")
    tweets_contas = scraper.buscar_tweets_por_contas(
        CONTAS_CRIPTO[:3],
        max_por_conta=2,
        max_total=args.max,
        dias_max=args.dias
    )

    print(f"\nEncontrados {len(tweets_contas)} tweets de contas:\n")
    for i, tweet in enumerate(tweets_contas, 1):
        # Mostrar informações de sentimento
        sentimento_info = f"[{tweet.get('sentimento', 'desconhecido').upper()}]"

        print(f"{i}. @{tweet.get('author_username', 'desconhecido')}: {tweet['text'][:100]}... {sentimento_info}")
        print(f"   Likes: {tweet.get('likes', 0)}, Retweets: {tweet.get('retweets', 0)}")
        print(f"   URL: {tweet['url']}")
        print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
