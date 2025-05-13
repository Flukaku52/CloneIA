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

    def _simplificar_noticias(self, noticias: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Simplifica as notícias para um público leigo.

        Args:
            noticias: Lista de notícias

        Returns:
            List[Dict[str, Any]]: Lista de notícias simplificadas
        """
        nivel_tecnico = self.content_manager.rapidinha_params.get("nivel_tecnico", "baixo")

        # Se o nível técnico não for baixo, retornar as notícias originais
        if nivel_tecnico != "baixo":
            return noticias

        # Lista de termos técnicos e suas versões simplificadas
        termos_tecnicos = {
            "blockchain": "tecnologia por trás das criptomoedas",
            "hash rate": "poder de processamento",
            "halving": "evento que reduz pela metade a recompensa dos mineradores",
            "fork": "atualização da rede",
            "smart contract": "contrato digital automático",
            "staking": "processo de guardar criptomoedas para ganhar recompensas",
            "yield farming": "forma de ganhar recompensas com criptomoedas",
            "liquidity pool": "reserva de criptomoedas",
            "defi": "finanças descentralizadas",
            "nft": "token não fungível (arte digital)",
            "token": "moeda digital",
            "wallet": "carteira digital",
            "exchange": "corretora de criptomoedas",
            "mining": "mineração",
            "miner": "minerador",
            "proof of work": "prova de trabalho",
            "proof of stake": "prova de participação",
            "consensus": "consenso",
            "decentralized": "descentralizado",
            "centralized": "centralizado",
            "protocol": "protocolo",
            "layer 2": "segunda camada",
            "scalability": "escalabilidade",
            "volatility": "volatilidade"
        }

        noticias_simplificadas = []

        for noticia in noticias:
            noticia_simplificada = noticia.copy()

            # Simplificar o título
            titulo = noticia.get('titulo', '')
            for termo, simplificado in termos_tecnicos.items():
                padrao = re.compile(r'\b' + re.escape(termo) + r'\b', re.IGNORECASE)
                titulo = padrao.sub(f"{termo} ({simplificado})", titulo, count=1)
            noticia_simplificada['titulo'] = titulo

            # Simplificar o resumo
            resumo = noticia.get('resumo', '')
            for termo, simplificado in termos_tecnicos.items():
                padrao = re.compile(r'\b' + re.escape(termo) + r'\b', re.IGNORECASE)
                resumo = padrao.sub(f"{termo} ({simplificado})", resumo, count=1)
            noticia_simplificada['resumo'] = resumo

            noticias_simplificadas.append(noticia_simplificada)

        return noticias_simplificadas

    def _formatar_noticia(self, noticia: Dict[str, Any], usar_transicao: bool = True) -> str:
        """
        Formata uma notícia para o script.

        Args:
            noticia: Dicionário com informações da notícia
            usar_transicao: Se True, adiciona uma transição antes do resumo

        Returns:
            str: Texto formatado da notícia
        """
        titulo = noticia.get('titulo', '')
        resumo = noticia.get('resumo', '')
        portal = noticia.get('portal', '')
        data = noticia.get('data', '')

        # Formatar o texto
        if usar_transicao:
            # Adicionar uma transição aleatória
            transicao = self.content_manager.get_random_transition()
            texto = f"{titulo}.\n\n{transicao} {resumo}"
        else:
            texto = f"{titulo}.\n\n{resumo}"

        # Adicionar fonte de forma mais concisa
        texto += f" (Fonte: {portal}, {data})"

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

    def gerar_script(self, num_noticias: int = 4, num_tweets: int = 0) -> str:
        """
        Gera um script para o vídeo Rapidinha.

        Args:
            num_noticias: Número de notícias a incluir (padrão: 4)
            num_tweets: Número de tweets a incluir (padrão: 0)

        Returns:
            str: Script gerado
        """
        # Obter o número padrão de notícias da configuração
        num_noticias_padrao = self.content_manager.rapidinha_params.get("num_noticias_padrao", 4)
        if num_noticias != 4:  # Se foi especificado um valor diferente do padrão
            num_noticias = max(3, min(num_noticias, 4))  # Garantir entre 3 e 4 notícias
        else:
            num_noticias = num_noticias_padrao

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

        # Simplificar as notícias para público leigo
        melhores_noticias = self._simplificar_noticias(melhores_noticias)

        # Buscar tweets relacionados à primeira notícia (se solicitado)
        melhores_tweets = []
        if num_tweets > 0:
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

            # Usar as transições numeradas para as notícias
            if i == 0:
                conteudo += self._formatar_noticia(noticia, usar_transicao=False)
            else:
                transicao = f"Notícia {i+1}:" if i < 3 else "E para finalizar:"
                conteudo += f"{transicao} {self._formatar_noticia(noticia, usar_transicao=False)}"

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
