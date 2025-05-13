#!/usr/bin/env python3
"""
Buscador de vídeos sobre criptomoedas no YouTube.
"""
import os
import sys
import json
import time
import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('buscador_videos_cripto')

# Lista de canais confiáveis sobre criptomoedas
CANAIS_CONFIAVEIS = [
    {
        "nome": "Coin Bureau",
        "id": "UCqK_GSMbpiV8spgD3ZGloSw",
        "idioma": "en",
        "confiabilidade": 9
    },
    {
        "nome": "Benjamin Cowen",
        "id": "UCRvqjQPSeaWn-uEx-w0XOIg",
        "idioma": "en",
        "confiabilidade": 9
    },
    {
        "nome": "Cointimes",
        "id": "UCLxRSbcNdBTdqtDbXCkUuZQ",
        "idioma": "pt",
        "confiabilidade": 8
    },
    {
        "nome": "Flukaku",
        "id": "UCnJMIKYPnNXbQXoWJdBqjjw",
        "idioma": "pt",
        "confiabilidade": 8
    },
    {
        "nome": "Crypto Michael",
        "id": "UCxdf_M_QVSsBxhHG1e3_oAg",
        "idioma": "en",
        "confiabilidade": 8
    }
]

# Palavras-chave para busca
TERMOS_BUSCA = [
    "bitcoin", "ethereum", "cripto", "criptomoeda", "blockchain",
    "bitcoin para iniciantes", "como investir em bitcoin", "bitcoin explicado"
]

