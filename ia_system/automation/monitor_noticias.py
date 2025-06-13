#!/usr/bin/env python3
"""
Monitor automático de notícias para detecção de conteúdo relevante.
"""
import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Adicionar diretório pai ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
sys.path.insert(0, project_root)

from ia_system.core.news_collector import NewsCollector
from ia_system.core.twitter_collector import TwitterCollector
from ia_system.core.notificador import Notificador

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NewsMonitor:
    """
    Monitor automático de notícias cripto.
    """
    
    def __init__(self):
        """Inicializa o monitor de notícias."""
        self.news_collector = NewsCollector()
        self.twitter_collector = TwitterCollector()
        self.notificador = Notificador()
        
        # Arquivo para tracking de notícias já vistas
        self.seen_file = os.path.join(os.path.dirname(__file__), "..", "cache", "seen_news.json")
        os.makedirs(os.path.dirname(self.seen_file), exist_ok=True)
        
        # Carregar notícias já vistas
        self.seen_news = self._load_seen_news()
        
        # Palavras-chave de alta prioridade para alertas
        self.high_priority_keywords = [
            'urgente', 'breaking', 'oficial', 'aprovado', 'regulamentação',
            'banco central', 'sec', 'brasil', 'drex', 'cbdc',
            'microstrategy', 'tesla', 'blackrock', 'etf aprovado',
            'hack', 'falência', 'proibição', 'liberação'
        ]
    
    def _load_seen_news(self) -> List[str]:
        """Carrega IDs de notícias já vistas."""
        if os.path.exists(self.seen_file):
            try:
                with open(self.seen_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('seen_ids', [])
            except:
                return []
        return []
    
    def _save_seen_news(self):
        """Salva IDs de notícias já vistas."""
        try:
            data = {
                'seen_ids': self.seen_news[-1000:],  # Manter apenas últimas 1000
                'last_update': datetime.now().isoformat()
            }
            with open(self.seen_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar seen_news: {e}")
    
    def _is_high_priority(self, titulo: str, conteudo: str) -> bool:
        """Verifica se é notícia de alta prioridade."""
        texto_completo = f"{titulo} {conteudo}".lower()
        
        for keyword in self.high_priority_keywords:
            if keyword in texto_completo:
                return True
        
        return False
    
    def _generate_alert(self, noticias_novas: List[Any], high_priority: List[Any]):
        """Gera alerta sobre notícias novas."""
        print("\n" + "="*60)
        print(f"🚨 ALERTA DE NOTÍCIAS - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print("="*60)
        
        if high_priority:
            print(f"\n⚡ ALTA PRIORIDADE ({len(high_priority)} notícias):")
            print("-"*40)
            for noticia in high_priority:
                print(f"• {noticia.titulo}")
                print(f"  📰 Fonte: {noticia.fonte}")
                print(f"  🏷️ Categoria: {', '.join(noticia.categorias)}")
                print(f"  📊 Score: {noticia.relevancia_score}")
                print()
        
        if noticias_novas:
            print(f"\n📰 NOVAS NOTÍCIAS ({len(noticias_novas)} encontradas):")
            print("-"*40)
            for noticia in noticias_novas[:5]:  # Mostrar até 5
                print(f"• {noticia.titulo[:80]}...")
                print(f"  📰 {noticia.fonte} | 🏷️ {', '.join(noticia.categorias)}")
        
        print("\n💡 Dica: Execute o pipeline para gerar roteiro com essas notícias!")
        print("="*60 + "\n")
    
    def monitorar_uma_vez(self) -> Dict[str, Any]:
        """Executa uma checagem de notícias."""
        logger.info("🔍 Verificando notícias...")
        
        # Coletar notícias
        todas_noticias = self.news_collector.obter_noticias_para_roteiro()
        
        # Filtrar notícias novas
        noticias_novas = []
        high_priority = []
        
        for noticia in todas_noticias:
            # Criar ID único para a notícia
            noticia_id = f"{noticia.fonte}_{noticia.titulo[:50]}_{noticia.data_publicacao.date()}"
            
            if noticia_id not in self.seen_news:
                noticias_novas.append(noticia)
                self.seen_news.append(noticia_id)
                
                # Verificar se é alta prioridade
                if self._is_high_priority(noticia.titulo, noticia.conteudo):
                    high_priority.append(noticia)
        
        # Salvar notícias vistas
        self._save_seen_news()
        
        # Resultado
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'total_noticias': len(todas_noticias),
            'noticias_novas': len(noticias_novas),
            'alta_prioridade': len(high_priority),
            'fontes': list(set(n.fonte for n in todas_noticias))
        }
        
        # Gerar alerta se houver notícias novas
        if noticias_novas:
            self._generate_alert(noticias_novas, high_priority)
            
            # Enviar notificações
            if high_priority:
                # Notificação de alta prioridade
                titulo = f"CRIPTO ALERTA: {len(high_priority)} notícias urgentes!"
                mensagem = f"Detectadas {len(noticias_novas)} notícias novas, {len(high_priority)} de alta prioridade"
                
                self.notificador.notificar_completo(
                    titulo=titulo,
                    mensagem=mensagem,
                    prioridade="alta",
                    detalhes={
                        "noticias": [
                            {
                                "titulo": n.titulo,
                                "fonte": n.fonte,
                                "categoria": ", ".join(n.categorias),
                                "score": n.relevancia_score
                            } for n in high_priority
                        ]
                    }
                )
            elif len(noticias_novas) >= 3:
                # Notificação normal para muitas notícias
                titulo = f"Novas notícias cripto detectadas"
                mensagem = f"Encontradas {len(noticias_novas)} notícias novas verificadas"
                
                self.notificador.notificar_completo(
                    titulo=titulo,
                    mensagem=mensagem,
                    prioridade="normal",
                    detalhes={
                        "total": len(noticias_novas),
                        "fontes": resultado['fontes']
                    }
                )
        else:
            logger.info("✅ Nenhuma notícia nova encontrada")
        
        return resultado
    
    def monitorar_continuo(self, intervalo_minutos: int = 15):
        """
        Monitora continuamente as notícias.
        
        Args:
            intervalo_minutos: Intervalo entre verificações
        """
        logger.info(f"🚀 Iniciando monitoramento contínuo (intervalo: {intervalo_minutos} min)")
        logger.info("Pressione Ctrl+C para parar\n")
        
        try:
            while True:
                # Executar checagem
                resultado = self.monitorar_uma_vez()
                
                # Log resumido
                logger.info(
                    f"📊 Resumo: {resultado['total_noticias']} notícias, "
                    f"{resultado['noticias_novas']} novas, "
                    f"{resultado['alta_prioridade']} prioritárias"
                )
                
                # Aguardar próximo ciclo
                logger.info(f"⏰ Próxima verificação em {intervalo_minutos} minutos...")
                time.sleep(intervalo_minutos * 60)
                
        except KeyboardInterrupt:
            logger.info("\n👋 Monitoramento interrompido pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro no monitoramento: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor de notícias cripto")
    parser.add_argument(
        "--continuo", 
        action="store_true", 
        help="Executar monitoramento contínuo"
    )
    parser.add_argument(
        "--intervalo", 
        type=int, 
        default=15,
        help="Intervalo em minutos para monitoramento contínuo (padrão: 15)"
    )
    
    args = parser.parse_args()
    
    monitor = NewsMonitor()
    
    if args.continuo:
        monitor.monitorar_continuo(args.intervalo)
    else:
        monitor.monitorar_uma_vez()