#!/usr/bin/env python3
"""
Script para extrair dados dos Reels da Rapidinha no Instagram.
Este script é executado localmente pelo usuário, sem compartilhar credenciais.
"""
import os
import json
import time
import logging
import argparse
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('instagram_data_extractor')

class InstagramDataExtractor:
    """
    Classe para extrair dados dos Reels do Instagram.
    """
    def __init__(self, 
                 access_token: str = None, 
                 instagram_account_id: str = None,
                 config_file: str = "config/instagram_config.json",
                 output_dir: str = "output/instagram_data"):
        """
        Inicializa o extrator de dados do Instagram.
        
        Args:
            access_token: Token de acesso à API do Instagram Graph
            instagram_account_id: ID da conta do Instagram
            config_file: Caminho para o arquivo de configuração
            output_dir: Diretório para salvar os dados extraídos
        """
        # Carregar configurações do arquivo se não fornecidas diretamente
        if not (access_token and instagram_account_id):
            self._load_config(config_file)
        else:
            self.access_token = access_token
            self.instagram_account_id = instagram_account_id
        
        self.api_version = "v18.0"  # Versão atual da API do Graph
        self.api_base_url = f"https://graph.facebook.com/{self.api_version}"
        self.output_dir = output_dir
        
        # Criar diretório de saída se não existir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _load_config(self, config_file: str) -> None:
        """
        Carrega as configurações do arquivo.
        
        Args:
            config_file: Caminho para o arquivo de configuração
        """
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.access_token = config.get("access_token")
                self.instagram_account_id = config.get("instagram_account_id")
                
                logger.info("Configurações do Instagram carregadas com sucesso.")
            else:
                # Tentar carregar de variáveis de ambiente
                self.access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
                self.instagram_account_id = os.environ.get("INSTAGRAM_ACCOUNT_ID")
                
                if self.access_token and self.instagram_account_id:
                    logger.info("Configurações do Instagram carregadas das variáveis de ambiente.")
                else:
                    logger.warning(f"Arquivo de configuração não encontrado: {config_file}")
                    self.access_token = None
                    self.instagram_account_id = None
        except Exception as e:
            logger.error(f"Erro ao carregar configurações do Instagram: {e}")
            self.access_token = None
            self.instagram_account_id = None
    
    def check_auth_status(self) -> bool:
        """
        Verifica se a autenticação está configurada e válida.
        
        Returns:
            bool: True se a autenticação está configurada e válida, False caso contrário
        """
        if not (self.access_token and self.instagram_account_id):
            logger.warning("Credenciais do Instagram não configuradas.")
            return False
        
        try:
            # Testar a API com uma chamada simples
            url = f"{self.api_base_url}/{self.instagram_account_id}"
            params = {
                "fields": "username",
                "access_token": self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Autenticação válida para a conta: {data.get('username', 'desconhecido')}")
                return True
            else:
                logger.warning(f"Falha na autenticação: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Erro ao verificar autenticação: {e}")
            return False
    
    def get_media_list(self, limit: int = 50, media_type: str = "REELS") -> List[Dict[str, Any]]:
        """
        Obtém a lista de mídias da conta do Instagram.
        
        Args:
            limit: Número máximo de mídias a retornar
            media_type: Tipo de mídia a buscar (REELS, IMAGE, VIDEO, CAROUSEL_ALBUM)
            
        Returns:
            List[Dict[str, Any]]: Lista de mídias
        """
        if not self.check_auth_status():
            logger.error("Autenticação inválida. Não é possível obter a lista de mídias.")
            return []
        
        try:
            url = f"{self.api_base_url}/{self.instagram_account_id}/media"
            params = {
                "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username,comments_count,like_count",
                "access_token": self.access_token,
                "limit": limit
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                logger.error(f"Erro ao obter lista de mídias: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            media_list = data.get("data", [])
            
            # Filtrar por tipo de mídia, se especificado
            if media_type:
                media_list = [m for m in media_list if m.get("media_type") == media_type]
            
            logger.info(f"Obtidas {len(media_list)} mídias do tipo {media_type}")
            return media_list
        
        except Exception as e:
            logger.error(f"Erro ao obter lista de mídias: {e}")
            return []
    
    def get_media_details(self, media_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém detalhes de uma mídia específica.
        
        Args:
            media_id: ID da mídia
            
        Returns:
            Optional[Dict[str, Any]]: Detalhes da mídia, ou None se falhar
        """
        if not self.check_auth_status():
            logger.error("Autenticação inválida. Não é possível obter detalhes da mídia.")
            return None
        
        try:
            url = f"{self.api_base_url}/{media_id}"
            params = {
                "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username,comments_count,like_count,comments{text,username,timestamp}",
                "access_token": self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                logger.error(f"Erro ao obter detalhes da mídia: {response.status_code} - {response.text}")
                return None
            
            return response.json()
        
        except Exception as e:
            logger.error(f"Erro ao obter detalhes da mídia: {e}")
            return None
    
    def extract_reels_data(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Extrai dados dos Reels da conta do Instagram.
        
        Args:
            limit: Número máximo de Reels a extrair
            
        Returns:
            List[Dict[str, Any]]: Dados dos Reels
        """
        # Obter lista de Reels
        reels_list = self.get_media_list(limit=limit, media_type="REELS")
        
        if not reels_list:
            logger.warning("Nenhum Reel encontrado.")
            return []
        
        # Obter detalhes de cada Reel
        reels_data = []
        
        for reel in reels_list:
            # Adicionar um pequeno atraso para não sobrecarregar a API
            time.sleep(1)
            
            reel_id = reel.get("id")
            reel_details = self.get_media_details(reel_id)
            
            if reel_details:
                reels_data.append(reel_details)
        
        logger.info(f"Extraídos dados de {len(reels_data)} Reels")
        return reels_data
    
    def save_reels_data(self, reels_data: List[Dict[str, Any]], filename: str = None) -> str:
        """
        Salva os dados dos Reels em um arquivo JSON.
        
        Args:
            reels_data: Dados dos Reels
            filename: Nome do arquivo (opcional)
            
        Returns:
            str: Caminho para o arquivo salvo
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instagram_reels_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Extrair apenas os dados relevantes
        simplified_data = []
        
        for reel in reels_data:
            simplified_reel = {
                "id": reel.get("id"),
                "caption": reel.get("caption"),
                "permalink": reel.get("permalink"),
                "timestamp": reel.get("timestamp"),
                "like_count": reel.get("like_count"),
                "comments_count": reel.get("comments_count"),
                "comments": []
            }
            
            # Extrair comentários
            comments_data = reel.get("comments", {}).get("data", [])
            for comment in comments_data:
                simplified_reel["comments"].append({
                    "text": comment.get("text"),
                    "username": comment.get("username"),
                    "timestamp": comment.get("timestamp")
                })
            
            simplified_data.append(simplified_reel)
        
        # Salvar no arquivo
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(simplified_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dados dos Reels salvos em: {filepath}")
        return filepath

def main():
    """
    Função principal para extrair dados dos Reels do Instagram.
    """
    parser = argparse.ArgumentParser(description="Extrator de dados dos Reels do Instagram")
    parser.add_argument("--config", default="config/instagram_config.json", help="Arquivo de configuração do Instagram")
    parser.add_argument("--output-dir", default="output/instagram_data", help="Diretório para salvar os dados extraídos")
    parser.add_argument("--limit", type=int, default=50, help="Número máximo de Reels a extrair")
    parser.add_argument("--token", help="Token de acesso à API do Instagram Graph (opcional)")
    parser.add_argument("--account-id", help="ID da conta do Instagram (opcional)")
    
    args = parser.parse_args()
    
    # Criar o extrator
    extractor = InstagramDataExtractor(
        access_token=args.token,
        instagram_account_id=args.account_id,
        config_file=args.config,
        output_dir=args.output_dir
    )
    
    # Verificar autenticação
    if not extractor.check_auth_status():
        logger.error("Falha na autenticação. Verifique suas credenciais.")
        return 1
    
    # Extrair dados dos Reels
    reels_data = extractor.extract_reels_data(limit=args.limit)
    
    if not reels_data:
        logger.error("Nenhum dado de Reel extraído.")
        return 1
    
    # Salvar dados
    filepath = extractor.save_reels_data(reels_data)
    
    print(f"\nDados extraídos com sucesso e salvos em: {filepath}")
    print(f"Total de Reels extraídos: {len(reels_data)}")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