class YouTubeCriptoScraper:
    """
    Classe para buscar vídeos sobre criptomoedas no YouTube.
    """
    def __init__(self, api_key: str = None, cache_dir: str = "cache", traduzir_automaticamente: bool = True):
        """
        Inicializa o scraper de vídeos.

        Args:
            api_key: Chave da API do YouTube
            cache_dir: Diretório para armazenar o cache de vídeos
            traduzir_automaticamente: Se True, traduz automaticamente vídeos em outros idiomas
        """
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY")
        self.cache_dir = cache_dir
        self.traduzir_automaticamente = traduzir_automaticamente
        
        # Verificar se temos uma chave de API
        if not self.api_key:
            logger.warning("Chave da API do YouTube não configurada. Usando método alternativo.")
            self.usar_api = False
        else:
            self.usar_api = True
        
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

    def _get_cache_path(self, nome: str) -> str:
        """
        Retorna o caminho para o arquivo de cache.

        Args:
            nome: Nome do cache

        Returns:
            str: Caminho para o arquivo de cache
        """
        return os.path.join(self.cache_dir, f"youtube_{nome.lower().replace(' ', '_')}_cache.json")

    def _load_cache(self, nome: str) -> List[Dict[str, Any]]:
        """
        Carrega o cache de vídeos.

        Args:
            nome: Nome do cache

        Returns:
            List[Dict[str, Any]]: Lista de vídeos em cache
        """
        cache_path = self._get_cache_path(nome)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar cache para {nome}: {e}")
        return []

    def _save_cache(self, nome: str, videos: List[Dict[str, Any]]) -> None:
        """
        Salva o cache de vídeos.

        Args:
            nome: Nome do cache
            videos: Lista de vídeos a serem salvos
        """
        cache_path = self._get_cache_path(nome)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(videos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar cache para {nome}: {e}")

    def _traduzir_video(self, video: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traduz um vídeo para português, se necessário.

        Args:
            video: Dados do vídeo

        Returns:
            Dict[str, Any]: Vídeo traduzido
        """
        if not self.traduzir_automaticamente:
            return video

        # Se o vídeo já está em português, não precisa traduzir
        if video.get("idioma", "pt") == "pt":
            return video

        try:
            # Traduzir título
            titulo_traduzido = self.translator.translate(
                video["titulo"], src=video.get("idioma", "en"), dest="pt"
            ).text

            # Traduzir descrição, se existir
            descricao_traduzida = ""
            if video.get("descricao"):
                descricao_traduzida = self.translator.translate(
                    video["descricao"], src=video.get("idioma", "en"), dest="pt"
                ).text

            # Criar cópia do vídeo com os campos traduzidos
            video_traduzido = video.copy()
            video_traduzido["titulo_original"] = video["titulo"]
            video_traduzido["titulo"] = titulo_traduzido
            
            if descricao_traduzida:
                video_traduzido["descricao_original"] = video["descricao"]
                video_traduzido["descricao"] = descricao_traduzida
            
            video_traduzido["traduzido"] = True
            video_traduzido["idioma_original"] = video.get("idioma", "en")
            video_traduzido["idioma"] = "pt"

            logger.info(f"Vídeo traduzido: {video['titulo']} -> {titulo_traduzido}")
            return video_traduzido
        except Exception as e:
            logger.error(f"Erro ao traduzir vídeo: {e}")
            # Em caso de erro, retornar o vídeo original
            video["traduzido"] = False
            return video

    def buscar_videos_por_canal(self, canal: Dict[str, Any], max_videos: int = 5) -> List[Dict[str, Any]]:
        """
        Busca vídeos em um canal específico.

        Args:
            canal: Configuração do canal
            max_videos: Número máximo de vídeos a retornar

        Returns:
            List[Dict[str, Any]]: Lista de vídeos encontrados
        """
        logger.info(f"Buscando vídeos no canal {canal['nome']}...")
        
        # Implementação usando a API do YouTube
        if self.usar_api:
            return self._buscar_videos_por_canal_api(canal, max_videos)
        
        # Implementação alternativa (sem API)
        return self._buscar_videos_por_canal_alternativo(canal, max_videos)

    def _buscar_videos_por_canal_api(self, canal: Dict[str, Any], max_videos: int = 5) -> List[Dict[str, Any]]:
        """
        Busca vídeos em um canal usando a API do YouTube.

        Args:
            canal: Configuração do canal
            max_videos: Número máximo de vídeos a retornar

        Returns:
            List[Dict[str, Any]]: Lista de vídeos encontrados
        """
        try:
            # Construir URL da API
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "key": self.api_key,
                "channelId": canal["id"],
                "part": "snippet",
                "order": "date",
                "maxResults": max_videos * 2,  # Buscar mais para compensar filtragem
                "type": "video"
            }
            
            # Fazer requisição
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extrair vídeos
            videos = []
            for item in data.get("items", []):
                video_id = item["id"]["videoId"]
                snippet = item["snippet"]
                
                video = {
                    "id": video_id,
                    "titulo": snippet["title"],
                    "descricao": snippet["description"],
                    "canal": canal["nome"],
                    "canal_id": canal["id"],
                    "data_publicacao": snippet["publishedAt"],
                    "thumbnail": snippet["thumbnails"]["high"]["url"],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "idioma": canal.get("idioma", "en"),
                    "confiabilidade": canal.get("confiabilidade", 5),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Traduzir se necessário
                if canal.get("idioma") != "pt" and self.traduzir_automaticamente:
                    video = self._traduzir_video(video)
                
                videos.append(video)
            
            return videos[:max_videos]
        except Exception as e:
            logger.error(f"Erro ao buscar vídeos no canal {canal['nome']}: {e}")
            return []

    def _buscar_videos_por_canal_alternativo(self, canal: Dict[str, Any], max_videos: int = 5) -> List[Dict[str, Any]]:
        """
        Busca vídeos em um canal sem usar a API do YouTube (método alternativo).

        Args:
            canal: Configuração do canal
            max_videos: Número máximo de vídeos a retornar

        Returns:
            List[Dict[str, Any]]: Lista de vídeos encontrados
        """
        # Implementação simplificada para quando não temos a API
        # Na prática, seria necessário usar web scraping ou outra abordagem
        logger.warning("Método alternativo de busca não implementado completamente.")
        return []

    def buscar_videos_por_termo(self, termo: str, max_videos: int = 5) -> List[Dict[str, Any]]:
        """
        Busca vídeos por um termo específico.

        Args:
            termo: Termo de busca
            max_videos: Número máximo de vídeos a retornar

        Returns:
            List[Dict[str, Any]]: Lista de vídeos encontrados
        """
        logger.info(f"Buscando vídeos para o termo '{termo}'...")
        
        # Implementação usando a API do YouTube
        if self.usar_api:
            return self._buscar_videos_por_termo_api(termo, max_videos)
        
        # Implementação alternativa (sem API)
        return self._buscar_videos_por_termo_alternativo(termo, max_videos)

    def _buscar_videos_por_termo_api(self, termo: str, max_videos: int = 5) -> List[Dict[str, Any]]:
        """
        Busca vídeos por um termo usando a API do YouTube.

        Args:
            termo: Termo de busca
            max_videos: Número máximo de vídeos a retornar

        Returns:
            List[Dict[str, Any]]: Lista de vídeos encontrados
        """
        try:
            # Construir URL da API
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "key": self.api_key,
                "q": termo,
                "part": "snippet",
                "order": "relevance",
                "maxResults": max_videos * 2,  # Buscar mais para compensar filtragem
                "type": "video",
                "relevanceLanguage": "pt"  # Priorizar conteúdo em português
            }
            
            # Fazer requisição
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extrair vídeos
            videos = []
            for item in data.get("items", []):
                video_id = item["id"]["videoId"]
                snippet = item["snippet"]
                
                # Determinar idioma e confiabilidade
                canal_id = snippet["channelId"]
                canal_info = next((c for c in CANAIS_CONFIAVEIS if c["id"] == canal_id), None)
                
                idioma = "pt" if "pt" in snippet.get("defaultAudioLanguage", "") else "en"
                confiabilidade = 5  # Valor padrão médio
                
                if canal_info:
                    idioma = canal_info.get("idioma", idioma)
                    confiabilidade = canal_info.get("confiabilidade", confiabilidade)
                
                video = {
                    "id": video_id,
                    "titulo": snippet["title"],
                    "descricao": snippet["description"],
                    "canal": snippet["channelTitle"],
                    "canal_id": canal_id,
                    "data_publicacao": snippet["publishedAt"],
                    "thumbnail": snippet["thumbnails"]["high"]["url"],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "idioma": idioma,
                    "confiabilidade": confiabilidade,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Traduzir se necessário
                if idioma != "pt" and self.traduzir_automaticamente:
                    video = self._traduzir_video(video)
                
                videos.append(video)
            
            # Filtrar por confiabilidade
            videos_confiaveis = [v for v in videos if v.get("confiabilidade", 0) >= 6]
            
            # Se não houver vídeos confiáveis suficientes, incluir alguns não confiáveis
            if len(videos_confiaveis) < max_videos:
                videos_restantes = [v for v in videos if v not in videos_confiaveis]
                videos_confiaveis.extend(videos_restantes[:max_videos - len(videos_confiaveis)])
            
            return videos_confiaveis[:max_videos]
        except Exception as e:
            logger.error(f"Erro ao buscar vídeos para o termo '{termo}': {e}")
            return []

    def _buscar_videos_por_termo_alternativo(self, termo: str, max_videos: int = 5) -> List[Dict[str, Any]]:
        """
        Busca vídeos por um termo sem usar a API do YouTube (método alternativo).

        Args:
            termo: Termo de busca
            max_videos: Número máximo de vídeos a retornar

        Returns:
            List[Dict[str, Any]]: Lista de vídeos encontrados
        """
        # Implementação simplificada para quando não temos a API
        # Na prática, seria necessário usar web scraping ou outra abordagem
        logger.warning("Método alternativo de busca não implementado completamente.")
        return []

    def buscar_todos_videos(self, max_por_canal: int = 2, max_por_termo: int = 3, max_total: int = 10,
                         dias_max: int = 30) -> List[Dict[str, Any]]:
        """
        Busca vídeos em todos os canais e termos configurados, filtrando por data.

        Args:
            max_por_canal: Número máximo de vídeos por canal
            max_por_termo: Número máximo de vídeos por termo
            max_total: Número máximo de vídeos no total
            dias_max: Número máximo de dias de antiguidade dos vídeos

        Returns:
            List[Dict[str, Any]]: Lista de vídeos encontrados
        """
        todos_videos = []
        
        # Calcular a data limite (hoje - dias_max)
        data_limite = datetime.now() - timedelta(days=dias_max)
        data_limite_iso = data_limite.isoformat()
        
        logger.info(f"Buscando vídeos mais recentes que {data_limite.strftime('%d/%m/%Y')}")
        
        # Buscar vídeos por canal
        for canal in CANAIS_CONFIAVEIS:
            # Adicionar um pequeno atraso para não sobrecarregar a API
            time.sleep(1)
            
            videos = self.buscar_videos_por_canal(canal, max_por_canal * 2)  # Buscar mais para compensar filtragem
            
            # Filtrar vídeos pela data
            videos_recentes = []
            for video in videos:
                # Se não tiver data, assumir que é recente
                if not video.get("data_publicacao"):
                    videos_recentes.append(video)
                    continue
                
                # Verificar se a data é mais recente que o limite
                if video["data_publicacao"] >= data_limite_iso:
                    videos_recentes.append(video)
            
            logger.info(f"Canal {canal['nome']}: {len(videos)} vídeos encontrados, {len(videos_recentes)} dentro do período de {dias_max} dias")
            
            todos_videos.extend(videos_recentes[:max_por_canal])
            
            # Parar se já tivermos vídeos suficientes
            if len(todos_videos) >= max_total:
                break
        
        # Buscar vídeos por termo
        for termo in TERMOS_BUSCA:
            # Adicionar um pequeno atraso para não sobrecarregar a API
            time.sleep(1)
            
            videos = self.buscar_videos_por_termo(termo, max_por_termo * 2)  # Buscar mais para compensar filtragem
            
            # Filtrar vídeos pela data
            videos_recentes = []
            for video in videos:
                # Se não tiver data, assumir que é recente
                if not video.get("data_publicacao"):
                    videos_recentes.append(video)
                    continue
                
                # Verificar se a data é mais recente que o limite
                if video["data_publicacao"] >= data_limite_iso:
                    videos_recentes.append(video)
            
            logger.info(f"Termo '{termo}': {len(videos)} vídeos encontrados, {len(videos_recentes)} dentro do período de {dias_max} dias")
            
            todos_videos.extend(videos_recentes[:max_por_termo])
            
            # Parar se já tivermos vídeos suficientes
            if len(todos_videos) >= max_total:
                break
        
        # Remover duplicatas (pelo ID do vídeo)
        videos_unicos = []
        ids_vistos = set()
        for video in todos_videos:
            if video["id"] not in ids_vistos:
                videos_unicos.append(video)
                ids_vistos.add(video["id"])
        
        # Ordenar por data (mais recentes primeiro)
        videos_unicos.sort(key=lambda x: x.get("data_publicacao", ""), reverse=True)
        
        # Limitar ao número máximo de vídeos
        return videos_unicos[:max_total]

def main():
    """
    Função principal para testar o buscador de vídeos.
    """
    import argparse
    
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Buscador de vídeos sobre criptomoedas no YouTube")
    parser.add_argument("--api-key", help="Chave da API do YouTube")
    parser.add_argument("--max", type=int, default=10, help="Número máximo de vídeos a buscar")
    parser.add_argument("--dias", type=int, default=30, help="Número máximo de dias de antiguidade dos vídeos")
    parser.add_argument("--no-traduzir", action="store_true", help="Não traduzir vídeos automaticamente")
    
    args = parser.parse_args()
    
    # Criar o scraper
    scraper = YouTubeCriptoScraper(
        api_key=args.api_key,
        traduzir_automaticamente=not args.no_traduzir
    )
    
    # Buscar vídeos
    videos = scraper.buscar_todos_videos(max_total=args.max, dias_max=args.dias)
    
    # Exibir os vídeos encontrados
    print(f"\nEncontrados {len(videos)} vídeos sobre criptomoedas:\n")
    
    for i, video in enumerate(videos, 1):
        # Mostrar informações de tradução, se aplicável
        titulo_display = video['titulo']
        if video.get('traduzido'):
            titulo_display += f" [Traduzido de: {video.get('idioma_original', 'en')}]"
        
        # Mostrar informações de confiabilidade
        confiabilidade_info = f"[Confiabilidade: {video.get('confiabilidade', 'N/A')}/10]"
        
        print(f"{i}. {titulo_display} {confiabilidade_info}")
        print(f"   Canal: {video['canal']}")
        print(f"   Data: {video.get('data_publicacao', 'N/A')}")
        print(f"   URL: {video['url']}")
        
        if video.get('descricao'):
            descricao_display = video['descricao'][:150]
            if len(video['descricao']) > 150:
                descricao_display += "..."
            print(f"   Descrição: {descricao_display}")
        
        print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
