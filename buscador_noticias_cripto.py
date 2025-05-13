#!/usr/bin/env python3
"""
Buscador de notícias sobre criptomoedas em portais especializados.
"""
import os
import re
import sys
import json
import time
import random
import logging
import requests
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from googletrans import Translator

# Importar o verificador de notícias
try:
    from core.verificador_noticias import VerificadorNoticias
    VERIFICADOR_DISPONIVEL = True
except ImportError:
    VERIFICADOR_DISPONIVEL = False
    logging.warning("Módulo verificador_noticias não encontrado. O cruzamento de informações não estará disponível.")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('buscador_noticias_cripto')

# Lista de portais de notícias sobre criptomoedas
PORTAIS = [
    # Portais nacionais (confiáveis)
    {
        "nome": "CriptoFácil",
        "url": "https://www.criptofacil.com/ultimas-noticias/",
        "seletor_noticias": "article.jeg_post",
        "seletor_titulo": "h3.jeg_post_title a",
        "seletor_link": "h3.jeg_post_title a",
        "seletor_data": "div.jeg_meta_date a",
        "seletor_resumo": "div.jeg_post_excerpt p",
        "formato_data": "%d de %B de %Y",
        "idioma": "pt",
        "confiabilidade": 8  # Escala de 1-10
    },
    {
        "nome": "Portal do Bitcoin",
        "url": "https://portaldobitcoin.uol.com.br/",
        "seletor_noticias": "div.td_module_flex",
        "seletor_titulo": "h3.entry-title a",
        "seletor_link": "h3.entry-title a",
        "seletor_data": "time.entry-date",
        "seletor_resumo": "div.td-excerpt",
        "formato_data": "%d de %B de %Y",
        "idioma": "pt",
        "confiabilidade": 9  # Escala de 1-10
    },
    {
        "nome": "Cointelegraph Brasil",
        "url": "https://br.cointelegraph.com/",
        "seletor_noticias": "article.post-card",
        "seletor_titulo": "span.post-card__title-text",
        "seletor_link": "a.post-card__title-link",
        "seletor_data": "time.post-card__date",
        "seletor_resumo": "p.post-card__text",
        "formato_data": "%d/%m/%Y",
        "idioma": "pt",
        "confiabilidade": 8  # Escala de 1-10
    },
    {
        "nome": "Livecoins",
        "url": "https://livecoins.com.br/categoria/bitcoin/",
        "seletor_noticias": "article.jeg_post",
        "seletor_titulo": "h3.jeg_post_title a",
        "seletor_link": "h3.jeg_post_title a",
        "seletor_data": "div.jeg_meta_date a",
        "seletor_resumo": "div.jeg_post_excerpt p",
        "formato_data": "%d de %B de %Y",
        "idioma": "pt",
        "confiabilidade": 7  # Escala de 1-10
    },
    {
        "nome": "Bitcoin Portal",
        "url": "https://bitcoinportal.com.br/",
        "seletor_noticias": "article.post",
        "seletor_titulo": "h2.entry-title a",
        "seletor_link": "h2.entry-title a",
        "seletor_data": "time.entry-date",
        "seletor_resumo": "div.entry-content p",
        "formato_data": "%d de %B de %Y",
        "idioma": "pt",
        "confiabilidade": 7  # Escala de 1-10
    },
    {
        "nome": "BeInCrypto Brasil",
        "url": "https://beincrypto.com.br/",
        "seletor_noticias": "article.jeg_post",
        "seletor_titulo": "h3.jeg_post_title a",
        "seletor_link": "h3.jeg_post_title a",
        "seletor_data": "div.jeg_meta_date a",
        "seletor_resumo": "div.jeg_post_excerpt p",
        "formato_data": "%d de %B de %Y",
        "idioma": "pt",
        "confiabilidade": 7  # Escala de 1-10
    },

    # Portais internacionais (confiáveis)
    {
        "nome": "CoinDesk",
        "url": "https://www.coindesk.com/",
        "seletor_noticias": "div.article-cardstyles__AcRoot-sc-q1x8lc-1",
        "seletor_titulo": "h6.typography__StyledTypography-sc-owin6q-0",
        "seletor_link": "a.card-title",
        "seletor_data": "span.typography__StyledTypography-sc-owin6q-0",
        "seletor_resumo": "p.typography__StyledTypography-sc-owin6q-0",
        "formato_data": "%b %d, %Y",
        "idioma": "en",
        "confiabilidade": 9  # Escala de 1-10
    },
    {
        "nome": "Cointelegraph",
        "url": "https://cointelegraph.com/",
        "seletor_noticias": "article.post-card",
        "seletor_titulo": "span.post-card__title-text",
        "seletor_link": "a.post-card__title-link",
        "seletor_data": "time.post-card__date",
        "seletor_resumo": "p.post-card__text",
        "formato_data": "%m/%d/%Y",
        "idioma": "en",
        "confiabilidade": 8  # Escala de 1-10
    },
    {
        "nome": "Bitcoin Magazine",
        "url": "https://bitcoinmagazine.com/",
        "seletor_noticias": "article.article-card",
        "seletor_titulo": "h3.article-card__title a",
        "seletor_link": "h3.article-card__title a",
        "seletor_data": "time.article-card__date",
        "seletor_resumo": "p.article-card__excerpt",
        "formato_data": "%B %d, %Y",
        "idioma": "en",
        "confiabilidade": 9  # Escala de 1-10
    },
    {
        "nome": "Decrypt",
        "url": "https://decrypt.co/",
        "seletor_noticias": "article.styledArticle",
        "seletor_titulo": "h3.styledHeading a",
        "seletor_link": "h3.styledHeading a",
        "seletor_data": "time.styledTime",
        "seletor_resumo": "p.styledExcerpt",
        "formato_data": "%B %d, %Y",
        "idioma": "en",
        "confiabilidade": 8  # Escala de 1-10
    }
]

