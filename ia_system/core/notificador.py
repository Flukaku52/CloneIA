#!/usr/bin/env python3
"""
Sistema de notificações para alertas de notícias.
"""
import os
import json
import subprocess
import platform
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class Notificador:
    """
    Sistema de notificações multiplataforma.
    """
    
    def __init__(self):
        """Inicializa o notificador."""
        self.sistema = platform.system()
        self.som_habilitado = True
        
        # Arquivo de configuração de notificações
        self.config_file = os.path.join(os.path.dirname(__file__), "..", "config", "notificacoes.json")
        self.config = self._carregar_config()
    
    def _carregar_config(self) -> dict:
        """Carrega configurações de notificação."""
        config_padrao = {
            "metodos_ativos": ["desktop", "som", "arquivo"],
            "webhook_discord": "",
            "webhook_telegram": "",
            "email": "",
            "som_arquivo": ""
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return config_padrao
    
    def notificar_desktop(self, titulo: str, mensagem: str):
        """
        Envia notificação desktop nativa.
        
        Args:
            titulo: Título da notificação
            mensagem: Mensagem da notificação
        """
        try:
            if self.sistema == "Darwin":  # macOS
                # Usar osascript para notificação nativa
                script = f'display notification "{mensagem}" with title "{titulo}" sound name "Submarine"'
                subprocess.run(["osascript", "-e", script])
                
            elif self.sistema == "Windows":
                # Windows 10/11 toast notification
                try:
                    from win10toast import ToastNotifier
                    toaster = ToastNotifier()
                    toaster.show_toast(titulo, mensagem, duration=10)
                except ImportError:
                    # Fallback para Windows
                    subprocess.run([
                        "msg", "*", f"{titulo}\n{mensagem}"
                    ])
                    
            else:  # Linux
                # Usar notify-send
                subprocess.run([
                    "notify-send", titulo, mensagem,
                    "-i", "dialog-information",
                    "-u", "critical"
                ])
                
            logger.info(f"✅ Notificação desktop enviada: {titulo}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação desktop: {e}")
    
    def tocar_som(self):
        """Toca som de alerta."""
        if not self.som_habilitado:
            return
            
        try:
            if self.sistema == "Darwin":  # macOS
                # Som do sistema
                subprocess.run(["afplay", "/System/Library/Sounds/Submarine.aiff"])
            elif self.sistema == "Windows":
                # Beep do Windows
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            else:  # Linux
                # Beep genérico
                subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/message.oga"])
                
        except Exception as e:
            logger.error(f"Erro ao tocar som: {e}")
    
    def salvar_notificacao_arquivo(self, titulo: str, mensagem: str, detalhes: dict = None):
        """
        Salva notificação em arquivo para consulta posterior.
        
        Args:
            titulo: Título da notificação
            mensagem: Mensagem principal
            detalhes: Detalhes adicionais
        """
        try:
            notif_dir = os.path.join(os.path.dirname(__file__), "..", "..", "output", "notificacoes")
            os.makedirs(notif_dir, exist_ok=True)
            
            notif_file = os.path.join(notif_dir, f"alertas_{datetime.now().strftime('%Y%m%d')}.txt")
            
            with open(notif_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"🚨 {datetime.now().strftime('%H:%M:%S')} - {titulo}\n")
                f.write(f"{'='*60}\n")
                f.write(f"{mensagem}\n")
                
                if detalhes:
                    f.write(f"\nDETALHES:\n")
                    for key, value in detalhes.items():
                        f.write(f"• {key}: {value}\n")
                
                f.write(f"\n")
            
            logger.info(f"📝 Notificação salva em: {notif_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar notificação: {e}")
    
    def enviar_webhook_discord(self, titulo: str, mensagem: str, noticias: List = None):
        """
        Envia notificação via webhook do Discord.
        
        Args:
            titulo: Título
            mensagem: Mensagem
            noticias: Lista de notícias
        """
        webhook_url = self.config.get("webhook_discord")
        if not webhook_url:
            return
            
        try:
            import requests
            
            # Formatar mensagem para Discord
            embed = {
                "title": f"🚨 {titulo}",
                "description": mensagem,
                "color": 16711680,  # Vermelho
                "timestamp": datetime.utcnow().isoformat(),
                "fields": []
            }
            
            if noticias:
                for i, noticia in enumerate(noticias[:5]):
                    embed["fields"].append({
                        "name": f"📰 Notícia {i+1}",
                        "value": f"{noticia['titulo']}\n*Fonte: {noticia['fonte']}*",
                        "inline": False
                    })
            
            data = {"embeds": [embed]}
            
            response = requests.post(webhook_url, json=data)
            if response.status_code == 204:
                logger.info("✅ Notificação enviada para Discord")
            
        except Exception as e:
            logger.error(f"Erro ao enviar para Discord: {e}")
    
    def notificar_completo(self, titulo: str, mensagem: str, prioridade: str = "normal", detalhes: dict = None):
        """
        Envia notificação usando todos os métodos configurados.
        
        Args:
            titulo: Título da notificação
            mensagem: Mensagem principal
            prioridade: "alta", "normal" ou "baixa"
            detalhes: Informações adicionais
        """
        metodos = self.config.get("metodos_ativos", ["desktop", "som", "arquivo"])
        
        # Se alta prioridade, forçar todos os métodos
        if prioridade == "alta":
            if "desktop" in metodos:
                self.notificar_desktop(f"⚡ {titulo}", mensagem)
            if "som" in metodos:
                self.tocar_som()
        
        # Sempre salvar em arquivo
        if "arquivo" in metodos:
            self.salvar_notificacao_arquivo(titulo, mensagem, detalhes)
        
        # Enviar para Discord se configurado
        if "discord" in metodos and detalhes and "noticias" in detalhes:
            self.enviar_webhook_discord(titulo, mensagem, detalhes["noticias"])
    
    def configurar_webhook_discord(self, webhook_url: str):
        """Configura webhook do Discord."""
        self.config["webhook_discord"] = webhook_url
        self._salvar_config()
        logger.info("✅ Webhook Discord configurado")
    
    def _salvar_config(self):
        """Salva configurações."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)


if __name__ == "__main__":
    # Teste do notificador
    notificador = Notificador()
    
    print("🔔 TESTE DE NOTIFICAÇÕES")
    print("-" * 40)
    
    # Teste de notificação desktop
    notificador.notificar_desktop(
        "Nova notícia cripto detectada!",
        "MicroStrategy compra mais 1.000 BTC"
    )
    
    # Teste de som
    notificador.tocar_som()
    
    # Teste de arquivo
    notificador.salvar_notificacao_arquivo(
        "ALERTA: Alta prioridade",
        "Banco Central anuncia nova fase do Drex",
        {
            "fonte": "Twitter - @bitdov",
            "categoria": "cbdc_drex",
            "score": 85
        }
    )
    
    print("\n✅ Testes concluídos!")
    print("Verifique:")
    print("• Notificação desktop apareceu")
    print("• Som foi tocado")
    print("• Arquivo salvo em output/notificacoes/")