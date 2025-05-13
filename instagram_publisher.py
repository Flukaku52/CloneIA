#!/usr/bin/env python3
"""
Módulo para publicar vídeos diretamente no Instagram usando a API do Instagram Graph.
Requer uma conta comercial ou de criador de conteúdo no Instagram.
"""
import os
import sys
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('instagram_publisher')

class InstagramPublisher:
    """
    Classe para publicar conteúdo no Instagram usando a API do Instagram Graph.
    """
    def __init__(self,
                 access_token: str = None,
                 instagram_account_id: str = None,
                 facebook_page_id: str = None,
                 config_file: str = "config/instagram_config.json",
                 cache_dir: str = "cache"):
        """
        Inicializa o publicador do Instagram.

        Args:
            access_token: Token de acesso à API do Instagram Graph
            instagram_account_id: ID da conta do Instagram
            facebook_page_id: ID da página do Facebook associada
            config_file: Caminho para o arquivo de configuração
            cache_dir: Diretório para armazenar o cache
        """
        # Carregar configurações do arquivo se não fornecidas diretamente
        if not (access_token and instagram_account_id):
            self._load_config(config_file)
        else:
            self.access_token = access_token
            self.instagram_account_id = instagram_account_id
            self.facebook_page_id = facebook_page_id

        self.api_version = "v18.0"  # Versão atual da API do Graph
        self.api_base_url = f"https://graph.facebook.com/{self.api_version}"
        self.cache_dir = cache_dir

        # Criar diretório de cache se não existir
        os.makedirs(self.cache_dir, exist_ok=True)

        # Verificar se temos as credenciais necessárias
        if not (self.access_token and self.instagram_account_id):
            logger.warning("Credenciais do Instagram não configuradas. A publicação não será possível.")

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
                self.facebook_page_id = config.get("facebook_page_id")

                logger.info("Configurações do Instagram carregadas com sucesso.")
            else:
                # Tentar carregar de variáveis de ambiente
                self.access_token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
                self.instagram_account_id = os.environ.get("INSTAGRAM_ACCOUNT_ID")
                self.facebook_page_id = os.environ.get("FACEBOOK_PAGE_ID")

                if self.access_token and self.instagram_account_id:
                    logger.info("Configurações do Instagram carregadas das variáveis de ambiente.")
                else:
                    logger.warning(f"Arquivo de configuração não encontrado: {config_file}")
                    self.access_token = None
                    self.instagram_account_id = None
                    self.facebook_page_id = None
        except Exception as e:
            logger.error(f"Erro ao carregar configurações do Instagram: {e}")
            self.access_token = None
            self.instagram_account_id = None
            self.facebook_page_id = None

    def _save_config(self, config_file: str) -> bool:
        """
        Salva as configurações no arquivo.

        Args:
            config_file: Caminho para o arquivo de configuração

        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            # Garantir que o diretório existe
            os.makedirs(os.path.dirname(config_file), exist_ok=True)

            config = {
                "access_token": self.access_token,
                "instagram_account_id": self.instagram_account_id,
                "facebook_page_id": self.facebook_page_id,
                "last_updated": datetime.now().isoformat()
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            logger.info(f"Configurações salvas em {config_file}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {e}")
            return False

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

    def get_auth_url(self, app_id: str, redirect_uri: str, state: str = None) -> str:
        """
        Gera a URL para autenticação OAuth.

        Args:
            app_id: ID do aplicativo Facebook
            redirect_uri: URI de redirecionamento após autenticação
            state: Estado para segurança CSRF

        Returns:
            str: URL para autenticação
        """
        if not state:
            state = f"instagram_auth_{int(time.time())}"

        params = {
            "client_id": app_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": "instagram_basic,instagram_content_publish,pages_read_engagement,pages_show_list",
            "response_type": "code"
        }

        auth_url = f"https://www.facebook.com/{self.api_version}/dialog/oauth?" + urlencode(params)
        return auth_url

    def exchange_code_for_token(self, app_id: str, app_secret: str, redirect_uri: str, code: str) -> bool:
        """
        Troca o código de autorização por um token de acesso.

        Args:
            app_id: ID do aplicativo Facebook
            app_secret: Segredo do aplicativo Facebook
            redirect_uri: URI de redirecionamento
            code: Código de autorização

        Returns:
            bool: True se o token foi obtido com sucesso, False caso contrário
        """
        try:
            url = f"{self.api_base_url}/oauth/access_token"
            params = {
                "client_id": app_id,
                "client_secret": app_secret,
                "redirect_uri": redirect_uri,
                "code": code
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")

                # Obter token de longa duração
                if self.access_token:
                    return self._get_long_lived_token(app_id, app_secret)
                else:
                    logger.error("Token não encontrado na resposta")
                    return False
            else:
                logger.error(f"Erro ao trocar código por token: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Erro ao trocar código por token: {e}")
            return False

    def _get_long_lived_token(self, app_id: str, app_secret: str) -> bool:
        """
        Obtém um token de acesso de longa duração.

        Args:
            app_id: ID do aplicativo Facebook
            app_secret: Segredo do aplicativo Facebook

        Returns:
            bool: True se o token foi obtido com sucesso, False caso contrário
        """
        try:
            url = f"{self.api_base_url}/oauth/access_token"
            params = {
                "grant_type": "fb_exchange_token",
                "client_id": app_id,
                "client_secret": app_secret,
                "fb_exchange_token": self.access_token
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")

                if self.access_token:
                    logger.info("Token de longa duração obtido com sucesso")
                    return True
                else:
                    logger.error("Token de longa duração não encontrado na resposta")
                    return False
            else:
                logger.error(f"Erro ao obter token de longa duração: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Erro ao obter token de longa duração: {e}")
            return False

    def get_instagram_account_id(self) -> bool:
        """
        Obtém o ID da conta do Instagram associada à página do Facebook.

        Returns:
            bool: True se o ID foi obtido com sucesso, False caso contrário
        """
        if not self.facebook_page_id:
            logger.error("ID da página do Facebook não configurado")
            return False

        try:
            url = f"{self.api_base_url}/{self.facebook_page_id}"
            params = {
                "fields": "instagram_business_account",
                "access_token": self.access_token
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                instagram_account = data.get("instagram_business_account", {})
                self.instagram_account_id = instagram_account.get("id")

                if self.instagram_account_id:
                    logger.info(f"ID da conta do Instagram obtido: {self.instagram_account_id}")
                    return True
                else:
                    logger.error("ID da conta do Instagram não encontrado")
                    return False
            else:
                logger.error(f"Erro ao obter ID da conta do Instagram: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Erro ao obter ID da conta do Instagram: {e}")
            return False

    def upload_video_to_container(self, video_path: str, caption: str = "") -> Optional[str]:
        """
        Faz upload de um vídeo para o container do Instagram.

        Args:
            video_path: Caminho para o arquivo de vídeo
            caption: Legenda para o vídeo

        Returns:
            Optional[str]: ID do container de mídia, ou None se falhar
        """
        if not os.path.exists(video_path):
            logger.error(f"Arquivo de vídeo não encontrado: {video_path}")
            return None

        if not self.check_auth_status():
            logger.error("Autenticação inválida. Não é possível fazer upload do vídeo.")
            return None

        try:
            # Iniciar o container de mídia
            url = f"{self.api_base_url}/{self.instagram_account_id}/media"

            # Preparar os parâmetros para o vídeo
            params = {
                "media_type": "VIDEO",
                "video_url": "WILL_BE_REPLACED_WITH_PRESIGNED_URL",
                "caption": caption,
                "access_token": self.access_token
            }

            # Obter URL para upload do vídeo
            logger.info("Solicitando URL para upload do vídeo...")
            response = requests.post(url, data=params)

            if response.status_code != 200:
                logger.error(f"Erro ao iniciar container de mídia: {response.status_code} - {response.text}")
                return None

            data = response.json()

            # Verificar se temos a URL de upload e o ID do container
            if "video_url" not in data:
                logger.error("URL de upload não encontrada na resposta")
                return None

            upload_url = data["video_url"]
            media_container_id = data.get("id")

            if not media_container_id:
                logger.error("ID do container de mídia não encontrado na resposta")
                return None

            # Fazer upload do vídeo para a URL fornecida
            logger.info(f"Fazendo upload do vídeo para {upload_url}...")
            with open(video_path, 'rb') as video_file:
                upload_response = requests.post(upload_url, files={"file": video_file})

            if upload_response.status_code not in [200, 201]:
                logger.error(f"Erro ao fazer upload do vídeo: {upload_response.status_code} - {upload_response.text}")
                return None

            logger.info(f"Vídeo enviado com sucesso para o container {media_container_id}")
            return media_container_id

        except Exception as e:
            logger.error(f"Erro ao fazer upload do vídeo: {e}")
            return None

    def publish_media(self, media_container_id: str) -> Optional[str]:
        """
        Publica a mídia no Instagram.

        Args:
            media_container_id: ID do container de mídia

        Returns:
            Optional[str]: ID da publicação, ou None se falhar
        """
        if not self.check_auth_status():
            logger.error("Autenticação inválida. Não é possível publicar a mídia.")
            return None

        try:
            # Verificar status do container de mídia
            max_attempts = 10
            attempt = 0

            while attempt < max_attempts:
                url = f"{self.api_base_url}/{media_container_id}"
                params = {
                    "fields": "status_code,status",
                    "access_token": self.access_token
                }

                response = requests.get(url, params=params)

                if response.status_code != 200:
                    logger.error(f"Erro ao verificar status do container: {response.status_code} - {response.text}")
                    return None

                data = response.json()
                status_code = data.get("status_code")

                if status_code == "FINISHED":
                    logger.info("Mídia pronta para publicação")
                    break
                elif status_code in ["IN_PROGRESS", "PROCESSING"]:
                    logger.info(f"Mídia ainda em processamento: {status_code}")
                    time.sleep(5)  # Esperar 5 segundos antes de verificar novamente
                    attempt += 1
                else:
                    logger.error(f"Status inesperado do container: {status_code}")
                    return None

            if attempt >= max_attempts:
                logger.error("Tempo limite excedido ao aguardar processamento da mídia")
                return None

            # Publicar a mídia
            url = f"{self.api_base_url}/{self.instagram_account_id}/media_publish"
            params = {
                "creation_id": media_container_id,
                "access_token": self.access_token
            }

            logger.info("Publicando mídia no Instagram...")
            response = requests.post(url, data=params)

            if response.status_code != 200:
                logger.error(f"Erro ao publicar mídia: {response.status_code} - {response.text}")
                return None

            data = response.json()
            post_id = data.get("id")

            if post_id:
                logger.info(f"Mídia publicada com sucesso! ID da publicação: {post_id}")
                return post_id
            else:
                logger.error("ID da publicação não encontrado na resposta")
                return None

        except Exception as e:
            logger.error(f"Erro ao publicar mídia: {e}")
            return None

    def publish_video(self, video_path: str, caption: str = "") -> Optional[str]:
        """
        Publica um vídeo no Instagram.

        Args:
            video_path: Caminho para o arquivo de vídeo
            caption: Legenda para o vídeo

        Returns:
            Optional[str]: ID da publicação, ou None se falhar
        """
        # Fazer upload do vídeo para o container
        media_container_id = self.upload_video_to_container(video_path, caption)

        if not media_container_id:
            return None

        # Publicar a mídia
        return self.publish_media(media_container_id)

    def publish_reels(self, video_path: str, caption: str = "", hashtags: List[str] = None) -> Optional[str]:
        """
        Publica um vídeo como Reels no Instagram.

        Args:
            video_path: Caminho para o arquivo de vídeo
            caption: Legenda para o vídeo
            hashtags: Lista de hashtags para adicionar à legenda

        Returns:
            Optional[str]: ID da publicação, ou None se falhar
        """
        # Adicionar hashtags à legenda
        if hashtags:
            hashtag_text = " ".join([f"#{tag.strip('#')}" for tag in hashtags])
            if caption:
                caption = f"{caption}\n\n{hashtag_text}"
            else:
                caption = hashtag_text

        # Adicionar hashtags padrão para Rapidinha
        default_hashtags = "#bitcoin #cripto #criptomoedas #rapidinha #flukaku"
        if caption:
            caption = f"{caption}\n\n{default_hashtags}"
        else:
            caption = default_hashtags

        return self.publish_video(video_path, caption)

    def schedule_post(self, video_path: str, caption: str = "",
                     publish_time: datetime = None, hashtags: List[str] = None) -> Optional[str]:
        """
        Agenda uma publicação para o Instagram.

        Args:
            video_path: Caminho para o arquivo de vídeo
            caption: Legenda para o vídeo
            publish_time: Data e hora para publicação (se None, publica imediatamente)
            hashtags: Lista de hashtags para adicionar à legenda

        Returns:
            Optional[str]: ID da publicação agendada, ou None se falhar
        """
        if publish_time is None:
            # Publicar imediatamente
            return self.publish_reels(video_path, caption, hashtags)

        # Verificar se a data é futura
        if publish_time <= datetime.now():
            logger.warning("Data de publicação deve ser futura. Publicando imediatamente.")
            return self.publish_reels(video_path, caption, hashtags)

        # Implementar agendamento (pode ser feito com um job scheduler como APScheduler)
        # Por enquanto, apenas salvamos os dados para agendamento manual
        try:
            schedule_file = os.path.join(self.cache_dir, "scheduled_posts.json")

            # Carregar agendamentos existentes
            scheduled_posts = []
            if os.path.exists(schedule_file):
                with open(schedule_file, 'r', encoding='utf-8') as f:
                    scheduled_posts = json.load(f)

            # Adicionar novo agendamento
            scheduled_posts.append({
                "video_path": video_path,
                "caption": caption,
                "hashtags": hashtags,
                "publish_time": publish_time.isoformat(),
                "created_at": datetime.now().isoformat(),
                "status": "scheduled"
            })

            # Salvar agendamentos
            with open(schedule_file, 'w', encoding='utf-8') as f:
                json.dump(scheduled_posts, f, indent=2)

            logger.info(f"Publicação agendada para {publish_time.isoformat()}")
            return f"scheduled_{len(scheduled_posts)}"

        except Exception as e:
            logger.error(f"Erro ao agendar publicação: {e}")
            return None

    def process_scheduled_posts(self) -> Dict[str, int]:
        """
        Processa as publicações agendadas que estão prontas para serem publicadas.

        Returns:
            Dict[str, int]: Contagem de publicações processadas por status
        """
        schedule_file = os.path.join(self.cache_dir, "scheduled_posts.json")

        if not os.path.exists(schedule_file):
            logger.info("Nenhuma publicação agendada encontrada")
            return {"total": 0, "published": 0, "failed": 0, "pending": 0}

        try:
            # Carregar agendamentos
            with open(schedule_file, 'r', encoding='utf-8') as f:
                scheduled_posts = json.load(f)

            # Contadores
            counts = {"total": len(scheduled_posts), "published": 0, "failed": 0, "pending": 0}

            # Processar cada agendamento
            now = datetime.now()
            updated_posts = []

            for post in scheduled_posts:
                # Pular posts já publicados ou que falharam
                if post["status"] in ["published", "failed"]:
                    counts[post["status"]] += 1
                    updated_posts.append(post)
                    continue

                # Verificar se é hora de publicar
                publish_time = datetime.fromisoformat(post["publish_time"])

                if publish_time <= now:
                    # Hora de publicar
                    logger.info(f"Processando publicação agendada para {publish_time.isoformat()}")

                    # Verificar se o arquivo de vídeo existe
                    if not os.path.exists(post["video_path"]):
                        logger.error(f"Arquivo de vídeo não encontrado: {post['video_path']}")
                        post["status"] = "failed"
                        post["error"] = "Arquivo de vídeo não encontrado"
                        counts["failed"] += 1
                        updated_posts.append(post)
                        continue

                    # Publicar o vídeo
                    post_id = self.publish_reels(
                        post["video_path"],
                        post["caption"],
                        post.get("hashtags")
                    )

                    if post_id:
                        post["status"] = "published"
                        post["post_id"] = post_id
                        post["published_at"] = now.isoformat()
                        counts["published"] += 1
                    else:
                        post["status"] = "failed"
                        post["error"] = "Falha ao publicar"
                        counts["failed"] += 1
                else:
                    # Ainda não é hora de publicar
                    counts["pending"] += 1

                updated_posts.append(post)

            # Salvar agendamentos atualizados
            with open(schedule_file, 'w', encoding='utf-8') as f:
                json.dump(updated_posts, f, indent=2)

            logger.info(f"Processamento de agendamentos concluído: {counts}")
            return counts

        except Exception as e:
            logger.error(f"Erro ao processar publicações agendadas: {e}")
            return {"total": 0, "published": 0, "failed": 0, "pending": 0, "error": str(e)}

    def get_scheduled_posts(self) -> List[Dict[str, Any]]:
        """
        Retorna a lista de publicações agendadas.

        Returns:
            List[Dict[str, Any]]: Lista de publicações agendadas
        """
        schedule_file = os.path.join(self.cache_dir, "scheduled_posts.json")

        if not os.path.exists(schedule_file):
            return []

        try:
            with open(schedule_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar publicações agendadas: {e}")
            return []

    def cancel_scheduled_post(self, post_id: str) -> bool:
        """
        Cancela uma publicação agendada.

        Args:
            post_id: ID da publicação agendada (formato: scheduled_X)

        Returns:
            bool: True se cancelou com sucesso, False caso contrário
        """
        if not post_id.startswith("scheduled_"):
            logger.error(f"ID de publicação inválido: {post_id}")
            return False

        try:
            # Extrair o índice da publicação
            index = int(post_id.split("_")[1]) - 1

            schedule_file = os.path.join(self.cache_dir, "scheduled_posts.json")

            if not os.path.exists(schedule_file):
                logger.error("Nenhuma publicação agendada encontrada")
                return False

            # Carregar agendamentos
            with open(schedule_file, 'r', encoding='utf-8') as f:
                scheduled_posts = json.load(f)

            # Verificar se o índice é válido
            if index < 0 or index >= len(scheduled_posts):
                logger.error(f"Índice de publicação inválido: {index}")
                return False

            # Verificar se a publicação já foi processada
            if scheduled_posts[index]["status"] in ["published", "failed"]:
                logger.error(f"Publicação já processada: {scheduled_posts[index]['status']}")
                return False

            # Cancelar a publicação
            scheduled_posts[index]["status"] = "cancelled"
            scheduled_posts[index]["cancelled_at"] = datetime.now().isoformat()

            # Salvar agendamentos atualizados
            with open(schedule_file, 'w', encoding='utf-8') as f:
                json.dump(scheduled_posts, f, indent=2)

            logger.info(f"Publicação {post_id} cancelada com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro ao cancelar publicação: {e}")
            return False

def setup_instagram_auth(app_id: str, app_secret: str, redirect_uri: str) -> None:
    """
    Configura a autenticação do Instagram.

    Args:
        app_id: ID do aplicativo Facebook
        app_secret: Segredo do aplicativo Facebook
        redirect_uri: URI de redirecionamento
    """
    publisher = InstagramPublisher()

    # Gerar URL de autenticação
    auth_url = publisher.get_auth_url(app_id, redirect_uri)

    print("\n=== Configuração da Autenticação do Instagram ===")
    print(f"\nAcesse a seguinte URL no seu navegador para autorizar o aplicativo:")
    print(f"\n{auth_url}\n")
    print("Após autorizar, você será redirecionado para uma URL. Copie essa URL completa e cole abaixo:")

    redirect_url = input("\nURL de redirecionamento: ")

    # Extrair o código de autorização da URL
    try:
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(redirect_url)
        params = parse_qs(parsed_url.query)

        if "code" not in params:
            print("Código de autorização não encontrado na URL")
            return

        code = params["code"][0]

        # Trocar o código por um token de acesso
        if publisher.exchange_code_for_token(app_id, app_secret, redirect_uri, code):
            # Obter o ID da conta do Instagram
            if publisher.get_instagram_account_id():
                # Salvar configurações
                publisher._save_config("config/instagram_config.json")
                print("\nAutenticação configurada com sucesso!")
            else:
                print("\nFalha ao obter ID da conta do Instagram")
        else:
            print("\nFalha ao trocar código por token de acesso")

    except Exception as e:
        print(f"\nErro ao processar URL de redirecionamento: {e}")

def main():
    """
    Função principal para testar o publicador do Instagram.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Publicador de vídeos para o Instagram")
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # Comando de configuração
    setup_parser = subparsers.add_parser("setup", help="Configurar autenticação do Instagram")
    setup_parser.add_argument("--app-id", required=True, help="ID do aplicativo Facebook")
    setup_parser.add_argument("--app-secret", required=True, help="Segredo do aplicativo Facebook")
    setup_parser.add_argument("--redirect-uri", required=True, help="URI de redirecionamento")

    # Comando de publicação
    publish_parser = subparsers.add_parser("publish", help="Publicar vídeo no Instagram")
    publish_parser.add_argument("--video", required=True, help="Caminho para o arquivo de vídeo")
    publish_parser.add_argument("--caption", default="", help="Legenda para o vídeo")
    publish_parser.add_argument("--hashtags", help="Hashtags separadas por vírgula")

    # Comando de agendamento
    schedule_parser = subparsers.add_parser("schedule", help="Agendar publicação no Instagram")
    schedule_parser.add_argument("--video", required=True, help="Caminho para o arquivo de vídeo")
    schedule_parser.add_argument("--caption", default="", help="Legenda para o vídeo")
    schedule_parser.add_argument("--hashtags", help="Hashtags separadas por vírgula")
    schedule_parser.add_argument("--datetime", required=True, help="Data e hora para publicação (formato: YYYY-MM-DD HH:MM)")

    # Comando de processamento de agendamentos
    process_parser = subparsers.add_parser("process", help="Processar publicações agendadas")

    # Comando de listagem de agendamentos
    list_parser = subparsers.add_parser("list", help="Listar publicações agendadas")

    # Comando de cancelamento de agendamento
    cancel_parser = subparsers.add_parser("cancel", help="Cancelar publicação agendada")
    cancel_parser.add_argument("--id", required=True, help="ID da publicação agendada")

    # Comando de verificação de autenticação
    check_parser = subparsers.add_parser("check", help="Verificar autenticação do Instagram")

    args = parser.parse_args()

    # Criar o publicador
    publisher = InstagramPublisher()

    if args.command == "setup":
        setup_instagram_auth(args.app_id, args.app_secret, args.redirect_uri)

    elif args.command == "publish":
        # Processar hashtags
        hashtags = None
        if args.hashtags:
            hashtags = [tag.strip() for tag in args.hashtags.split(",")]

        # Publicar vídeo
        post_id = publisher.publish_reels(args.video, args.caption, hashtags)

        if post_id:
            print(f"\nVídeo publicado com sucesso! ID da publicação: {post_id}")
        else:
            print("\nFalha ao publicar vídeo")

    elif args.command == "schedule":
        # Processar hashtags
        hashtags = None
        if args.hashtags:
            hashtags = [tag.strip() for tag in args.hashtags.split(",")]

        # Processar data e hora
        try:
            publish_time = datetime.strptime(args.datetime, "%Y-%m-%d %H:%M")
        except ValueError:
            print("\nFormato de data e hora inválido. Use o formato: YYYY-MM-DD HH:MM")
            return 1

        # Agendar publicação
        post_id = publisher.schedule_post(args.video, args.caption, publish_time, hashtags)

        if post_id:
            print(f"\nPublicação agendada com sucesso! ID: {post_id}")
            print(f"Data e hora: {publish_time.isoformat()}")
        else:
            print("\nFalha ao agendar publicação")

    elif args.command == "process":
        # Processar publicações agendadas
        results = publisher.process_scheduled_posts()

        print("\n=== Processamento de Publicações Agendadas ===")
        print(f"Total: {results['total']}")
        print(f"Publicadas: {results['published']}")
        print(f"Falhas: {results['failed']}")
        print(f"Pendentes: {results['pending']}")

        if "error" in results:
            print(f"Erro: {results['error']}")

    elif args.command == "list":
        # Listar publicações agendadas
        posts = publisher.get_scheduled_posts()

        print("\n=== Publicações Agendadas ===")

        if not posts:
            print("Nenhuma publicação agendada encontrada")
            return 0

        for i, post in enumerate(posts, 1):
            print(f"\n{i}. Status: {post['status']}")
            print(f"   Vídeo: {post['video_path']}")
            print(f"   Legenda: {post['caption'][:50]}..." if len(post['caption']) > 50 else f"   Legenda: {post['caption']}")
            print(f"   Data agendada: {post['publish_time']}")

            if post["status"] == "published":
                print(f"   Publicado em: {post['published_at']}")
                print(f"   ID da publicação: {post['post_id']}")
            elif post["status"] == "failed":
                print(f"   Erro: {post.get('error', 'Desconhecido')}")
            elif post["status"] == "cancelled":
                print(f"   Cancelado em: {post['cancelled_at']}")

    elif args.command == "cancel":
        # Cancelar publicação agendada
        if publisher.cancel_scheduled_post(args.id):
            print(f"\nPublicação {args.id} cancelada com sucesso")
        else:
            print(f"\nFalha ao cancelar publicação {args.id}")

    elif args.command == "check":
        # Verificar autenticação
        if publisher.check_auth_status():
            print("\nAutenticação válida")
        else:
            print("\nAutenticação inválida ou não configurada")

    else:
        parser.print_help()

    return 0

if __name__ == "__main__":
    sys.exit(main())
