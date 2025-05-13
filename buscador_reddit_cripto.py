#!/usr/bin/env python3
"""
Buscador de posts sobre criptomoedas no Reddit.
"""
import os
import sys
import json
import time
import random
import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('buscador_reddit_cripto')

# Lista de subreddits confiáveis sobre criptomoedas
SUBREDDITS_CONFIAVEIS = [
    {
        "nome": "r/Bitcoin",
        "url": "https://www.reddit.com/r/Bitcoin/",
        "idioma": "en",
        "confiabilidade": 7
    },
    {
        "nome": "r/CryptoCurrency",
        "url": "https://www.reddit.com/r/CryptoCurrency/",
        "idioma": "en",
        "confiabilidade": 7
    },
    {
        "nome": "r/btc",
        "url": "https://www.reddit.com/r/btc/",
        "idioma": "en",
        "confiabilidade": 6
    },
    {
        "nome": "r/ethereum",
        "url": "https://www.reddit.com/r/ethereum/",
        "idioma": "en",
        "confiabilidade": 8
    },
    {
        "nome": "r/CryptoMarkets",
        "url": "https://www.reddit.com/r/CryptoMarkets/",
        "idioma": "en",
        "confiabilidade": 6
    },
    {
        "nome": "r/BitcoinBeginners",
        "url": "https://www.reddit.com/r/BitcoinBeginners/",
        "idioma": "en",
        "confiabilidade": 8
    },
    {
        "nome": "r/CriptoBrasil",
        "url": "https://www.reddit.com/r/CriptoBrasil/",
        "idioma": "pt",
        "confiabilidade": 7
    }
]

# Termos de busca para criptomoedas
TERMOS_BUSCA = [
    "bitcoin", "ethereum", "cripto", "criptomoeda", "blockchain",
    "bitcoin para iniciantes", "como investir em bitcoin", "bitcoin explicado"
]

