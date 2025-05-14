#!/usr/bin/env python3
"""
Gerenciador de contas para serviços externos (HeyGen, ElevenLabs, etc.).
"""
import os
import json
import logging
from typing import Dict, Any, Optional, Tuple

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('account_manager')

class AccountManager:
    """
    Classe para gerenciar contas de serviços externos.
    """
    def __init__(self, config_dir: str = "config"):
        """
        Inicializa o gerenciador de contas.
        
        Args:
            config_dir: Diretório onde os arquivos de configuração estão armazenados
        """
        self.config_dir = config_dir
        self.heygen_config_file = os.path.join(config_dir, "heygen_accounts.json")
        self.elevenlabs_config_file = os.path.join(config_dir, "elevenlabs_accounts.json")
        
        # Criar diretório de configuração se não existir
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            logger.info(f"Diretório de configuração criado: {config_dir}")
        
        # Carregar configurações
        self.heygen_accounts = self._load_config(self.heygen_config_file)
        self.elevenlabs_accounts = self._load_config(self.elevenlabs_config_file)
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """
        Carrega configurações de um arquivo JSON.
        
        Args:
            config_file: Caminho para o arquivo de configuração
            
        Returns:
            Dict[str, Any]: Configurações carregadas
        """
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                logger.info(f"Configurações carregadas: {config_file}")
                return config
            except Exception as e:
                logger.error(f"Erro ao carregar configurações: {e}")
                return {"accounts": {}, "active_account": ""}
        else:
            logger.warning(f"Arquivo de configuração não encontrado: {config_file}")
            return {"accounts": {}, "active_account": ""}
    
    def _save_config(self, config: Dict[str, Any], config_file: str) -> bool:
        """
        Salva configurações em um arquivo JSON.
        
        Args:
            config: Configurações a serem salvas
            config_file: Caminho para o arquivo de configuração
            
        Returns:
            bool: True se as configurações foram salvas com sucesso, False caso contrário
        """
        try:
            with open(config_file, "w") as f:
                json.dump(config, f, indent=4)
            logger.info(f"Configurações salvas: {config_file}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            return False
    
    def get_heygen_account(self, account_id: Optional[str] = None) -> Tuple[str, str]:
        """
        Obtém as credenciais da conta HeyGen.
        
        Args:
            account_id: ID da conta (opcional, usa a conta ativa se não for fornecido)
            
        Returns:
            Tuple[str, str]: API key e ID do avatar
        """
        if not account_id:
            account_id = self.heygen_accounts.get("active_account", "")
        
        if not account_id or account_id not in self.heygen_accounts.get("accounts", {}):
            logger.warning(f"Conta HeyGen não encontrada: {account_id}")
            return "", ""
        
        account = self.heygen_accounts["accounts"][account_id]
        return account.get("api_key", ""), account.get("avatar_id", "")
    
    def set_active_heygen_account(self, account_id: str) -> bool:
        """
        Define a conta HeyGen ativa.
        
        Args:
            account_id: ID da conta
            
        Returns:
            bool: True se a conta foi definida com sucesso, False caso contrário
        """
        if account_id not in self.heygen_accounts.get("accounts", {}):
            logger.error(f"Conta HeyGen não encontrada: {account_id}")
            return False
        
        self.heygen_accounts["active_account"] = account_id
        success = self._save_config(self.heygen_accounts, self.heygen_config_file)
        
        if success:
            logger.info(f"Conta HeyGen ativa definida: {account_id}")
        
        return success
    
    def add_heygen_account(self, account_id: str, api_key: str, avatar_id: str, description: str = "") -> bool:
        """
        Adiciona uma nova conta HeyGen.
        
        Args:
            account_id: ID da conta
            api_key: Chave de API
            avatar_id: ID do avatar
            description: Descrição da conta (opcional)
            
        Returns:
            bool: True se a conta foi adicionada com sucesso, False caso contrário
        """
        if "accounts" not in self.heygen_accounts:
            self.heygen_accounts["accounts"] = {}
        
        self.heygen_accounts["accounts"][account_id] = {
            "api_key": api_key,
            "avatar_id": avatar_id,
            "description": description
        }
        
        success = self._save_config(self.heygen_accounts, self.heygen_config_file)
        
        if success:
            logger.info(f"Conta HeyGen adicionada: {account_id}")
        
        return success
    
    def remove_heygen_account(self, account_id: str) -> bool:
        """
        Remove uma conta HeyGen.
        
        Args:
            account_id: ID da conta
            
        Returns:
            bool: True se a conta foi removida com sucesso, False caso contrário
        """
        if account_id not in self.heygen_accounts.get("accounts", {}):
            logger.error(f"Conta HeyGen não encontrada: {account_id}")
            return False
        
        del self.heygen_accounts["accounts"][account_id]
        
        # Se a conta removida era a ativa, definir outra conta como ativa
        if self.heygen_accounts.get("active_account") == account_id:
            if self.heygen_accounts["accounts"]:
                self.heygen_accounts["active_account"] = next(iter(self.heygen_accounts["accounts"]))
            else:
                self.heygen_accounts["active_account"] = ""
        
        success = self._save_config(self.heygen_accounts, self.heygen_config_file)
        
        if success:
            logger.info(f"Conta HeyGen removida: {account_id}")
        
        return success
    
    def list_heygen_accounts(self) -> Dict[str, Dict[str, str]]:
        """
        Lista todas as contas HeyGen.
        
        Returns:
            Dict[str, Dict[str, str]]: Dicionário com as contas HeyGen
        """
        return self.heygen_accounts.get("accounts", {})
    
    def get_active_heygen_account_id(self) -> str:
        """
        Obtém o ID da conta HeyGen ativa.
        
        Returns:
            str: ID da conta HeyGen ativa
        """
        return self.heygen_accounts.get("active_account", "")
    
    def get_elevenlabs_api_key(self) -> str:
        """
        Obtém a chave de API do ElevenLabs.
        
        Returns:
            str: Chave de API do ElevenLabs
        """
        # Por enquanto, apenas retornar a chave do .env
        return os.environ.get("ELEVENLABS_API_KEY", "")
