#!/usr/bin/env python3
"""
Gerador de scripts para os vídeos Rapidinha.
"""
import os
import re
import sys
import json
import logging
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gerador_script')

# Importar módulos necessários
try:
    from buscador_noticias_cripto import NoticiasCriptoScraper
    from buscador_tweets_cripto import TwitterCriptoScraper
    from core.content_manager import ContentManager
except ImportError as e:
    logger.error(f"Erro ao importar módulos necessários: {e}")
    logger.error("Verifique se os arquivos estão no diretório correto.")
    sys.exit(1)

class GeradorScript:
    """
    Classe para gerar scripts para os vídeos Rapidinha.
    """
    def __init__(self, dias_max: int = 7, content_config: str = "config/content_params.json"):
        """
        Inicializa o gerador de scripts.
        
        Args:
            dias_max: Número máximo de dias de antiguidade das notícias
            content_config: Caminho para o arquivo de configuração de conteúdo
        """
        self.dias_max = dias_max
        
        # Inicializar buscadores
        self.buscador_noticias = NoticiasCriptoScraper()
        self.buscador_tweets = TwitterCriptoScraper()
        
        # Inicializar gerenciador de conteúdo
        self.content_manager = ContentManager(config_path=content_config)
        
        logger.info(f"Gerador de scripts inicializado. Saudação: '{self.content_manager.saudacao_inicial}', "
                   f"Duração máxima: {self.content_manager.duracao_maxima} segundos")
    
    def _formatar_noticia(self, noticia: Dict[str, Any]) -> str:
        """
        Formata uma notícia para o script.
        
        Args:
            noticia: Dicionário com informações da notícia
            
        Returns:
            str: Texto formatado da notícia
        """
        titulo = noticia.get('titulo', '')
        resumo = noticia.get('resumo', '')
        portal = noticia.get('portal', '')
        data = noticia.get('data', '')
        link = noticia.get('link', '')
        
        # Adicionar uma transição aleatória
        transicao = self.content_manager.get_random_transition()
        
        # Formatar o texto
        texto = f"{titulo}.\n\n{transicao} {resumo}\n\n"
        
        # Adicionar fonte
        texto += f"Esta informação foi publicada pelo portal {portal} em {data}."
        
        return texto
    
    def _formatar_tweet(self, tweet: Dict[str, Any]) -> str:
        """
        Formata um tweet para o script.
        
        Args:
            tweet: Dicionário com informações do tweet
            
        Returns:
            str: Texto formatado do tweet
        """
        texto = tweet.get('text', '')
        autor = tweet.get('author_name', '')
        username = tweet.get('author_username', '')
        
        # Adicionar uma expressão de ênfase aleatória
        enfase = self.content_manager.get_random_emphasis()
        
        # Formatar o texto
        return f"{enfase} @{username} ({autor}) comentou: \"{texto}\""
    
    def _selecionar_melhores_noticias(self, noticias: List[Dict[str, Any]], num: int = 3) -> List[Dict[str, Any]]:
        """
        Seleciona as melhores notícias com base na credibilidade e data.
        
        Args:
            noticias: Lista de notícias
            num: Número de notícias a selecionar
            
        Returns:
            List[Dict[str, Any]]: Lista de notícias selecionadas
        """
        # Filtrar notícias confiáveis
        noticias_confiaveis = [n for n in noticias if n.get('confiavel', False)]
        
        # Ordenar por credibilidade (mais alta primeiro) e data (mais recente primeiro)
        noticias_ordenadas = sorted(
            noticias_confiaveis,
            key=lambda x: (x.get('credibilidade', 0), x.get('data_iso', '')),
            reverse=True
        )
        
        # Selecionar as melhores
        return noticias_ordenadas[:num]
    
    def _selecionar_melhores_tweets(self, tweets: List[Dict[str, Any]], num: int = 2) -> List[Dict[str, Any]]:
        """
        Seleciona os melhores tweets com base na relevância e engajamento.
        
        Args:
            tweets: Lista de tweets
            num: Número de tweets a selecionar
            
        Returns:
            List[Dict[str, Any]]: Lista de tweets selecionados
        """
        # Filtrar tweets com sentimento positivo ou neutro
        tweets_filtrados = [t for t in tweets if t.get('sentimento') in ['positivo', 'neutro']]
        
        # Calcular pontuação de engajamento
        for tweet in tweets_filtrados:
            likes = tweet.get('likes', 0)
            retweets = tweet.get('retweets', 0)
            replies = tweet.get('replies', 0)
            
            # Fórmula de engajamento
            engajamento = likes + (retweets * 2) + (replies * 1.5)
            tweet['engajamento'] = engajamento
            
            # Considerar confiabilidade da fonte, se disponível
            if 'confiabilidade' in tweet:
                tweet['engajamento'] *= (tweet['confiabilidade'] / 5)
        
        # Ordenar por engajamento (mais alto primeiro)
        tweets_ordenados = sorted(tweets_filtrados, key=lambda x: x.get('engajamento', 0), reverse=True)
        
        # Selecionar os melhores
        return tweets_ordenados[:num]
    
    def gerar_script(self, num_noticias: int = 3, num_tweets: int = 2) -> str:
        """
        Gera um script para o vídeo Rapidinha.
        
        Args:
            num_noticias: Número de notícias a incluir
            num_tweets: Número de tweets a incluir
            
        Returns:
            str: Script gerado
        """
        logger.info(f"Gerando script com {num_noticias} notícias e {num_tweets} tweets...")
        
        # Buscar notícias
        noticias = self.buscador_noticias.buscar_todas_noticias(
            max_total=num_noticias * 3,  # Buscar mais para ter opções
            dias_max=self.dias_max
        )
        
        # Selecionar as melhores notícias
        melhores_noticias = self._selecionar_melhores_noticias(noticias, num_noticias)
        
        if not melhores_noticias:
            logger.warning("Nenhuma notícia encontrada!")
            return ""
        
        # Buscar tweets relacionados à primeira notícia
        termos_busca = []
        for noticia in melhores_noticias[:2]:  # Usar as duas primeiras notícias para extrair termos
            titulo = noticia.get('titulo', '')
            palavras = re.findall(r'\b\w+\b', titulo)
            termos_relevantes = [p for p in palavras if len(p) > 3 and p.lower() not in ['sobre', 'para', 'como', 'mais']]
            termos_busca.extend(termos_relevantes[:3])  # Limitar a 3 termos por notícia
        
        # Remover duplicatas e limitar a 5 termos
        termos_busca = list(set(termos_busca))[:5]
        
        # Buscar tweets
        tweets = self.buscador_tweets.buscar_tweets_por_termos(termos_busca, max_tweets=num_tweets * 3)
        
        # Selecionar os melhores tweets
        melhores_tweets = self._selecionar_melhores_tweets(tweets, num_tweets)
        
        # Gerar o título do vídeo
        noticia_principal = melhores_noticias[0]
        titulo_video = f"Rapidinha Cripto: {noticia_principal.get('titulo')}"
        
        # Gerar o conteúdo principal
        conteudo = ""
        
        # Adicionar notícias
        for i, noticia in enumerate(melhores_noticias):
            if i > 0:
                conteudo += "\n\n"
            conteudo += self._formatar_noticia(noticia)
        
        # Adicionar tweets, se houver
        if melhores_tweets:
            conteudo += "\n\n"
            conteudo += "Veja o que a comunidade está dizendo:\n\n"
            
            for tweet in melhores_tweets:
                conteudo += self._formatar_tweet(tweet) + "\n\n"
        
        # Formatar o script completo usando o gerenciador de conteúdo
        script = self.content_manager.format_script(titulo_video, conteudo)
        
        # Validar o script
        valido, info = self.content_manager.validate_script_length(script)
        if not valido:
            logger.warning(f"Script excede o limite de duração: {info['duracao_estimada_segundos']:.1f}s "
                          f"(máximo: {info['duracao_maxima_segundos']}s)")
            
            # Tentar reduzir o script
            if len(melhores_noticias) > 1:
                logger.info("Tentando reduzir o script removendo uma notícia...")
                return self.gerar_script(num_noticias - 1, num_tweets)
            elif len(melhores_tweets) > 0:
                logger.info("Tentando reduzir o script removendo um tweet...")
                return self.gerar_script(num_noticias, num_tweets - 1)
        
        # Verificar palavras proibidas
        palavras_proibidas = self.content_manager.check_forbidden_words(script)
        if palavras_proibidas:
            logger.warning(f"Script contém palavras proibidas: {', '.join(palavras_proibidas)}")
            
            # Substituir palavras proibidas
            for palavra in palavras_proibidas:
                if palavra in ['investir', 'investimento']:
                    script = re.sub(r'\b' + re.escape(palavra) + r'\b', 'alocar recursos', script, flags=re.IGNORECASE)
                elif palavra in ['lucro', 'ganho']:
                    script = re.sub(r'\b' + re.escape(palavra) + r'\b', 'resultado positivo', script, flags=re.IGNORECASE)
                elif palavra in ['perda', 'prejuízo']:
                    script = re.sub(r'\b' + re.escape(palavra) + r'\b', 'resultado negativo', script, flags=re.IGNORECASE)
                elif palavra in ['recomendo', 'recomendação', 'conselho', 'aconselho']:
                    script = re.sub(r'\b' + re.escape(palavra) + r'\b', 'observação', script, flags=re.IGNORECASE)
                elif palavra in ['compre', 'comprar']:
                    script = re.sub(r'\b' + re.escape(palavra) + r'\b', 'adquirir', script, flags=re.IGNORECASE)
                elif palavra in ['venda', 'vender']:
                    script = re.sub(r'\b' + re.escape(palavra) + r'\b', 'negociar', script, flags=re.IGNORECASE)
        
        logger.info(f"Script gerado com sucesso! ({info['num_palavras']} palavras, "
                   f"{info['duracao_estimada_segundos']:.1f} segundos)")
        
        return script
