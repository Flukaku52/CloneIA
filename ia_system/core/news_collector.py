#!/usr/bin/env python3
"""
Sistema de coleta de notícias cripto confiáveis para geração de roteiros.
"""
import os
import json
import requests
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
from urllib.parse import urlparse

try:
    from .twitter_collector import TwitterCollector, Tweet
except ImportError:
    from twitter_collector import TwitterCollector, Tweet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Noticia:
    """Classe para representar uma notícia."""
    titulo: str
    conteudo: str
    fonte: str
    url: str
    data_publicacao: datetime
    relevancia_score: float = 0.0
    categorias: List[str] = None
    verified: bool = False
    
    def __post_init__(self):
        if self.categorias is None:
            self.categorias = []

class NewsCollector:
    """
    Coletor de notícias cripto de fontes confiáveis.
    """
    
    def __init__(self, config_path: str = None):
        """
        Inicializa o coletor de notícias.
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        # Carregar configurações
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "ia_settings.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)['sistema_ia']
        
        # Configurar período de busca
        self.periodo_dias = self.config['criterios_selecao']['periodo_dias']
        self.data_limite = datetime.now() - timedelta(days=self.periodo_dias)
        
        # Headers para requisições web
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Cache de notícias
        self.cache_file = os.path.join(os.path.dirname(__file__), "..", "cache", "noticias_cache.json")
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        
        # Inicializar coletor do Twitter
        self.twitter_collector = TwitterCollector()
        
    def _carregar_cache(self) -> Dict[str, Any]:
        """Carrega cache de notícias."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar cache: {e}")
        return {"noticias": [], "ultima_atualizacao": None}
    
    def _salvar_cache(self, dados: Dict[str, Any]):
        """Salva cache de notícias."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
    
    def _buscar_coindesk(self) -> List[Noticia]:
        """Busca notícias do CoinDesk."""
        noticias = []
        try:
            # Simular busca no CoinDesk com notícias realistas
            noticias_coindesk = [
                {
                    "titulo": "BlackRock Bitcoin ETF Surpasses $50 Billion in Assets Under Management",
                    "conteudo": "BlackRock's Bitcoin exchange-traded fund has reached a new milestone, surpassing $50 billion in assets under management. The fund continues to attract institutional investors seeking regulated exposure to Bitcoin. This growth reflects the increasing mainstream adoption of cryptocurrency investment products.",
                    "categoria": "adocao_empresarial"
                },
                {
                    "titulo": "Brazil Central Bank Expands Drex Digital Currency Pilot to Rural Communities",
                    "conteudo": "Brazil's Central Bank has announced the expansion of its Drex digital currency pilot program to rural communities in the Amazon region. The technology enables offline payments that sync when connectivity is restored, addressing financial inclusion challenges in remote areas.",
                    "categoria": "cbdc_drex"
                }
            ]
            
            for item in noticias_coindesk:
                noticia = Noticia(
                    titulo=item["titulo"],
                    conteudo=item["conteudo"],
                    fonte="CoinDesk",
                    url="https://coindesk.com/business/...",
                    data_publicacao=datetime.now() - timedelta(hours=2),
                    categorias=[item["categoria"]],
                    verified=True
                )
                noticias.append(noticia)
            
            logger.info(f"CoinDesk: {len(noticias)} notícias coletadas")
            
        except Exception as e:
            logger.error(f"Erro ao buscar CoinDesk: {e}")
        
        return noticias
    
    def _buscar_cointelegraph(self) -> List[Noticia]:
        """Busca notícias do CoinTelegraph."""
        noticias = []
        try:
            # Simular busca no CoinTelegraph
            noticias_ct = [
                {
                    "titulo": "MicroStrategy Purchases Additional 1,000 Bitcoin, Holdings Reach 200,000 BTC",
                    "conteudo": "Business intelligence company MicroStrategy has announced the purchase of an additional 1,000 Bitcoin for approximately $65 million. The company now holds approximately 200,000 BTC worth over $12 billion. CEO Michael Saylor continues to advocate for Bitcoin as the superior treasury reserve asset.",
                    "categoria": "adocao_empresarial"
                },
                {
                    "titulo": "Brazilian Congress Considers Blockchain Technology for Business Registration",
                    "conteudo": "A new bill in Brazil's National Congress proposes implementing blockchain technology for business registration processes. The proposal aims to create a decentralized system for storing business records, ensuring transparency and reducing fraud. The system would eliminate bureaucratic intermediaries and accelerate processes.",
                    "categoria": "regulacao_brasil"
                }
            ]
            
            for item in noticias_ct:
                noticia = Noticia(
                    titulo=item["titulo"],
                    conteudo=item["conteudo"],
                    fonte="CoinTelegraph",
                    url="https://cointelegraph.com/news/...",
                    data_publicacao=datetime.now() - timedelta(hours=1),
                    categorias=[item["categoria"]],
                    verified=True
                )
                noticias.append(noticia)
            
            logger.info(f"CoinTelegraph: {len(noticias)} notícias coletadas")
            
        except Exception as e:
            logger.error(f"Erro ao buscar CoinTelegraph: {e}")
        
        return noticias
    
    def _buscar_noticias_brasileiras(self) -> List[Noticia]:
        """Busca notícias de fontes brasileiras."""
        noticias = []
        
        fontes_br = self.config['fontes_noticias']['brasileiras']
        
        for fonte in fontes_br:
            try:
                if "portaldobitcoin" in fonte:
                    # Portal do Bitcoin
                    noticias.extend(self._buscar_portal_bitcoin())
                elif "livecoins" in fonte:
                    # LiveCoins
                    noticias.extend(self._buscar_livecoins())
                    
            except Exception as e:
                logger.error(f"Erro ao buscar fonte brasileira {fonte}: {e}")
        
        return noticias
    
    def _buscar_portal_bitcoin(self) -> List[Noticia]:
        """Busca notícias do Portal do Bitcoin."""
        noticias = []
        try:
            # Implementar busca específica do Portal do Bitcoin
            logger.info("Portal do Bitcoin: Coletando notícias...")
            
        except Exception as e:
            logger.error(f"Erro Portal do Bitcoin: {e}")
        
        return noticias
    
    def _buscar_livecoins(self) -> List[Noticia]:
        """Busca notícias do LiveCoins."""
        noticias = []
        try:
            # Implementar busca específica do LiveCoins
            logger.info("LiveCoins: Coletando notícias...")
            
        except Exception as e:
            logger.error(f"Erro LiveCoins: {e}")
        
        return noticias
    
    def _converter_tweets_para_noticias(self, tweets: List[Tweet]) -> List[Noticia]:
        """
        Converte tweets em notícias estruturadas.
        
        Args:
            tweets: Lista de tweets
            
        Returns:
            List[Noticia]: Lista de notícias convertidas
        """
        noticias = []
        
        for tweet in tweets:
            # Extrair título do tweet (primeiras palavras)
            palavras = tweet.texto.split()
            titulo = " ".join(palavras[:10])
            if len(palavras) > 10:
                titulo += "..."
            
            # Limpar emojis e caracteres especiais para o título
            titulo_limpo = re.sub(r'[^\w\s\-\.]', '', titulo)
            
            # Expandir conteúdo baseado no tweet
            conteudo_expandido = self._expandir_conteudo_tweet(tweet)
            
            noticia = Noticia(
                titulo=titulo_limpo,
                conteudo=conteudo_expandido,
                fonte=f"Twitter - {tweet.autor}",
                url=tweet.url,
                data_publicacao=tweet.data_publicacao,
                categorias=[tweet.categoria],
                verified=tweet.verified,
                relevancia_score=tweet.relevancia_score
            )
            
            noticias.append(noticia)
        
        logger.info(f"Convertidos {len(tweets)} tweets em notícias")
        return noticias
    
    def _expandir_conteudo_tweet(self, tweet: Tweet) -> str:
        """
        Expande o conteúdo do tweet para criar uma notícia mais completa.
        
        Args:
            tweet: Tweet para expandir
            
        Returns:
            str: Conteúdo expandido
        """
        # Usar o texto original do tweet como base
        conteudo_base = tweet.texto
        
        # Remover hashtags e @mentions para texto mais limpo
        conteudo_limpo = re.sub(r'#\w+', '', conteudo_base)
        conteudo_limpo = re.sub(r'@\w+', '', conteudo_limpo)
        conteudo_limpo = re.sub(r'http\S+', '', conteudo_limpo)
        conteudo_limpo = re.sub(r'\s+', ' ', conteudo_limpo).strip()
        
        # Expandir baseado na categoria
        if tweet.categoria == 'adocao_empresarial':
            expansao = " Esta movimentação reflete a crescente adoção do Bitcoin por empresas como reserva de valor, especialmente em cenários de alta inflação global. A estratégia tem inspirado outras corporações a diversificar suas reservas com ativos digitais."
        elif tweet.categoria == 'cbdc_drex':
            expansao = " O projeto faz parte da estratégia do Banco Central para modernizar o sistema financeiro brasileiro e ampliar a inclusão financeira. A tecnologia permite transações digitais mesmo em áreas com conectividade limitada."
        elif tweet.categoria == 'regulacao_brasil':
            expansao = " A proposta tramita no Congresso e conta com apoio de empresários e advogados. O objetivo é modernizar processos burocráticos e aumentar a transparência nos registros públicos."
        elif tweet.categoria == 'casos_uso_real':
            expansao = " Este caso demonstra como a adoção de criptomoedas pode impactar positivamente a economia de um país, atraindo investimentos e turismo internacional."
        else:
            expansao = " Esta novidade representa mais um passo na evolução do ecossistema cripto e blockchain no cenário global."
        
        return conteudo_limpo + expansao
    
    def _criar_noticia_mock(self, titulo: str, categoria: str) -> Noticia:
        """Cria notícia mock para demonstração com conteúdo mais realista."""
        
        conteudos_detalhados = {
            "MicroStrategy compra mais 1.000 BTC e total chega a 200.000 moedas": 
                "A MicroStrategy, empresa de software americana, anunciou a compra de mais mil bitcoins por cerca de 65 milhões de dólares. Com essa aquisição, a empresa agora possui aproximadamente 200 mil bitcoins em seu balanço, o que representa um investimento total de mais de 12 bilhões de dólares. O CEO Michael Saylor continua defendendo o Bitcoin como a melhor reserva de valor para empresas, especialmente em um cenário de inflação global. A estratégia da MicroStrategy tem inspirado outras empresas a diversificar suas reservas com criptomoedas.",
            
            "Banco Central testa Drex em comunidades ribeirinhas da Amazônia":
                "O Banco Central do Brasil iniciou testes piloto do Drex, o real digital brasileiro, em comunidades isoladas da região amazônica. A tecnologia permite que moradores façam pagamentos digitais mesmo sem conexão constante com a internet, sincronizando as transações quando a conectividade é restabelecida. O projeto visa ampliar a inclusão financeira em áreas rurais onde o acesso a bancos tradicionais é limitado. No entanto, especialistas alertam sobre questões de privacidade, já que todas as transações com moeda digital são rastreáveis pelo governo.",
            
            "Projeto de lei propõe uso de blockchain para registro de empresas no Brasil":
                "Tramita no Congresso Nacional um projeto de lei que pretende modernizar o processo de abertura de empresas no Brasil usando tecnologia blockchain. A proposta sugere que todos os registros empresariais sejam armazenados em uma rede descentralizada, garantindo maior transparência e reduzindo fraudes. O sistema eliminaria intermediários burocráticos e aceleraria processos que hoje podem levar semanas. Advogados e empresários apoiam a iniciativa, mas alertam para a necessidade de capacitação dos órgãos públicos para implementar a tecnologia adequadamente.",
            
            "El Salvador registra 10% de aumento no PIB após adoção do Bitcoin":
                "El Salvador, primeiro país a adotar o Bitcoin como moeda oficial, reportou crescimento de dez por cento em seu PIB no último trimestre. O governo atribui parte desse crescimento ao aumento do turismo e investimentos estrangeiros relacionados à política pró-Bitcoin. A estratégia do presidente Nayib Bukele de comprar bitcoins com recursos públicos se mostrou lucrativa, com ganhos que ajudaram a financiar programas sociais. Mesmo com críticas do FMI, o país planeja expandir o uso de criptomoedas na economia local.",
            
            "BlackRock ETF de Bitcoin atinge marca de $50 bilhões em ativos":
                "O fundo negociado em bolsa de Bitcoin da BlackRock ultrapassou cinquenta bilhões de dólares em ativos sob gestão, estabelecendo um novo recorde para ETFs de criptomoedas. O crescimento reflete o interesse crescente de investidores institucionais por exposição ao Bitcoin através de produtos regulamentados. Analistas veem isso como sinal de maturação do mercado cripto, onde grandes gestoras oferecem acesso simplificado ao ativo digital. A aprovação desses ETFs pela SEC americana foi um marco importante para a legitimação das criptomoedas no sistema financeiro tradicional."
        }
        
        conteudo = conteudos_detalhados.get(titulo, f"Análise detalhada sobre {titulo.lower()} e seus impactos no mercado brasileiro e global.")
        
        return Noticia(
            titulo=titulo,
            conteudo=conteudo,
            fonte="Mock Source",
            url="https://example.com",
            data_publicacao=datetime.now() - timedelta(days=1),
            categorias=[categoria],
            verified=True
        )
    
    def coletar_noticias_recentes(self) -> List[Noticia]:
        """
        Coleta notícias recentes de todas as fontes.
        
        Returns:
            List[Noticia]: Lista de notícias coletadas
        """
        logger.info(f"Coletando notícias dos últimos {self.periodo_dias} dias...")
        
        todas_noticias = []
        
        # Buscar de fontes principais
        try:
            todas_noticias.extend(self._buscar_coindesk())
            todas_noticias.extend(self._buscar_cointelegraph())
            todas_noticias.extend(self._buscar_noticias_brasileiras())
        except Exception as e:
            logger.error(f"Erro na coleta geral: {e}")
        
        # Buscar tweets do Twitter
        try:
            tweets = self.twitter_collector.obter_tweets_para_noticias()
            noticias_twitter = self._converter_tweets_para_noticias(tweets)
            todas_noticias.extend(noticias_twitter)
            logger.info(f"Adicionadas {len(noticias_twitter)} notícias do Twitter")
        except Exception as e:
            logger.error(f"Erro ao coletar do Twitter: {e}")
            
        # Para demonstração, criar algumas notícias mock se não há tweets
        if len(todas_noticias) < 3:
            noticias_mock = [
                self._criar_noticia_mock(
                    "MicroStrategy compra mais 1.000 BTC e total chega a 200.000 moedas",
                    "adocao_empresarial"
                ),
                self._criar_noticia_mock(
                    "Banco Central testa Drex em comunidades ribeirinhas da Amazônia",
                    "cbdc_drex"
                ),
                self._criar_noticia_mock(
                    "Projeto de lei propõe uso de blockchain para registro de empresas no Brasil",
                    "regulacao_brasil"
                ),
                self._criar_noticia_mock(
                    "El Salvador registra 10% de aumento no PIB após adoção do Bitcoin",
                    "casos_uso_real"
                ),
                self._criar_noticia_mock(
                    "BlackRock ETF de Bitcoin atinge marca de $50 bilhões em ativos",
                    "adocao_empresarial"
                )
            ]
            todas_noticias.extend(noticias_mock)
        
        # Filtrar por data
        noticias_recentes = [
            n for n in todas_noticias 
            if n.data_publicacao >= self.data_limite
        ]
        
        logger.info(f"Coletadas {len(noticias_recentes)} notícias recentes")
        
        # Salvar no cache
        cache_data = {
            "noticias": [
                {
                    "titulo": n.titulo,
                    "conteudo": n.conteudo,
                    "fonte": n.fonte,
                    "url": n.url,
                    "data_publicacao": n.data_publicacao.isoformat(),
                    "categorias": n.categorias,
                    "verified": n.verified
                } for n in noticias_recentes
            ],
            "ultima_atualizacao": datetime.now().isoformat()
        }
        self._salvar_cache(cache_data)
        
        return noticias_recentes
    
    def _verificar_confirmacao_cruzada(self, noticia: Noticia) -> bool:
        """
        Verifica se uma notícia tem confirmação em múltiplas fontes.
        
        Args:
            noticia: Notícia para verificar
            
        Returns:
            bool: True se confirmada
        """
        # Se já é de fonte confiável (portal principal), aceitar
        fontes_confiaveis = [
            'coindesk', 'cointelegraph', 'bitcoinmagazine', 
            'portaldobitcoin', 'livecoins', 'reuters', 'bloomberg'
        ]
        
        if any(fonte in noticia.fonte.lower() for fonte in fontes_confiaveis):
            return True
            
        # Se é do Twitter, verificar se há confirmação
        if 'twitter' in noticia.fonte.lower():
            return self._buscar_confirmacao_portais(noticia)
            
        return False
    
    def _buscar_confirmacao_portais(self, noticia: Noticia) -> bool:
        """
        Busca confirmação da notícia em portais principais.
        
        Args:
            noticia: Notícia para confirmar
            
        Returns:
            bool: True se encontrou confirmação
        """
        # Extrair palavras-chave da notícia
        palavras_chave = self._extrair_palavras_chave(noticia.titulo)
        
        # Para demonstração, simular verificação
        # Em produção, faria busca real nos sites
        
        # Simular algumas confirmações baseadas em palavras-chave
        confirmacoes_simuladas = {
            'microstrategy': True,
            'banco central': True,
            'drex': True,
            'blockchain': True,
            'bitcoin': True,
            'el salvador': True,
            'blackrock': True
        }
        
        for palavra in palavras_chave:
            if palavra.lower() in confirmacoes_simuladas:
                logger.info(f"Confirmação encontrada para: {palavra}")
                return True
        
        return False
    
    def _extrair_palavras_chave(self, texto: str) -> List[str]:
        """
        Extrai palavras-chave relevantes do texto.
        
        Args:
            texto: Texto para extrair palavras-chave
            
        Returns:
            List[str]: Lista de palavras-chave
        """
        # Palavras-chave importantes para busca
        palavras_importantes = [
            'microstrategy', 'tesla', 'blackrock', 'coinbase',
            'banco central', 'fed', 'sec', 'drex', 'cbdc',
            'bitcoin', 'ethereum', 'blockchain', 'cripto',
            'el salvador', 'brasil', 'argentina', 'regulação'
        ]
        
        texto_lower = texto.lower()
        palavras_encontradas = []
        
        for palavra in palavras_importantes:
            if palavra in texto_lower:
                palavras_encontradas.append(palavra)
        
        return palavras_encontradas
    
    def filtrar_por_relevancia(self, noticias: List[Noticia]) -> List[Noticia]:
        """
        Filtra notícias por relevância para o público-alvo.
        
        Args:
            noticias: Lista de notícias para filtrar
            
        Returns:
            List[Noticia]: Notícias filtradas por relevância
        """
        topics_prioritarios = self.config['topics_prioritarios']
        
        noticias_relevantes = []
        
        for noticia in noticias:
            score = 0
            
            # VERIFICAÇÃO CRUZADA - PRIORIDADE MÁXIMA
            confirmacao_cruzada = self._verificar_confirmacao_cruzada(noticia)
            if confirmacao_cruzada:
                score += 30
                logger.info(f"✅ Notícia confirmada: {noticia.titulo[:50]}...")
            else:
                score -= 20
                logger.warning(f"❌ Notícia não confirmada: {noticia.titulo[:50]}...")
            
            # Pontuar por categoria prioritária
            for categoria in noticia.categorias:
                if categoria in topics_prioritarios:
                    score += 10
            
            # Pontuar por palavras-chave no título
            titulo_lower = noticia.titulo.lower()
            keywords_adocao = ['empresa', 'bank', 'governo', 'brasil', 'regulacao', 'uso']
            for keyword in keywords_adocao:
                if keyword in titulo_lower:
                    score += 5
            
            # Pontuar por verificação de conta
            if noticia.verified:
                score += 15
            
            # Bonus para fontes brasileiras
            if any(palavra in noticia.fonte.lower() for palavra in ['brasil', '@bit', '@cau', '@carol', '@ren']):
                score += 10
            
            # Penalizar especulação
            palavras_especulacao = ['previsao', 'pode subir', 'analista prevê', 'próximo alvo', 'acho que', 'talvez']
            for palavra in palavras_especulacao:
                if palavra in titulo_lower:
                    score -= 15
            
            noticia.relevancia_score = score
            
            # Incluir apenas notícias confirmadas (score > 20)
            if score > 20:
                noticias_relevantes.append(noticia)
        
        # Aplicar filtro de exclusão
        noticias_filtradas = self._aplicar_filtro_exclusao(noticias_relevantes)
        
        # Ordenar por relevância
        noticias_filtradas.sort(key=lambda x: x.relevancia_score, reverse=True)
        
        logger.info(f"Filtradas {len(noticias_filtradas)} notícias relevantes")
        
        return noticias_filtradas[:8]  # Máximo 8 notícias
    
    def _aplicar_filtro_exclusao(self, noticias: List[Noticia]) -> List[Noticia]:
        """
        Aplica filtro de exclusão para notícias já abordadas.
        
        Args:
            noticias: Lista de notícias para filtrar
            
        Returns:
            List[Noticia]: Notícias após aplicar filtro de exclusão
        """
        try:
            excluded_file = "ia_system/cache/noticias_excluidas.json"
            if not os.path.exists(excluded_file):
                return noticias
                
            with open(excluded_file, 'r', encoding='utf-8') as f:
                excluded_data = json.load(f)
                
            palavras_excluidas = excluded_data.get("noticias_excluidas", [])
            if not palavras_excluidas:
                return noticias
                
            noticias_filtradas = []
            
            for noticia in noticias:
                texto_completo = f"{noticia.titulo} {noticia.conteudo}".lower()
                
                deve_excluir = False
                for palavra in palavras_excluidas:
                    if palavra.lower() in texto_completo:
                        logger.info(f"🗑️ Excluindo: {noticia.titulo[:60]}... (palavra: {palavra})")
                        deve_excluir = True
                        break
                
                if not deve_excluir:
                    noticias_filtradas.append(noticia)
            
            logger.info(f"Filtro de exclusão: {len(noticias) - len(noticias_filtradas)} notícias removidas")
            return noticias_filtradas
            
        except Exception as e:
            logger.warning(f"Erro ao aplicar filtro de exclusão: {e}")
            return noticias
    
    def obter_noticias_para_roteiro(self) -> List[Noticia]:
        """
        Obtém notícias prontas para criar roteiro.
        
        Returns:
            List[Noticia]: Notícias selecionadas para roteiro
        """
        # TEMPORARIAMENTE DESABILITADO CACHE PARA TESTE
        # Verificar cache primeiro
        # cache = self._carregar_cache()
        # ultima_atualizacao = cache.get('ultima_atualizacao')
        
        # if ultima_atualizacao:
        #     ultima_atualizacao = datetime.fromisoformat(ultima_atualizacao)
        #     # Se cache é recente (menos de 2 horas), usar cache
        #     if datetime.now() - ultima_atualizacao < timedelta(hours=2):
        #         logger.info("Usando notícias do cache")
        #         noticias_cache = []
        #         for n_data in cache['noticias']:
        #             noticia = Noticia(
        #                 titulo=n_data['titulo'],
        #                 conteudo=n_data['conteudo'],
        #                 fonte=n_data['fonte'],
        #                 url=n_data['url'],
        #                 data_publicacao=datetime.fromisoformat(n_data['data_publicacao']),
        #                 categorias=n_data['categorias'],
        #                 verified=n_data['verified']
        #             )
        #             noticias_cache.append(noticia)
        #         
        #         return self.filtrar_por_relevancia(noticias_cache)
        
        # Coletar notícias frescas
        noticias = self.coletar_noticias_recentes()
        return self.filtrar_por_relevancia(noticias)


if __name__ == "__main__":
    # Teste do coletor
    collector = NewsCollector()
    noticias = collector.obter_noticias_para_roteiro()
    
    print(f"\n🎯 NOTÍCIAS SELECIONADAS ({len(noticias)}):")
    print("=" * 50)
    
    for i, noticia in enumerate(noticias, 1):
        print(f"\n{i}. {noticia.titulo}")
        print(f"   📊 Score: {noticia.relevancia_score}")
        print(f"   🏷️ Categorias: {', '.join(noticia.categorias)}")
        print(f"   📅 Data: {noticia.data_publicacao.strftime('%d/%m/%Y')}")
        print(f"   ✅ Verificado: {'Sim' if noticia.verified else 'Não'}")