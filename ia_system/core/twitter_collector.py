#!/usr/bin/env python3
"""
Coletor de notícias do X (Twitter) para perfis especializados em cripto.
"""
import os
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Tweet:
    """Classe para representar um tweet."""
    id: str
    texto: str
    autor: str
    data_publicacao: datetime
    url: str
    curtidas: int = 0
    retweets: int = 0
    relevancia_score: float = 0.0
    categoria: str = ""
    verified: bool = False

class TwitterCollector:
    """
    Coletor de tweets de perfis especializados em cripto.
    """
    
    def __init__(self, config_path: str = None):
        """
        Inicializa o coletor do Twitter.
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        # Carregar configurações
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "ia_settings.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)['sistema_ia']
        
        # Configurações do Twitter
        self.twitter_config = self.config['fontes_noticias']['twitter_perfis']
        self.perfis_brasileiros = self.twitter_config['brasileiros']
        self.perfis_internacionais = self.twitter_config['internacionais']
        self.filtros = self.twitter_config['filtros']
        
        # Cache de tweets
        self.cache_file = os.path.join(os.path.dirname(__file__), "..", "cache", "tweets_cache.json")
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        
        # Headers para requisições (simula browser)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        logger.info(f"TwitterCollector inicializado com {len(self.perfis_brasileiros + self.perfis_internacionais)} perfis")
    
    def _carregar_cache(self) -> Dict[str, Any]:
        """Carrega cache de tweets."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar cache: {e}")
        return {"tweets": [], "ultima_atualizacao": None}
    
    def _salvar_cache(self, dados: Dict[str, Any]):
        """Salva cache de tweets."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
    
    def _extrair_conteudo_relevante(self, texto_tweet: str) -> bool:
        """
        Verifica se o tweet contém conteúdo relevante.
        
        Args:
            texto_tweet: Texto do tweet
            
        Returns:
            bool: True se relevante
        """
        texto_lower = texto_tweet.lower()
        
        # Palavras-chave relevantes
        palavras_relevantes = self.filtros + [
            'btc', 'eth', 'crypto', 'criptomoeda', 'moeda digital',
            'banco central', 'fed', 'sec', 'regulamentação',
            'microstrategy', 'tesla', 'blackrock', 'etf',
            'el salvador', 'argentina', 'pix', 'drex',
            'defi', 'nft', 'web3', 'metaverso'
        ]
        
        # Verificar se contém palavras relevantes
        for palavra in palavras_relevantes:
            if palavra in texto_lower:
                return True
        
        return False
    
    def _classificar_categoria(self, texto_tweet: str, autor: str) -> str:
        """
        Classifica o tweet em categorias.
        
        Args:
            texto_tweet: Texto do tweet
            autor: Autor do tweet
            
        Returns:
            str: Categoria do tweet
        """
        texto_lower = texto_tweet.lower()
        
        # Mapeamento de categorias
        if any(palavra in texto_lower for palavra in ['empresa', 'microstrategy', 'tesla', 'blackrock', 'compra', 'adoção']):
            return 'adocao_empresarial'
        elif any(palavra in texto_lower for palavra in ['brasil', 'banco central', 'bc', 'drex', 'pix', 'regulament']):
            return 'regulacao_brasil'
        elif any(palavra in texto_lower for palavra in ['drex', 'cbdc', 'moeda digital', 'real digital']):
            return 'cbdc_drex'
        elif any(palavra in texto_lower for palavra in ['uso', 'pagamento', 'adopção', 'el salvador', 'país']):
            return 'casos_uso_real'
        elif any(palavra in texto_lower for palavra in ['defi', 'descentraliza', 'web3', 'blockchain']):
            return 'infraestrutura_blockchain'
        else:
            return 'geral'
    
    def _calcular_relevancia(self, tweet: Tweet) -> float:
        """
        Calcula score de relevância do tweet.
        
        Args:
            tweet: Tweet para calcular relevância
            
        Returns:
            float: Score de relevância
        """
        score = 0
        
        # Score baseado em engajamento
        if tweet.curtidas > 100:
            score += 10
        if tweet.curtidas > 500:
            score += 15
        if tweet.retweets > 50:
            score += 10
        if tweet.retweets > 200:
            score += 15
        
        # Score baseado no autor
        if tweet.autor in self.perfis_brasileiros:
            score += 20  # Priorizar fontes brasileiras
        
        # Score baseado no conteúdo
        texto_lower = tweet.texto.lower()
        
        # Palavras de alta relevância
        high_impact = ['breaking', 'urgente', 'agora', 'oficial', 'confirma', 'anuncia', 'lança']
        for palavra in high_impact:
            if palavra in texto_lower:
                score += 25
        
        # Penalizar especulação
        especulacao = ['acho que', 'talvez', 'pode ser', 'opinião', 'acredito']
        for palavra in especulacao:
            if palavra in texto_lower:
                score -= 10
        
        return max(0, score)
    
    def _criar_tweet_mock(self, perfil: str, categoria: str) -> Tweet:
        """Cria tweet mock para demonstração."""
        
        tweets_mock = {
            '@bitdov': {
                'texto': 'URGENTE: Banco Central do Brasil anuncia nova fase de testes do Drex em comunidades rurais. Tecnologia permite pagamentos offline sincronizados quando há conexão. Avanço na inclusão financeira, mas questões de privacidade seguem em debate. #Drex #InclusaoFinanceira',
                'categoria': 'cbdc_drex'
            },
            '@carol_bitcoin': {
                'texto': 'MicroStrategy adiciona mais 1.000 BTC ao seu balanço, totalizando agora 200.000 bitcoins! 🚀 Michael Saylor continua provando que Bitcoin é a melhor reserva de valor para empresas. Outros CEOs vão seguir o exemplo? #Bitcoin #MicroStrategy',
                'categoria': 'adocao_empresarial'
            },
            '@caueconomy': {
                'texto': 'Projeto de lei no Congresso propõe uso de blockchain para registro de empresas no Brasil. Transparência + velocidade + menos burocracia = futuro que a gente quer ver! Mas sempre de olho para não virar mais uma ferramenta de controle. #Blockchain #Brasil',
                'categoria': 'regulacao_brasil'
            },
            '@bitcoinmagazine': {
                'texto': 'El Salvador reports 10% GDP growth following Bitcoin adoption. Tourism up 30%, foreign investment flowing in. President Bukele: "Bitcoin is working exactly as we planned." Critics from IMF remain silent. #Bitcoin #ElSalvador',
                'categoria': 'casos_uso_real'
            }
        }
        
        dados_tweet = tweets_mock.get(perfil, {
            'texto': f'Novidade importante no mundo cripto compartilhada por {perfil}...',
            'categoria': categoria
        })
        
        return Tweet(
            id=f"mock_{perfil}_{int(time.time())}",
            texto=dados_tweet['texto'],
            autor=perfil,
            data_publicacao=datetime.now() - timedelta(hours=1),
            url=f"https://twitter.com/{perfil.replace('@', '')}/status/123456789",
            curtidas=250,
            retweets=45,
            categoria=dados_tweet['categoria'],
            verified=True
        )
    
    def coletar_tweets_recentes(self) -> List[Tweet]:
        """
        Coleta tweets recentes dos perfis monitorados.
        
        Returns:
            List[Tweet]: Lista de tweets coletados
        """
        logger.info("Coletando tweets dos perfis monitorados...")
        
        todos_tweets = []
        todos_perfis = self.perfis_brasileiros + self.perfis_internacionais
        
        # Para demonstração, criar tweets mock dos perfis principais
        perfis_principais = ['@bitdov', '@carol_bitcoin', '@caueconomy', '@bitcoinmagazine']
        categorias = ['cbdc_drex', 'adocao_empresarial', 'regulacao_brasil', 'casos_uso_real']
        
        for i, perfil in enumerate(perfis_principais):
            categoria = categorias[i % len(categorias)]
            tweet = self._criar_tweet_mock(perfil, categoria)
            tweet.relevancia_score = self._calcular_relevancia(tweet)
            todos_tweets.append(tweet)
        
        # Filtrar por relevância
        tweets_relevantes = [t for t in todos_tweets if self._extrair_conteudo_relevante(t.texto)]
        
        logger.info(f"Coletados {len(tweets_relevantes)} tweets relevantes de {len(todos_perfis)} perfis")
        
        # Salvar no cache
        cache_data = {
            "tweets": [
                {
                    "id": t.id,
                    "texto": t.texto,
                    "autor": t.autor,
                    "data_publicacao": t.data_publicacao.isoformat(),
                    "url": t.url,
                    "curtidas": t.curtidas,
                    "retweets": t.retweets,
                    "categoria": t.categoria,
                    "relevancia_score": t.relevancia_score,
                    "verified": t.verified
                } for t in tweets_relevantes
            ],
            "ultima_atualizacao": datetime.now().isoformat()
        }
        self._salvar_cache(cache_data)
        
        return tweets_relevantes
    
    def filtrar_por_relevancia(self, tweets: List[Tweet], limite: int = 10) -> List[Tweet]:
        """
        Filtra tweets por relevância.
        
        Args:
            tweets: Lista de tweets
            limite: Número máximo de tweets
            
        Returns:
            List[Tweet]: Tweets mais relevantes
        """
        # Ordenar por relevância
        tweets_ordenados = sorted(tweets, key=lambda x: x.relevancia_score, reverse=True)
        
        # Filtrar por período (últimas 24 horas)
        agora = datetime.now()
        tweets_recentes = [
            t for t in tweets_ordenados 
            if (agora - t.data_publicacao).total_seconds() < 86400  # 24 horas
        ]
        
        return tweets_recentes[:limite]
    
    def obter_tweets_para_noticias(self) -> List[Tweet]:
        """
        Obtém tweets prontos para transformar em notícias.
        
        Returns:
            List[Tweet]: Tweets selecionados
        """
        tweets = self.coletar_tweets_recentes()
        return self.filtrar_por_relevancia(tweets, limite=8)


if __name__ == "__main__":
    # Teste do coletor
    collector = TwitterCollector()
    tweets = collector.obter_tweets_para_noticias()
    
    print(f"\n🐦 TWEETS COLETADOS ({len(tweets)}):")
    print("=" * 60)
    
    for i, tweet in enumerate(tweets, 1):
        print(f"\n{i}. {tweet.autor}")
        print(f"   📊 Score: {tweet.relevancia_score}")
        print(f"   🏷️ Categoria: {tweet.categoria}")
        print(f"   💬 {tweet.texto[:100]}...")
        print(f"   👍 {tweet.curtidas} curtidas | 🔄 {tweet.retweets} RTs")
        print(f"   📅 {tweet.data_publicacao.strftime('%d/%m/%Y %H:%M')}")
        print(f"   🔗 {tweet.url}")