class RedditCriptoScraper:
    """
    Classe para buscar posts sobre criptomoedas no Reddit.
    """
    def __init__(self, client_id: str = None, client_secret: str = None, 
                 cache_dir: str = "cache", traduzir_automaticamente: bool = True):
        """
        Inicializa o scraper de posts do Reddit.

        Args:
            client_id: ID do cliente da API do Reddit
            client_secret: Segredo do cliente da API do Reddit
            cache_dir: Diretório para armazenar o cache de posts
            traduzir_automaticamente: Se True, traduz automaticamente posts em outros idiomas
        """
        self.client_id = client_id or os.environ.get("REDDIT_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("REDDIT_CLIENT_SECRET")
        self.cache_dir = cache_dir
        self.traduzir_automaticamente = traduzir_automaticamente
        
        # Verificar se temos credenciais da API
        if not (self.client_id and self.client_secret):
            logger.warning("Credenciais da API do Reddit não configuradas. Usando método alternativo.")
            self.usar_api = False
        else:
            self.usar_api = True
            self._obter_token_acesso()
        
        # Criar diretório de cache se não existir
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Inicializar tradutor se necessário
        if traduzir_automaticamente:
            try:
                from googletrans import Translator
                self.translator = Translator()
            except ImportError:
                logger.warning("Biblioteca googletrans não encontrada. Tradução automática desativada.")
                self.traduzir_automaticamente = False

    def _obter_token_acesso(self) -> None:
        """
        Obtém um token de acesso para a API do Reddit.
        """
        if not self.usar_api:
            return
        
        try:
            auth = requests.auth.HTTPBasicAuth(self.client_id, self.client_secret)
            data = {
                'grant_type': 'client_credentials',
                'username': os.environ.get("REDDIT_USERNAME", ""),
                'password': os.environ.get("REDDIT_PASSWORD", "")
            }
            headers = {'User-Agent': 'CriptoScraper/0.1 by YourUsername'}
            
            response = requests.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=auth,
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                self.token = response.json().get('access_token')
                self.headers = {
                    'User-Agent': 'CriptoScraper/0.1 by YourUsername',
                    'Authorization': f"bearer {self.token}"
                }
                logger.info("Token de acesso do Reddit obtido com sucesso.")
            else:
                logger.error(f"Erro ao obter token de acesso: {response.status_code} - {response.text}")
                self.usar_api = False
        except Exception as e:
            logger.error(f"Erro ao obter token de acesso: {e}")
            self.usar_api = False

    def _get_cache_path(self, nome: str) -> str:
        """
        Retorna o caminho para o arquivo de cache.

        Args:
            nome: Nome do cache

        Returns:
            str: Caminho para o arquivo de cache
        """
        return os.path.join(self.cache_dir, f"reddit_{nome.lower().replace(' ', '_').replace('/', '')}_cache.json")

    def _load_cache(self, nome: str) -> List[Dict[str, Any]]:
        """
        Carrega o cache de posts.

        Args:
            nome: Nome do cache

        Returns:
            List[Dict[str, Any]]: Lista de posts em cache
        """
        cache_path = self._get_cache_path(nome)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar cache para {nome}: {e}")
        return []

    def _save_cache(self, nome: str, posts: List[Dict[str, Any]]) -> None:
        """
        Salva o cache de posts.

        Args:
            nome: Nome do cache
            posts: Lista de posts a serem salvos
        """
        cache_path = self._get_cache_path(nome)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar cache para {nome}: {e}")

    def _traduzir_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traduz um post para português, se necessário.

        Args:
            post: Dados do post

        Returns:
            Dict[str, Any]: Post traduzido
        """
        if not self.traduzir_automaticamente:
            return post

        # Se o post já está em português, não precisa traduzir
        if post.get("idioma", "pt") == "pt":
            return post

        try:
            # Traduzir título
            titulo_traduzido = self.translator.translate(
                post["titulo"], src=post.get("idioma", "en"), dest="pt"
            ).text

            # Traduzir texto, se existir
            texto_traduzido = ""
            if post.get("texto"):
                texto_traduzido = self.translator.translate(
                    post["texto"], src=post.get("idioma", "en"), dest="pt"
                ).text

            # Criar cópia do post com os campos traduzidos
            post_traduzido = post.copy()
            post_traduzido["titulo_original"] = post["titulo"]
            post_traduzido["titulo"] = titulo_traduzido
            
            if texto_traduzido:
                post_traduzido["texto_original"] = post["texto"]
                post_traduzido["texto"] = texto_traduzido
            
            post_traduzido["traduzido"] = True
            post_traduzido["idioma_original"] = post.get("idioma", "en")
            post_traduzido["idioma"] = "pt"

            logger.info(f"Post traduzido: {post['titulo']} -> {titulo_traduzido}")
            return post_traduzido
        except Exception as e:
            logger.error(f"Erro ao traduzir post: {e}")
            # Em caso de erro, retornar o post original
            post["traduzido"] = False
            return post

    def _verificar_credibilidade(self, post: Dict[str, Any], subreddit: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica a credibilidade de um post.

        Args:
            post: Dados do post
            subreddit: Configuração do subreddit

        Returns:
            Dict[str, Any]: Post com informações de credibilidade
        """
        # Inicializar pontuação de credibilidade com base na confiabilidade do subreddit
        credibilidade = subreddit.get("confiabilidade", 5)
        razoes = []

        # Verificar se o post tem muitos upvotes (mais confiável)
        if post.get("upvotes", 0) > 100:
            credibilidade += 1
            razoes.append("Muitos upvotes")
        
        # Verificar se o post tem muitos comentários (mais engajamento)
        if post.get("num_comentarios", 0) > 50:
            credibilidade += 1
            razoes.append("Muitos comentários")
        
        # Verificar se o post é muito recente (menos tempo para verificação)
        if post.get("data_criacao"):
            data_criacao = datetime.fromisoformat(post["data_criacao"].replace("Z", "+00:00"))
            if (datetime.now() - data_criacao).total_seconds() < 3600:  # Menos de 1 hora
                credibilidade -= 1
                razoes.append("Post muito recente")
        
        # Verificar se o título é muito sensacionalista (todo em maiúsculas, muitas exclamações)
        if post["titulo"].isupper() or post["titulo"].count("!") > 1:
            credibilidade -= 2
            razoes.append("Título sensacionalista")

        # Limitar a pontuação entre 0 e 10
        credibilidade = max(0, min(10, credibilidade))

        # Adicionar informações de credibilidade ao post
        post["credibilidade"] = credibilidade
        post["razoes_credibilidade"] = razoes
        post["confiavel"] = credibilidade >= 6  # Consideramos confiável se a pontuação for 6 ou mais

        return post

    def buscar_posts_por_subreddit(self, subreddit: Dict[str, Any], max_posts: int = 5) -> List[Dict[str, Any]]:
        """
        Busca posts em um subreddit específico.

        Args:
            subreddit: Configuração do subreddit
            max_posts: Número máximo de posts a retornar

        Returns:
            List[Dict[str, Any]]: Lista de posts encontrados
        """
        logger.info(f"Buscando posts no subreddit {subreddit['nome']}...")
        
        # Implementação usando a API do Reddit
        if self.usar_api:
            return self._buscar_posts_por_subreddit_api(subreddit, max_posts)
        
        # Implementação alternativa (sem API)
        return self._buscar_posts_por_subreddit_alternativo(subreddit, max_posts)

    def _buscar_posts_por_subreddit_api(self, subreddit: Dict[str, Any], max_posts: int = 5) -> List[Dict[str, Any]]:
        """
        Busca posts em um subreddit usando a API do Reddit.

        Args:
            subreddit: Configuração do subreddit
            max_posts: Número máximo de posts a retornar

        Returns:
            List[Dict[str, Any]]: Lista de posts encontrados
        """
        try:
            # Extrair nome do subreddit
            subreddit_nome = subreddit["nome"].replace("r/", "")
            
            # Construir URL da API
            url = f"https://oauth.reddit.com/r/{subreddit_nome}/hot"
            params = {
                "limit": max_posts * 2  # Buscar mais para compensar filtragem
            }
            
            # Fazer requisição
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extrair posts
            posts = []
            for child in data.get("data", {}).get("children", []):
                post_data = child.get("data", {})
                
                # Ignorar posts fixados
                if post_data.get("stickied", False):
                    continue
                
                post = {
                    "id": post_data.get("id"),
                    "titulo": post_data.get("title"),
                    "texto": post_data.get("selftext"),
                    "url": post_data.get("url"),
                    "permalink": f"https://www.reddit.com{post_data.get('permalink')}",
                    "autor": post_data.get("author"),
                    "subreddit": subreddit["nome"],
                    "upvotes": post_data.get("ups", 0),
                    "num_comentarios": post_data.get("num_comments", 0),
                    "data_criacao": datetime.fromtimestamp(post_data.get("created_utc", 0)).isoformat(),
                    "idioma": subreddit.get("idioma", "en"),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Verificar credibilidade
                post = self._verificar_credibilidade(post, subreddit)
                
                # Adicionar à lista apenas se for confiável
                if post["confiavel"]:
                    # Traduzir se necessário
                    if subreddit.get("idioma") != "pt" and self.traduzir_automaticamente:
                        post = self._traduzir_post(post)
                    
                    posts.append(post)
            
            return posts[:max_posts]
        except Exception as e:
            logger.error(f"Erro ao buscar posts no subreddit {subreddit['nome']}: {e}")
            return []

    def _buscar_posts_por_subreddit_alternativo(self, subreddit: Dict[str, Any], max_posts: int = 5) -> List[Dict[str, Any]]:
        """
        Busca posts em um subreddit sem usar a API do Reddit (método alternativo).

        Args:
            subreddit: Configuração do subreddit
            max_posts: Número máximo de posts a retornar

        Returns:
            List[Dict[str, Any]]: Lista de posts encontrados
        """
        try:
            # Construir URL JSON (funciona sem autenticação)
            url = f"{subreddit['url'].rstrip('/')}.json"
            
            # Fazer requisição
            headers = {'User-Agent': 'CriptoScraper/0.1 by YourUsername'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Extrair posts
            posts = []
            for child in data.get("data", {}).get("children", []):
                post_data = child.get("data", {})
                
                # Ignorar posts fixados
                if post_data.get("stickied", False):
                    continue
                
                post = {
                    "id": post_data.get("id"),
                    "titulo": post_data.get("title"),
                    "texto": post_data.get("selftext"),
                    "url": post_data.get("url"),
                    "permalink": f"https://www.reddit.com{post_data.get('permalink')}",
                    "autor": post_data.get("author"),
                    "subreddit": subreddit["nome"],
                    "upvotes": post_data.get("ups", 0),
                    "num_comentarios": post_data.get("num_comments", 0),
                    "data_criacao": datetime.fromtimestamp(post_data.get("created_utc", 0)).isoformat(),
                    "idioma": subreddit.get("idioma", "en"),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Verificar credibilidade
                post = self._verificar_credibilidade(post, subreddit)
                
                # Adicionar à lista apenas se for confiável
                if post["confiavel"]:
                    # Traduzir se necessário
                    if subreddit.get("idioma") != "pt" and self.traduzir_automaticamente:
                        post = self._traduzir_post(post)
                    
                    posts.append(post)
            
            return posts[:max_posts]
        except Exception as e:
            logger.error(f"Erro ao buscar posts no subreddit {subreddit['nome']} (método alternativo): {e}")
            return []

    def buscar_posts_por_termo(self, termo: str, max_posts: int = 5) -> List[Dict[str, Any]]:
        """
        Busca posts por um termo específico.

        Args:
            termo: Termo de busca
            max_posts: Número máximo de posts a retornar

        Returns:
            List[Dict[str, Any]]: Lista de posts encontrados
        """
        logger.info(f"Buscando posts para o termo '{termo}'...")
        
        # Implementação usando a API do Reddit
        if self.usar_api:
            return self._buscar_posts_por_termo_api(termo, max_posts)
        
        # Implementação alternativa (sem API)
        return self._buscar_posts_por_termo_alternativo(termo, max_posts)

    def _buscar_posts_por_termo_api(self, termo: str, max_posts: int = 5) -> List[Dict[str, Any]]:
        """
        Busca posts por um termo usando a API do Reddit.

        Args:
            termo: Termo de busca
            max_posts: Número máximo de posts a retornar

        Returns:
            List[Dict[str, Any]]: Lista de posts encontrados
        """
        try:
            # Construir URL da API
            url = f"https://oauth.reddit.com/search"
            params = {
                "q": termo,
                "sort": "relevance",
                "limit": max_posts * 2,  # Buscar mais para compensar filtragem
                "t": "week"  # Últimos 7 dias
            }
            
            # Fazer requisição
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extrair posts
            posts = []
            for child in data.get("data", {}).get("children", []):
                post_data = child.get("data", {})
                
                # Ignorar posts fixados
                if post_data.get("stickied", False):
                    continue
                
                # Encontrar o subreddit correspondente
                subreddit_nome = f"r/{post_data.get('subreddit')}"
                subreddit_info = next((s for s in SUBREDDITS_CONFIAVEIS if s["nome"] == subreddit_nome), None)
                
                # Se não for de um subreddit confiável, usar valores padrão
                if not subreddit_info:
                    subreddit_info = {
                        "nome": subreddit_nome,
                        "idioma": "en",
                        "confiabilidade": 5  # Valor médio
                    }
                
                post = {
                    "id": post_data.get("id"),
                    "titulo": post_data.get("title"),
                    "texto": post_data.get("selftext"),
                    "url": post_data.get("url"),
                    "permalink": f"https://www.reddit.com{post_data.get('permalink')}",
                    "autor": post_data.get("author"),
                    "subreddit": subreddit_nome,
                    "upvotes": post_data.get("ups", 0),
                    "num_comentarios": post_data.get("num_comments", 0),
                    "data_criacao": datetime.fromtimestamp(post_data.get("created_utc", 0)).isoformat(),
                    "idioma": subreddit_info.get("idioma", "en"),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Verificar credibilidade
                post = self._verificar_credibilidade(post, subreddit_info)
                
                # Adicionar à lista apenas se for confiável
                if post["confiavel"]:
                    # Traduzir se necessário
                    if subreddit_info.get("idioma") != "pt" and self.traduzir_automaticamente:
                        post = self._traduzir_post(post)
                    
                    posts.append(post)
            
            return posts[:max_posts]
        except Exception as e:
            logger.error(f"Erro ao buscar posts para o termo '{termo}': {e}")
            return []

    def _buscar_posts_por_termo_alternativo(self, termo: str, max_posts: int = 5) -> List[Dict[str, Any]]:
        """
        Busca posts por um termo sem usar a API do Reddit (método alternativo).

        Args:
            termo: Termo de busca
            max_posts: Número máximo de posts a retornar

        Returns:
            List[Dict[str, Any]]: Lista de posts encontrados
        """
        # Implementação simplificada para quando não temos a API
        # Na prática, seria necessário usar web scraping ou outra abordagem
        logger.warning("Método alternativo de busca por termo não implementado completamente.")
        return []

    def buscar_todos_posts(self, max_por_subreddit: int = 2, max_por_termo: int = 3, max_total: int = 10,
                         dias_max: int = 7) -> List[Dict[str, Any]]:
        """
        Busca posts em todos os subreddits e termos configurados, filtrando por data.

        Args:
            max_por_subreddit: Número máximo de posts por subreddit
            max_por_termo: Número máximo de posts por termo
            max_total: Número máximo de posts no total
            dias_max: Número máximo de dias de antiguidade dos posts

        Returns:
            List[Dict[str, Any]]: Lista de posts encontrados
        """
        todos_posts = []
        
        # Calcular a data limite (hoje - dias_max)
        data_limite = datetime.now() - timedelta(days=dias_max)
        data_limite_iso = data_limite.isoformat()
        
        logger.info(f"Buscando posts mais recentes que {data_limite.strftime('%d/%m/%Y')}")
        
        # Buscar posts por subreddit
        for subreddit in SUBREDDITS_CONFIAVEIS:
            # Adicionar um pequeno atraso para não sobrecarregar a API
            time.sleep(random.uniform(1, 2))
            
            posts = self.buscar_posts_por_subreddit(subreddit, max_por_subreddit * 2)  # Buscar mais para compensar filtragem
            
            # Filtrar posts pela data
            posts_recentes = []
            for post in posts:
                # Se não tiver data, assumir que é recente
                if not post.get("data_criacao"):
                    posts_recentes.append(post)
                    continue
                
                # Verificar se a data é mais recente que o limite
                if post["data_criacao"] >= data_limite_iso:
                    posts_recentes.append(post)
            
            logger.info(f"Subreddit {subreddit['nome']}: {len(posts)} posts encontrados, {len(posts_recentes)} dentro do período de {dias_max} dias")
            
            todos_posts.extend(posts_recentes[:max_por_subreddit])
            
            # Parar se já tivermos posts suficientes
            if len(todos_posts) >= max_total:
                break
        
        # Buscar posts por termo
        for termo in TERMOS_BUSCA:
            # Adicionar um pequeno atraso para não sobrecarregar a API
            time.sleep(random.uniform(1, 2))
            
            posts = self.buscar_posts_por_termo(termo, max_por_termo * 2)  # Buscar mais para compensar filtragem
            
            # Filtrar posts pela data
            posts_recentes = []
            for post in posts:
                # Se não tiver data, assumir que é recente
                if not post.get("data_criacao"):
                    posts_recentes.append(post)
                    continue
                
                # Verificar se a data é mais recente que o limite
                if post["data_criacao"] >= data_limite_iso:
                    posts_recentes.append(post)
            
            logger.info(f"Termo '{termo}': {len(posts)} posts encontrados, {len(posts_recentes)} dentro do período de {dias_max} dias")
            
            todos_posts.extend(posts_recentes[:max_por_termo])
            
            # Parar se já tivermos posts suficientes
            if len(todos_posts) >= max_total:
                break
        
        # Remover duplicatas (pelo ID do post)
        posts_unicos = []
        ids_vistos = set()
        for post in todos_posts:
            if post["id"] not in ids_vistos:
                posts_unicos.append(post)
                ids_vistos.add(post["id"])
        
        # Ordenar por data (mais recentes primeiro)
        posts_unicos.sort(key=lambda x: x.get("data_criacao", ""), reverse=True)
        
        # Limitar ao número máximo de posts
        return posts_unicos[:max_total]

def main():
    """
    Função principal para testar o buscador de posts do Reddit.
    """
    import argparse
    
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Buscador de posts sobre criptomoedas no Reddit")
    parser.add_argument("--client-id", help="ID do cliente da API do Reddit")
    parser.add_argument("--client-secret", help="Segredo do cliente da API do Reddit")
    parser.add_argument("--max", type=int, default=10, help="Número máximo de posts a buscar")
    parser.add_argument("--dias", type=int, default=7, help="Número máximo de dias de antiguidade dos posts")
    parser.add_argument("--no-traduzir", action="store_true", help="Não traduzir posts automaticamente")
    
    args = parser.parse_args()
    
    # Criar o scraper
    scraper = RedditCriptoScraper(
        client_id=args.client_id,
        client_secret=args.client_secret,
        traduzir_automaticamente=not args.no_traduzir
    )
    
    # Buscar posts
    posts = scraper.buscar_todos_posts(max_total=args.max, dias_max=args.dias)
    
    # Exibir os posts encontrados
    print(f"\nEncontrados {len(posts)} posts sobre criptomoedas:\n")
    
    for i, post in enumerate(posts, 1):
        # Mostrar informações de tradução, se aplicável
        titulo_display = post['titulo']
        if post.get('traduzido'):
            titulo_display += f" [Traduzido de: {post.get('idioma_original', 'en')}]"
        
        # Mostrar informações de credibilidade
        credibilidade_info = f"[Credibilidade: {post.get('credibilidade', 'N/A')}/10]"
        
        print(f"{i}. {titulo_display} {credibilidade_info}")
        print(f"   Subreddit: {post['subreddit']}")
        print(f"   Autor: {post['autor']}")
        print(f"   Upvotes: {post.get('upvotes', 'N/A')}")
        print(f"   Comentários: {post.get('num_comentarios', 'N/A')}")
        print(f"   Data: {post.get('data_criacao', 'N/A')}")
        print(f"   URL: {post['permalink']}")
        
        if post.get('texto'):
            texto_display = post['texto'][:150]
            if len(post['texto']) > 150:
                texto_display += "..."
            print(f"   Texto: {texto_display}")
        
        # Mostrar razões de credibilidade, se houver
        if post.get('razoes_credibilidade'):
            print(f"   Observações: {', '.join(post['razoes_credibilidade'])}")
        
        print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