# Lista de palavras-chave que podem indicar notícias falsas ou sensacionalistas
PALAVRAS_SUSPEITAS = [
    "golpe garantido", "lucro garantido", "enriqueça rápido", "ganhe dinheiro fácil",
    "segredo revelado", "ninguém está falando sobre", "os bancos odeiam",
    "governo não quer que você saiba", "proibido", "censurado",
    "esquema infalível", "retorno garantido", "investimento sem risco",
    "exclusivo", "revolucionário", "milagroso", "inacreditável",
    "chocante", "surpreendente", "você não vai acreditar"
]

# Lista de domínios conhecidos por espalhar notícias falsas sobre criptomoedas
DOMINIOS_SUSPEITOS = [
    "crypto-scam.com", "get-rich-crypto.com", "bitcoin-millionaire-secret.com",
    "crypto-ponzi-scheme.com", "fake-crypto-news.com", "scam-ico-alerts.com"
]

class NoticiasCriptoScraper:
    """
    Classe para buscar notícias sobre criptomoedas em portais especializados.
    """
    def __init__(self, user_agent: str = None, cache_dir: str = "cache", traduzir_automaticamente: bool = True):
        """
        Inicializa o scraper de notícias.

        Args:
            user_agent: User-Agent a ser usado nas requisições
            cache_dir: Diretório para armazenar o cache de notícias
            traduzir_automaticamente: Se True, traduz automaticamente notícias em outros idiomas
        """
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.cache_dir = cache_dir
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self.traduzir_automaticamente = traduzir_automaticamente

        # Inicializar o tradutor
        self.translator = Translator()

        # Criar diretório de cache se não existir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_path(self, portal_nome: str) -> str:
        """
        Retorna o caminho para o arquivo de cache de um portal.

        Args:
            portal_nome: Nome do portal

        Returns:
            str: Caminho para o arquivo de cache
        """
        return os.path.join(self.cache_dir, f"{portal_nome.lower().replace(' ', '_')}_cache.json")

    def _load_cache(self, portal_nome: str) -> List[Dict[str, Any]]:
        """
        Carrega o cache de notícias de um portal.

        Args:
            portal_nome: Nome do portal

        Returns:
            List[Dict[str, Any]]: Lista de notícias em cache
        """
        cache_path = self._get_cache_path(portal_nome)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar cache para {portal_nome}: {e}")
        return []

    def _save_cache(self, portal_nome: str, noticias: List[Dict[str, Any]]) -> None:
        """
        Salva o cache de notícias de um portal.

        Args:
            portal_nome: Nome do portal
            noticias: Lista de notícias a serem salvas
        """
        cache_path = self._get_cache_path(portal_nome)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(noticias, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar cache para {portal_nome}: {e}")

    def _parse_data(self, data_str: str, formato: str) -> Optional[datetime]:
        """
        Converte uma string de data para um objeto datetime.

        Args:
            data_str: String contendo a data
            formato: Formato da data

        Returns:
            Optional[datetime]: Objeto datetime ou None se falhar
        """
        try:
            # Substituir nomes de meses em português
            meses = {
                'janeiro': 'January',
                'fevereiro': 'February',
                'março': 'March',
                'abril': 'April',
                'maio': 'May',
                'junho': 'June',
                'julho': 'July',
                'agosto': 'August',
                'setembro': 'September',
                'outubro': 'October',
                'novembro': 'November',
                'dezembro': 'December'
            }

            data_str = data_str.lower()
            for mes_pt, mes_en in meses.items():
                data_str = data_str.replace(mes_pt, mes_en)

            # Tentar converter a data
            return datetime.strptime(data_str, formato.replace('%B', 'B'))
        except Exception as e:
            logger.warning(f"Erro ao converter data '{data_str}': {e}")
            return None

    def _traduzir_noticia(self, noticia: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traduz uma notícia para português, se necessário.

        Args:
            noticia: Dados da notícia

        Returns:
            Dict[str, Any]: Notícia traduzida
        """
        if not self.traduzir_automaticamente:
            return noticia

        # Se a notícia já está em português, não precisa traduzir
        if noticia.get("idioma", "pt") == "pt":
            return noticia

        try:
            # Traduzir título
            titulo_traduzido = self.translator.translate(
                noticia["titulo"], src=noticia.get("idioma", "en"), dest="pt"
            ).text

            # Traduzir resumo, se existir
            resumo_traduzido = ""
            if noticia.get("resumo"):
                resumo_traduzido = self.translator.translate(
                    noticia["resumo"], src=noticia.get("idioma", "en"), dest="pt"
                ).text

            # Criar cópia da notícia com os campos traduzidos
            noticia_traduzida = noticia.copy()
            noticia_traduzida["titulo_original"] = noticia["titulo"]
            noticia_traduzida["titulo"] = titulo_traduzido

            if resumo_traduzido:
                noticia_traduzida["resumo_original"] = noticia["resumo"]
                noticia_traduzida["resumo"] = resumo_traduzido

            noticia_traduzida["traduzido"] = True
            noticia_traduzida["idioma_original"] = noticia.get("idioma", "en")
            noticia_traduzida["idioma"] = "pt"

            logger.info(f"Notícia traduzida: {noticia['titulo']} -> {titulo_traduzido}")
            return noticia_traduzida
        except Exception as e:
            logger.error(f"Erro ao traduzir notícia: {e}")
            # Em caso de erro, retornar a notícia original
            noticia["traduzido"] = False
            return noticia

    def _verificar_credibilidade(self, noticia: Dict[str, Any], portal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica a credibilidade de uma notícia.

        Args:
            noticia: Dados da notícia
            portal: Configuração do portal

        Returns:
            Dict[str, Any]: Notícia com informações de credibilidade
        """
        # Inicializar pontuação de credibilidade com base na confiabilidade do portal
        credibilidade = portal.get("confiabilidade", 5)
        razoes = []

        # Verificar se o domínio está na lista de suspeitos
        dominio = urlparse(noticia["link"]).netloc
        if any(dominio_suspeito in dominio for dominio_suspeito in DOMINIOS_SUSPEITOS):
            credibilidade -= 5
            razoes.append("Domínio suspeito")

        # Verificar se o título ou resumo contém palavras suspeitas
        texto_completo = (noticia["titulo"] + " " + noticia.get("resumo", "")).lower()
        palavras_encontradas = [palavra for palavra in PALAVRAS_SUSPEITAS if palavra.lower() in texto_completo]

        if palavras_encontradas:
            credibilidade -= len(palavras_encontradas)
            razoes.append(f"Contém {len(palavras_encontradas)} termos sensacionalistas")

        # Verificar se a notícia tem data (notícias sem data são menos confiáveis)
        if not noticia.get("data_iso"):
            credibilidade -= 1
            razoes.append("Sem data definida")

        # Verificar se o título é muito sensacionalista (todo em maiúsculas, muitas exclamações)
        if noticia["titulo"].isupper() or noticia["titulo"].count("!") > 1:
            credibilidade -= 2
            razoes.append("Título sensacionalista")

        # Limitar a pontuação entre 0 e 10
        credibilidade = max(0, min(10, credibilidade))

        # Adicionar informações de credibilidade à notícia
        noticia["credibilidade"] = credibilidade
        noticia["razoes_credibilidade"] = razoes
        noticia["confiavel"] = credibilidade >= 6  # Consideramos confiável se a pontuação for 6 ou mais

        return noticia

    def _extrair_noticias(self, portal: Dict[str, str], html: str) -> List[Dict[str, Any]]:
        """
        Extrai notícias do HTML de um portal.

        Args:
            portal: Configuração do portal
            html: HTML da página

        Returns:
            List[Dict[str, Any]]: Lista de notícias extraídas
        """
        noticias = []
        soup = BeautifulSoup(html, 'html.parser')

        # Encontrar elementos de notícias
        elementos_noticias = soup.select(portal["seletor_noticias"])

        for elemento in elementos_noticias:
            try:
                # Extrair título
                titulo_elem = elemento.select_one(portal["seletor_titulo"])
                if not titulo_elem:
                    continue
                titulo = titulo_elem.get_text().strip()

                # Extrair link
                link_elem = elemento.select_one(portal["seletor_link"])
                if not link_elem:
                    continue
                link = link_elem.get('href')

                # Garantir que o link seja absoluto
                if link and not link.startswith(('http://', 'https://')):
                    parsed_url = urlparse(portal["url"])
                    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    link = f"{base_url}{link if link.startswith('/') else '/' + link}"

                # Extrair data
                data_elem = elemento.select_one(portal["seletor_data"])
                data_str = data_elem.get_text().strip() if data_elem else ""
                data_obj = self._parse_data(data_str, portal["formato_data"]) if data_str else None
                data_iso = data_obj.isoformat() if data_obj else None

                # Extrair resumo
                resumo_elem = elemento.select_one(portal["seletor_resumo"])
                resumo = resumo_elem.get_text().strip() if resumo_elem else ""

                # Criar objeto de notícia
                noticia = {
                    "titulo": titulo,
                    "link": link,
                    "data": data_str,
                    "data_iso": data_iso,
                    "resumo": resumo,
                    "portal": portal["nome"],
                    "idioma": portal.get("idioma", "pt"),
                    "timestamp": datetime.now().isoformat()
                }

                # Verificar credibilidade da notícia
                noticia = self._verificar_credibilidade(noticia, portal)

                # Adicionar à lista apenas se for confiável
                if noticia["confiavel"]:
                    # Traduzir notícia se necessário
                    if portal.get("idioma", "pt") != "pt" and self.traduzir_automaticamente:
                        noticia = self._traduzir_noticia(noticia)

                    noticias.append(noticia)
                else:
                    logger.warning(f"Notícia descartada por baixa credibilidade: {noticia['titulo']} (Pontuação: {noticia['credibilidade']})")
                    logger.warning(f"Razões: {', '.join(noticia['razoes_credibilidade'])}")
            except Exception as e:
                logger.error(f"Erro ao extrair notícia de {portal['nome']}: {e}")

        return noticias

    def buscar_noticias(self, portal: Dict[str, str], max_noticias: int = 10) -> List[Dict[str, Any]]:
        """
        Busca notícias em um portal específico.

        Args:
            portal: Configuração do portal
            max_noticias: Número máximo de notícias a retornar

        Returns:
            List[Dict[str, Any]]: Lista de notícias encontradas
        """
        logger.info(f"Buscando notícias em {portal['nome']}...")

        try:
            # Fazer requisição HTTP
            response = self.session.get(portal["url"], timeout=30)
            response.raise_for_status()

            # Extrair notícias
            noticias = self._extrair_noticias(portal, response.text)

            # Carregar cache
            cache = self._load_cache(portal["nome"])

            # Filtrar notícias já existentes no cache
            links_cache = {noticia["link"] for noticia in cache}
            noticias_novas = [noticia for noticia in noticias if noticia["link"] not in links_cache]

            # Atualizar cache
            cache = noticias_novas + cache
            cache = cache[:100]  # Manter apenas as 100 notícias mais recentes
            self._save_cache(portal["nome"], cache)

            logger.info(f"Encontradas {len(noticias_novas)} notícias novas em {portal['nome']}")

            # Retornar as notícias mais recentes
            return noticias[:max_noticias]
        except Exception as e:
            logger.error(f"Erro ao buscar notícias em {portal['nome']}: {e}")
            return []

    def buscar_todas_noticias(self, max_por_portal: int = 5, max_total: int = 20,
                          dias_max: int = 7, usar_verificacao_cruzada: bool = True) -> List[Dict[str, Any]]:
        """
        Busca notícias em todos os portais configurados, filtrando por data.

        Args:
            max_por_portal: Número máximo de notícias por portal
            max_total: Número máximo de notícias no total
            dias_max: Número máximo de dias de antiguidade das notícias
            usar_verificacao_cruzada: Se True, usa o sistema de verificação cruzada para melhorar a confiabilidade

        Returns:
            List[Dict[str, Any]]: Lista de notícias encontradas
        """
        todas_noticias = []

        # Calcular a data limite (hoje - dias_max)
        data_limite = datetime.now() - timedelta(days=dias_max)
        data_limite_iso = data_limite.isoformat()

        logger.info(f"Buscando notícias mais recentes que {data_limite.strftime('%d/%m/%Y')}")

        for portal in PORTAIS:
            # Adicionar um pequeno atraso para não sobrecarregar os servidores
            time.sleep(random.uniform(1, 3))

            noticias = self.buscar_noticias(portal, max_por_portal * 2)  # Buscar mais para compensar filtragem

            # Filtrar notícias pela data
            noticias_recentes = []
            for noticia in noticias:
                # Se não tiver data, assumir que é recente
                if not noticia.get("data_iso"):
                    noticias_recentes.append(noticia)
                    continue

                # Verificar se a data é mais recente que o limite
                if noticia["data_iso"] >= data_limite_iso:
                    noticias_recentes.append(noticia)

            logger.info(f"Portal {portal['nome']}: {len(noticias)} notícias encontradas, {len(noticias_recentes)} dentro do período de {dias_max} dias")

            todas_noticias.extend(noticias_recentes[:max_por_portal])  # Limitar ao máximo por portal

            # Parar se já tivermos notícias suficientes (coletamos mais para fazer a verificação cruzada)
            if len(todas_noticias) >= max_total * 2:
                break

        # Aplicar verificação cruzada se disponível e solicitada
        if VERIFICADOR_DISPONIVEL and usar_verificacao_cruzada and len(todas_noticias) > 1:
            logger.info("Aplicando verificação cruzada para melhorar a confiabilidade das notícias...")
            verificador = VerificadorNoticias()
            todas_noticias = verificador.verificar_noticias(todas_noticias)

            # Filtrar notícias com base na credibilidade atualizada
            todas_noticias = [n for n in todas_noticias if n.get('confiavel', False)]

            logger.info(f"Após verificação cruzada: {len(todas_noticias)} notícias confiáveis")
        else:
            # Se não usar verificação cruzada, ordenar por credibilidade original
            todas_noticias.sort(key=lambda x: x.get("credibilidade", 0), reverse=True)

            # Filtrar notícias não confiáveis
            todas_noticias = [n for n in todas_noticias if n.get('confiavel', False)]

        # Ordenar por data (mais recentes primeiro) e depois por credibilidade
        todas_noticias.sort(key=lambda x: (x.get("data_iso", ""), x.get("credibilidade", 0)), reverse=True)

        # Limitar ao número máximo de notícias
        return todas_noticias[:max_total]

def main():
    """
    Função principal para testar o buscador de notícias.
    """
    import argparse

    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Buscador de notícias sobre criptomoedas")
    parser.add_argument("--max", type=int, default=20, help="Número máximo de notícias a buscar")
    parser.add_argument("--dias", type=int, default=7, help="Número máximo de dias de antiguidade das notícias")
    parser.add_argument("--no-traduzir", action="store_true", help="Não traduzir notícias automaticamente")
    parser.add_argument("--min-credibilidade", type=int, default=6, help="Pontuação mínima de credibilidade (1-10)")
    parser.add_argument("--no-verificacao-cruzada", action="store_true", help="Desativar verificação cruzada de notícias")
    parser.add_argument("--limiar-similaridade", type=float, default=0.7, help="Limiar de similaridade para verificação cruzada (0.0-1.0)")

    args = parser.parse_args()

    # Criar o scraper
    scraper = NoticiasCriptoScraper(traduzir_automaticamente=not args.no_traduzir)

    # Buscar notícias
    noticias = scraper.buscar_todas_noticias(
        max_total=args.max,
        dias_max=args.dias,
        usar_verificacao_cruzada=not args.no_verificacao_cruzada
    )

    # Exibir as notícias encontradas
    print(f"\nEncontradas {len(noticias)} notícias sobre criptomoedas:\n")

    if VERIFICADOR_DISPONIVEL and not args.no_verificacao_cruzada:
        print("Verificação cruzada: ATIVADA")
    else:
        print("Verificação cruzada: DESATIVADA")

    for i, noticia in enumerate(noticias, 1):
        # Mostrar informações de tradução, se aplicável
        titulo_display = noticia['titulo']
        if noticia.get('traduzido'):
            titulo_display += f" [Traduzido de: {noticia.get('idioma_original', 'en')}]"

        # Mostrar informações de credibilidade
        credibilidade_info = f"[Credibilidade: {noticia.get('credibilidade', 'N/A')}/10]"

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

        print(f"{i}. {titulo_display} {credibilidade_info}{cruzamento_info}")
        print(f"   Portal: {noticia['portal']}")
        print(f"   Data: {noticia['data']}")
        print(f"   Link: {noticia['link']}")

        if noticia.get('resumo'):
            resumo_display = noticia['resumo'][:150]
            if len(noticia['resumo']) > 150:
                resumo_display += "..."
            print(f"   Resumo: {resumo_display}")

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
