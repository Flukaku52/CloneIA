#!/usr/bin/env python3
"""
Gerenciador de fontes confiáveis para o sistema de cruzamento de informações.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional, Set, Tuple

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('trusted_sources_manager')

class TrustedSourcesManager:
    """
    Classe para gerenciar fontes confiáveis de informação.
    """
    def __init__(self, config_path: str = "config/trusted_sources.json"):
        """
        Inicializa o gerenciador de fontes confiáveis.
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config_path = config_path
        self.sources = self._load_sources()
        
        # Cache para pesquisas rápidas
        self._twitter_accounts_cache = {}
        self._websites_cache = {}
        
        # Inicializar caches
        self._build_caches()
        
        logger.info(f"Gerenciador de fontes confiáveis inicializado com {len(self.get_twitter_accounts())} contas do Twitter e {len(self.get_websites())} websites")
    
    def _load_sources(self) -> Dict[str, Any]:
        """
        Carrega as fontes confiáveis do arquivo de configuração.
        
        Returns:
            Dict[str, Any]: Dados das fontes confiáveis
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Arquivo de configuração não encontrado: {self.config_path}")
                return {"twitter": {"accounts": []}, "websites": {"portais": []}}
        except Exception as e:
            logger.error(f"Erro ao carregar fontes confiáveis: {e}")
            return {"twitter": {"accounts": []}, "websites": {"portais": []}}
    
    def _save_sources(self) -> bool:
        """
        Salva as fontes confiáveis no arquivo de configuração.
        
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            # Garantir que o diretório existe
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.sources, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Fontes confiáveis salvas em {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar fontes confiáveis: {e}")
            return False
    
    def _build_caches(self) -> None:
        """
        Constrói caches para pesquisas rápidas.
        """
        # Cache de contas do Twitter
        self._twitter_accounts_cache = {
            account["username"].lower(): account
            for account in self.sources.get("twitter", {}).get("accounts", [])
        }
        
        # Cache de websites
        self._websites_cache = {
            portal["url"].lower(): portal
            for portal in self.sources.get("websites", {}).get("portais", [])
        }
    
    def get_twitter_accounts(self) -> List[Dict[str, Any]]:
        """
        Retorna todas as contas do Twitter confiáveis.
        
        Returns:
            List[Dict[str, Any]]: Lista de contas do Twitter
        """
        return self.sources.get("twitter", {}).get("accounts", [])
    
    def get_websites(self) -> List[Dict[str, Any]]:
        """
        Retorna todos os websites confiáveis.
        
        Returns:
            List[Dict[str, Any]]: Lista de websites
        """
        return self.sources.get("websites", {}).get("portais", [])
    
    def get_twitter_account(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Retorna informações sobre uma conta do Twitter.
        
        Args:
            username: Nome de usuário da conta
            
        Returns:
            Optional[Dict[str, Any]]: Informações da conta ou None se não encontrada
        """
        return self._twitter_accounts_cache.get(username.lower())
    
    def get_website(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retorna informações sobre um website.
        
        Args:
            url: URL do website
            
        Returns:
            Optional[Dict[str, Any]]: Informações do website ou None se não encontrado
        """
        # Normalizar URL para comparação
        url_lower = url.lower()
        
        # Verificar correspondência exata
        if url_lower in self._websites_cache:
            return self._websites_cache[url_lower]
        
        # Verificar correspondência parcial (domínio)
        for website_url, website in self._websites_cache.items():
            if url_lower.startswith(website_url) or website_url in url_lower:
                return website
        
        return None
    
    def add_twitter_account(self, account_data: Dict[str, Any]) -> bool:
        """
        Adiciona uma nova conta do Twitter à lista de fontes confiáveis.
        
        Args:
            account_data: Dados da conta
            
        Returns:
            bool: True se adicionou com sucesso, False caso contrário
        """
        try:
            # Verificar se a conta já existe
            username = account_data.get("username", "").lower()
            if not username:
                logger.error("Nome de usuário não fornecido")
                return False
            
            if username in self._twitter_accounts_cache:
                logger.warning(f"Conta do Twitter já existe: {username}")
                return False
            
            # Adicionar a conta
            self.sources.setdefault("twitter", {}).setdefault("accounts", []).append(account_data)
            
            # Atualizar cache
            self._twitter_accounts_cache[username] = account_data
            
            # Salvar alterações
            return self._save_sources()
        except Exception as e:
            logger.error(f"Erro ao adicionar conta do Twitter: {e}")
            return False
    
    def add_website(self, website_data: Dict[str, Any]) -> bool:
        """
        Adiciona um novo website à lista de fontes confiáveis.
        
        Args:
            website_data: Dados do website
            
        Returns:
            bool: True se adicionou com sucesso, False caso contrário
        """
        try:
            # Verificar se o website já existe
            url = website_data.get("url", "").lower()
            if not url:
                logger.error("URL não fornecida")
                return False
            
            if url in self._websites_cache:
                logger.warning(f"Website já existe: {url}")
                return False
            
            # Adicionar o website
            self.sources.setdefault("websites", {}).setdefault("portais", []).append(website_data)
            
            # Atualizar cache
            self._websites_cache[url] = website_data
            
            # Salvar alterações
            return self._save_sources()
        except Exception as e:
            logger.error(f"Erro ao adicionar website: {e}")
            return False
    
    def update_twitter_account(self, username: str, account_data: Dict[str, Any]) -> bool:
        """
        Atualiza uma conta do Twitter existente.
        
        Args:
            username: Nome de usuário da conta
            account_data: Novos dados da conta
            
        Returns:
            bool: True se atualizou com sucesso, False caso contrário
        """
        try:
            username_lower = username.lower()
            
            # Verificar se a conta existe
            if username_lower not in self._twitter_accounts_cache:
                logger.warning(f"Conta do Twitter não encontrada: {username}")
                return False
            
            # Atualizar a conta
            accounts = self.sources.get("twitter", {}).get("accounts", [])
            for i, account in enumerate(accounts):
                if account["username"].lower() == username_lower:
                    accounts[i] = account_data
                    break
            
            # Atualizar cache
            self._twitter_accounts_cache[username_lower] = account_data
            
            # Salvar alterações
            return self._save_sources()
        except Exception as e:
            logger.error(f"Erro ao atualizar conta do Twitter: {e}")
            return False
    
    def update_website(self, url: str, website_data: Dict[str, Any]) -> bool:
        """
        Atualiza um website existente.
        
        Args:
            url: URL do website
            website_data: Novos dados do website
            
        Returns:
            bool: True se atualizou com sucesso, False caso contrário
        """
        try:
            url_lower = url.lower()
            
            # Verificar se o website existe
            if url_lower not in self._websites_cache:
                logger.warning(f"Website não encontrado: {url}")
                return False
            
            # Atualizar o website
            portais = self.sources.get("websites", {}).get("portais", [])
            for i, portal in enumerate(portais):
                if portal["url"].lower() == url_lower:
                    portais[i] = website_data
                    break
            
            # Atualizar cache
            self._websites_cache[url_lower] = website_data
            
            # Salvar alterações
            return self._save_sources()
        except Exception as e:
            logger.error(f"Erro ao atualizar website: {e}")
            return False
    
    def remove_twitter_account(self, username: str) -> bool:
        """
        Remove uma conta do Twitter da lista de fontes confiáveis.
        
        Args:
            username: Nome de usuário da conta
            
        Returns:
            bool: True se removeu com sucesso, False caso contrário
        """
        try:
            username_lower = username.lower()
            
            # Verificar se a conta existe
            if username_lower not in self._twitter_accounts_cache:
                logger.warning(f"Conta do Twitter não encontrada: {username}")
                return False
            
            # Remover a conta
            accounts = self.sources.get("twitter", {}).get("accounts", [])
            self.sources["twitter"]["accounts"] = [
                account for account in accounts
                if account["username"].lower() != username_lower
            ]
            
            # Atualizar cache
            del self._twitter_accounts_cache[username_lower]
            
            # Salvar alterações
            return self._save_sources()
        except Exception as e:
            logger.error(f"Erro ao remover conta do Twitter: {e}")
            return False
    
    def remove_website(self, url: str) -> bool:
        """
        Remove um website da lista de fontes confiáveis.
        
        Args:
            url: URL do website
            
        Returns:
            bool: True se removeu com sucesso, False caso contrário
        """
        try:
            url_lower = url.lower()
            
            # Verificar se o website existe
            if url_lower not in self._websites_cache:
                logger.warning(f"Website não encontrado: {url}")
                return False
            
            # Remover o website
            portais = self.sources.get("websites", {}).get("portais", [])
            self.sources["websites"]["portais"] = [
                portal for portal in portais
                if portal["url"].lower() != url_lower
            ]
            
            # Atualizar cache
            del self._websites_cache[url_lower]
            
            # Salvar alterações
            return self._save_sources()
        except Exception as e:
            logger.error(f"Erro ao remover website: {e}")
            return False
    
    def get_source_confiabilidade(self, source_type: str, identifier: str) -> int:
        """
        Retorna a pontuação de confiabilidade de uma fonte.
        
        Args:
            source_type: Tipo de fonte ('twitter' ou 'website')
            identifier: Identificador da fonte (username ou URL)
            
        Returns:
            int: Pontuação de confiabilidade (0-10) ou 0 se não encontrada
        """
        if source_type == "twitter":
            account = self.get_twitter_account(identifier)
            return account.get("confiabilidade", 0) if account else 0
        elif source_type == "website":
            website = self.get_website(identifier)
            return website.get("confiabilidade", 0) if website else 0
        else:
            return 0
