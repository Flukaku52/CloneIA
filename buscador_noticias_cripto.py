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
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('buscador_noticias_cripto')

# Lista de portais de notícias sobre criptomoedas
PORTAIS = [
    {
        "nome": "CriptoFácil",
        "url": "https://www.criptofacil.com/ultimas-noticias/",
        "seletor_noticias": "article.jeg_post",
        "seletor_titulo": "h3.jeg_post_title a",
        "seletor_link": "h3.jeg_post_title a",
        "seletor_data": "div.jeg_meta_date a",
        "seletor_resumo": "div.jeg_post_excerpt p",
        "formato_data": "%d de %B de %Y"
    },
    {
        "nome": "Portal do Bitcoin",
        "url": "https://portaldobitcoin.uol.com.br/",
        "seletor_noticias": "div.td_module_flex",
        "seletor_titulo": "h3.entry-title a",
        "seletor_link": "h3.entry-title a",
        "seletor_data": "time.entry-date",
        "seletor_resumo": "div.td-excerpt",
        "formato_data": "%d de %B de %Y"
    },
    {
        "nome": "Cointelegraph Brasil",
        "url": "https://br.cointelegraph.com/",
        "seletor_noticias": "article.post-card",
        "seletor_titulo": "span.post-card__title-text",
        "seletor_link": "a.post-card__title-link",
        "seletor_data": "time.post-card__date",
        "seletor_resumo": "p.post-card__text",
        "formato_data": "%d/%m/%Y"
    },
    {
        "nome": "Livecoins",
        "url": "https://livecoins.com.br/categoria/bitcoin/",
        "seletor_noticias": "article.jeg_post",
        "seletor_titulo": "h3.jeg_post_title a",
        "seletor_link": "h3.jeg_post_title a",
        "seletor_data": "div.jeg_meta_date a",
        "seletor_resumo": "div.jeg_post_excerpt p",
        "formato_data": "%d de %B de %Y"
    }
]

class NoticiasCriptoScraper:
    """
    Classe para buscar notícias sobre criptomoedas em portais especializados.
    """
    def __init__(self, user_agent: str = None, cache_dir: str = "cache"):
        """
        Inicializa o scraper de notícias.

        Args:
            user_agent: User-Agent a ser usado nas requisições
            cache_dir: Diretório para armazenar o cache de notícias
        """
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.cache_dir = cache_dir
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

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
                    "timestamp": datetime.now().isoformat()
                }

                noticias.append(noticia)
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
                          dias_max: int = 7) -> List[Dict[str, Any]]:
        """
        Busca notícias em todos os portais configurados, filtrando por data.

        Args:
            max_por_portal: Número máximo de notícias por portal
            max_total: Número máximo de notícias no total
            dias_max: Número máximo de dias de antiguidade das notícias

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

            # Parar se já tivermos notícias suficientes
            if len(todas_noticias) >= max_total:
                break

        # Ordenar por data (mais recentes primeiro)
        todas_noticias.sort(key=lambda x: x.get("data_iso", ""), reverse=True)

        # Limitar ao número máximo de notícias
        return todas_noticias[:max_total]

def main():
    """
    Função principal para testar o buscador de notícias.
    """
    # Criar o scraper
    scraper = NoticiasCriptoScraper()

    # Buscar notícias
    noticias = scraper.buscar_todas_noticias()

    # Exibir as notícias encontradas
    print(f"\nEncontradas {len(noticias)} notícias sobre criptomoedas:\n")

    for i, noticia in enumerate(noticias, 1):
        print(f"{i}. {noticia['titulo']}")
        print(f"   Portal: {noticia['portal']}")
        print(f"   Data: {noticia['data']}")
        print(f"   Link: {noticia['link']}")
        if noticia.get('resumo'):
            print(f"   Resumo: {noticia['resumo'][:150]}...")
        print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
