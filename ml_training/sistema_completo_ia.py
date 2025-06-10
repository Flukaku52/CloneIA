#!/usr/bin/env python3
"""
Sistema completo de geração automática de reels
Busca notícias + Gera roteiro + Cria reel
"""

import json
import requests
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys

# Adicionar paths
sys.path.append('/Users/renatosantannasilva/Documents/augment-projects/CloneIA')
sys.path.append('/Users/renatosantannasilva/Documents/augment-projects/CloneIA/ml_training')

from gerador_roteiro_ia import GeradorRoteiro

class SistemaCompletoIA:
    """Sistema completo para gerar reels automaticamente"""
    
    def __init__(self):
        self.gerador_roteiro = GeradorRoteiro()
        self.fontes_noticias = self._configurar_fontes()
    
    def _configurar_fontes(self) -> Dict:
        """Configura fontes de notícias cripto"""
        
        return {
            "api_news": {
                # APIs gratuitas de notícias cripto
                "cryptonews": "https://cryptonews-api.com/api/v1/category", 
                "newsapi": "https://newsapi.org/v2/everything",
                "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/"
            },
            "sites_brasileiros": [
                "livecoins.com.br",
                "portaldobitcoin.uol.com.br", 
                "cointelegraph.com.br",
                "blocknews.com.br"
            ],
            "palavras_chave": [
                "bitcoin", "cryptocurrency", "blockchain", "drex", 
                "banco central", "regulamentacao", "brasil crypto",
                "cbdc", "ethereum", "defi"
            ]
        }
    
    def buscar_noticias_automaticamente(self) -> List[Dict]:
        """
        Busca notícias automaticamente de várias fontes
        (Simulação - você pode integrar APIs reais)
        """
        
        print("🔍 BUSCANDO NOTÍCIAS AUTOMATICAMENTE...")
        
        # Por enquanto, simular busca com notícias exemplo
        # Em produção, você integraria com APIs reais
        noticias_encontradas = self._simular_busca_noticias()
        
        # Filtrar e ranquear por relevância
        noticias_filtradas = self._filtrar_e_ranquear(noticias_encontradas)
        
        print(f"✅ {len(noticias_filtradas)} notícias relevantes encontradas")
        
        return noticias_filtradas
    
    def _simular_busca_noticias(self) -> List[Dict]:
        """Simula busca de notícias (substitua por API real)"""
        
        # Notícias exemplo que simulariam o que viria de APIs
        noticias_simuladas = [
            {
                "titulo": "Brasil lidera adoção de Bitcoin na América Latina",
                "conteudo": "Pesquisa da Chainalysis mostra que o Brasil concentra 45% do volume de transações de criptomoedas na região, superando Argentina e México.",
                "fonte": "Chainalysis",
                "categoria": "bitcoin",
                "relevancia": 9,
                "data": datetime.now().strftime("%Y-%m-%d"),
                "url": "exemplo.com/noticia1"
            },
            {
                "titulo": "Nubank anuncia suporte completo para DeFi",
                "conteudo": "Banco digital vai permitir que clientes acessem protocolos DeFi diretamente pelo app, incluindo staking e yield farming.",
                "fonte": "Nubank oficial",
                "categoria": "defi",
                "relevancia": 8,
                "data": datetime.now().strftime("%Y-%m-%d"),
                "url": "exemplo.com/noticia2"
            },
            {
                "titulo": "Receita Federal cria nova regra para declarar NFTs",
                "conteudo": "A partir de 2025, NFTs precisarão ser declarados como bens e direitos, com regras específicas para cálculo de ganho de capital.",
                "fonte": "Receita Federal",
                "categoria": "regulamentacao", 
                "relevancia": 7,
                "data": datetime.now().strftime("%Y-%m-%d"),
                "url": "exemplo.com/noticia3"
            },
            {
                "titulo": "Ethereum atinge novo recorde de transações no Brasil",
                "conteudo": "Rede Ethereum processou mais de 2 milhões de transações originárias do Brasil em dezembro, crescimento de 340% em relação ao ano anterior.",
                "fonte": "Etherscan",
                "categoria": "ethereum",
                "relevancia": 6,
                "data": datetime.now().strftime("%Y-%m-%d"),
                "url": "exemplo.com/noticia4"
            }
        ]
        
        return noticias_simuladas
    
    def _filtrar_e_ranquear(self, noticias: List[Dict]) -> List[Dict]:
        """Filtra notícias por relevância e adequação ao canal"""
        
        # Critérios baseados nos padrões aprendidos
        criterios_pontuacao = {
            "tem_dados_numericos": 2,  # Seu estilo sempre usa números específicos
            "menciona_brasil": 3,      # Foco em contexto brasileiro
            "categoria_prioridade": {  # Baseado nas categorias do roteiro analisado
                "bitcoin": 3,
                "regulamentacao": 3, 
                "cbdc": 3,
                "defi": 2,
                "ethereum": 2,
                "nft": 1
            },
            "fonte_credivel": 2,       # Sempre cita fontes
            "tem_controversia": 1      # Gosta de análise crítica
        }
        
        for noticia in noticias:
            pontuacao = noticia.get("relevancia", 0)
            
            # Verificar critérios
            conteudo = noticia["conteudo"].lower()
            titulo = noticia["titulo"].lower()
            
            # Dados numéricos
            import re
            if re.search(r'\d+[%\w]*', conteudo + titulo):
                pontuacao += criterios_pontuacao["tem_dados_numericos"]
            
            # Menciona Brasil
            if any(palavra in conteudo + titulo for palavra in ["brasil", "brasileiro", "receita", "banco central"]):
                pontuacao += criterios_pontuacao["menciona_brasil"]
            
            # Categoria
            categoria = noticia.get("categoria", "geral")
            pontuacao += criterios_pontuacao["categoria_prioridade"].get(categoria, 0)
            
            # Fonte credível (tem fonte específica)
            if noticia.get("fonte") and noticia["fonte"] != "":
                pontuacao += criterios_pontuacao["fonte_credivel"]
            
            noticia["pontuacao_final"] = pontuacao
        
        # Ordenar por pontuação e pegar top 3
        noticias_ranqueadas = sorted(noticias, key=lambda x: x["pontuacao_final"], reverse=True)
        
        return noticias_ranqueadas[:3]
    
    def gerar_reel_completo_automatico(self) -> Optional[str]:
        """Processo completo: busca notícias + gera roteiro + cria reel"""
        
        print("🤖 GERAÇÃO AUTOMÁTICA DE REEL COMPLETA")
        print("=" * 50)
        
        try:
            # 1. Buscar notícias
            noticias = self.buscar_noticias_automaticamente()
            
            if not noticias:
                print("❌ Nenhuma notícia encontrada!")
                return None
            
            # 2. Gerar roteiro automaticamente
            print("\n🎬 Gerando roteiro baseado nos padrões aprendidos...")
            roteiro = self.gerador_roteiro.gerar_roteiro_automatico(noticias)
            
            if not roteiro:
                print("❌ Erro ao gerar roteiro!")
                return None
            
            # 3. Salvar roteiro final
            arquivo_roteiro = self._salvar_roteiro_final(roteiro, noticias)
            
            # 4. Mostrar resultado
            self._mostrar_roteiro_gerado(roteiro)
            
            print(f"\n✅ REEL AUTOMÁTICO GERADO!")
            print(f"📁 Roteiro salvo: {arquivo_roteiro}")
            print(f"🎯 Próximo passo: Execute 'python generate_reel_correto.py' usando este roteiro")
            
            return arquivo_roteiro
            
        except Exception as e:
            print(f"❌ Erro na geração automática: {str(e)}")
            return None
    
    def _salvar_roteiro_final(self, roteiro: Dict, noticias: List[Dict]) -> str:
        """Salva roteiro final com metadados"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"ml_training/roteiros_exemplos/reel_automatico_{timestamp}.json"
        
        dados_completos = {
            "metadata": {
                "gerado_automaticamente": True,
                "timestamp": datetime.now().isoformat(),
                "noticias_fonte": noticias,
                "versao_ia": "1.0",
                "baseado_em_padroes": "padroes_roteiro_v1.json"
            },
            "roteiro": roteiro,
            "estatisticas": {
                "total_segmentos": len(roteiro),
                "noticias_processadas": len(noticias),
                "tempo_geracao": "automatico"
            }
        }
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_completos, f, indent=2, ensure_ascii=False)
        
        return arquivo
    
    def _mostrar_roteiro_gerado(self, roteiro: Dict):
        """Mostra preview do roteiro gerado"""
        
        print("\n📺 PREVIEW DO ROTEIRO GERADO:")
        print("=" * 40)
        
        for segmento_id, dados in roteiro.items():
            titulo = dados.get("title", segmento_id).upper()
            texto = dados.get("text", "")
            
            print(f"\n🎬 {titulo}")
            print(f"📝 {texto[:100]}{'...' if len(texto) > 100 else ''}")
    
    def integrar_com_pipeline_existente(self, arquivo_roteiro: str):
        """Integra roteiro gerado com pipeline existente"""
        
        print(f"\n🔄 INTEGRANDO COM PIPELINE EXISTENTE...")
        
        # Ler roteiro gerado
        with open(arquivo_roteiro, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        roteiro = dados["roteiro"]
        
        # Converter para formato esperado pelo generate_reel_correto.py
        segmentos_convertidos = []
        
        for segmento_id, dados_seg in roteiro.items():
            segmento_convertido = {
                "id": segmento_id,
                "title": dados_seg["title"],
                "text": dados_seg["text"]
            }
            segmentos_convertidos.append(segmento_convertido)
        
        # Salvar no formato esperado
        arquivo_pipeline = "roteiro_automatico_pipeline.json"
        with open(arquivo_pipeline, 'w', encoding='utf-8') as f:
            json.dump(segmentos_convertidos, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Roteiro convertido: {arquivo_pipeline}")
        print("🎯 Agora você pode usar este arquivo no pipeline existente!")


def main():
    """Função principal"""
    
    print("🤖 SISTEMA COMPLETO DE IA PARA REELS")
    print("Busca automática + Geração de roteiro + Pipeline")
    print()
    
    sistema = SistemaCompletoIA()
    
    # Processo completo
    arquivo_gerado = sistema.gerar_reel_completo_automatico()
    
    if arquivo_gerado:
        # Integrar com pipeline existente
        sistema.integrar_com_pipeline_existente(arquivo_gerado)
        
        print("\n🎉 PROCESSO COMPLETO FINALIZADO!")
        print("A IA agora pode:")
        print("  ✅ Buscar notícias automaticamente")
        print("  ✅ Gerar roteiros no seu estilo") 
        print("  ✅ Integrar com pipeline existente")
        print("  ✅ Usar rotação de avatares")
        print("\n🚀 Próxima evolução: Integrar APIs reais de notícias!")


if __name__ == "__main__":
    main()