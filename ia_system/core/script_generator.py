#!/usr/bin/env python3
"""
Gerador de roteiros educativos com viés libertário baseado em notícias cripto.
"""
import os
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass

try:
    from .news_collector import NewsCollector, Noticia
except ImportError:
    from news_collector import NewsCollector, Noticia

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SegmentoRoteiro:
    """Classe para representar um segmento do roteiro."""
    titulo: str
    texto: str
    categoria: str
    explicacao_tecnica: Optional[str] = None
    vies_libertario: Optional[str] = None

class ScriptGenerator:
    """
    Gerador de roteiros educativos com viés libertário.
    """
    
    def __init__(self, config_path: str = None):
        """
        Inicializa o gerador de roteiros.
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        # Carregar configurações
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "ia_settings.json")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)['sistema_ia']
        
        # Inicializar coletor de notícias
        self.news_collector = NewsCollector(config_path)
        
        # Templates de texto
        self.templates = {
            'introducoes_variadas': [
                "EAÍCAMBADA! Já tô de volta por aqui e bora pras notícias",
                "EAÍCAMBADA! E aí como é que tá? Bora para mais uma rapidinha",
                "FALACAMBADA! Tô aqui de novo com as notícias da semana"
            ],
            'transicoes': [
                "Seguinte:",
                "Agora uma que pouca gente tá falando:",
                "Agora presta atenção nessa aqui:",
                "E aqui ó, uma importante:",
                "Olha só essa notícia:",
                "Vou te contar uma que é interessante:"
            ],
            'enfases_libertarias': [
                "Mas a gente tem que ficar atento ao lado do controle nisso",
                "Isso mostra como a descentralização é importante",
                "É importante ter liberdade de escolha nessa história",
                "A tecnologia é boa, mas liberdade financeira tem que vir primeiro",
                "Transparência é bom, mas vigilância excessiva é preocupante"
            ],
            'explicacoes_leigo': {
                'blockchain': "que é um sistema onde as informações ficam registradas de forma descentralizada, sem depender de um banco ou governo",
                'bitcoin': "a primeira moeda digital que não depende de banco central",
                'defi': "que são finanças descentralizadas, sem bancos tradicionais no meio",
                'cbdc': "que é uma moeda digital controlada pelo banco central",
                'smart_contract': "que são contratos que executam automaticamente quando as condições são atendidas"
            }
        }
    
    def _adicionar_explicacao_tecnica(self, texto: str) -> str:
        """
        Adiciona explicações técnicas para termos complexos.
        
        Args:
            texto: Texto original
            
        Returns:
            str: Texto com explicações adicionadas
        """
        explicacoes = self.templates['explicacoes_leigo']
        
        for termo, explicacao in explicacoes.items():
            # Buscar variações do termo
            variacoes = {
                'blockchain': ['blockchain', 'tecnologia blockchain'],
                'bitcoin': ['bitcoin', 'btc'],
                'defi': ['defi', 'finanças descentralizadas'],
                'cbdc': ['cbdc', 'moeda digital do banco central', 'drex'],
                'smart_contract': ['smart contract', 'contrato inteligente']
            }
            
            if termo in variacoes:
                for variacao in variacoes[termo]:
                    if variacao.lower() in texto.lower():
                        # Adicionar explicação na primeira ocorrência
                        posicao = texto.lower().find(variacao.lower())
                        if posicao != -1:
                            inicio = posicao + len(variacao)
                            texto = texto[:inicio] + f" ({explicacao})" + texto[inicio:]
                            break  # Apenas uma explicação por termo
        
        return texto
    
    def _adicionar_vies_libertario(self, noticia: Noticia, texto: str) -> str:
        """
        Adiciona perspectiva libertária ao texto.
        
        Args:
            noticia: Notícia original
            texto: Texto do segmento
            
        Returns:
            str: Texto com viés libertário adicionado
        """
        vies_por_categoria = {
            'regulacao_brasil': [
                "É bom ver o governo modernizando, mas sempre importante acompanhar pra não virar mais controle sobre a gente.",
                "Modernização é boa, mas liberdade individual tem que ser preservada nesse processo."
            ],
            'cbdc_drex': [
                "A tecnologia é interessante pra inclusão, mas diferente do dinheiro físico, aqui tudo fica rastreado. Liberdade financeira tem que estar no centro dessa conversa.",
                "Inclusão financeira é importante, mas precisamos ficar atentos pra isso não virar ferramenta de controle do que a gente faz com nosso dinheiro."
            ],
            'adocao_empresarial': [
                "Isso mostra que o Bitcoin não é mais só 'dinheiro de internet' - tá virando reserva de valor institucional, fora do controle dos bancos centrais.",
                "Empresas diversificando além do dólar mostra que a busca por ativos descentralizados tá crescendo."
            ],
            'casos_uso_real': [
                "Casos assim mostram o poder da descentralização financeira na prática, dando mais opções pro povo.",
                "É isso que acontece quando as pessoas têm mais opções financeiras: liberdade gera prosperidade."
            ]
        }
        
        # Selecionar viés apropriado
        categoria = noticia.categorias[0] if noticia.categorias else 'geral'
        
        if categoria in vies_por_categoria:
            vies_opcoes = vies_por_categoria[categoria]
            vies_escolhido = random.choice(vies_opcoes)
            
            # Adicionar no final do segmento
            texto += f"\n\n{vies_escolhido}"
        
        return texto
    
    def _criar_segmento_noticia(self, noticia: Noticia, transicao: str) -> SegmentoRoteiro:
        """
        Cria um segmento de roteiro baseado numa notícia.
        
        Args:
            noticia: Notícia para transformar em segmento
            transicao: Frase de transição
            
        Returns:
            SegmentoRoteiro: Segmento criado
        """
        # Simplificar título para público leigo
        titulo_simplificado = self._simplificar_titulo(noticia.titulo)
        
        # Criar texto base adaptado
        texto_base = f"{transicao} {noticia.conteudo}"
        
        # Adicionar explicações técnicas
        texto_explicado = self._adicionar_explicacao_tecnica(texto_base)
        
        # Adicionar viés libertário
        texto_final = self._adicionar_vies_libertario(noticia, texto_explicado)
        
        # Otimizar para fala
        texto_otimizado = self._otimizar_para_fala(texto_final)
        
        return SegmentoRoteiro(
            titulo=titulo_simplificado,
            texto=texto_otimizado,
            categoria=noticia.categorias[0] if noticia.categorias else 'geral'
        )
    
    def _simplificar_titulo(self, titulo: str) -> str:
        """
        Simplifica título para público leigo.
        
        Args:
            titulo: Título original
            
        Returns:
            str: Título simplificado
        """
        # Substituições para linguagem mais acessível
        substituicoes = {
            'ETF': 'fundo de investimento',
            'CBDC': 'moeda digital do governo',
            'DeFi': 'finanças descentralizadas',
            'blockchain': 'tecnologia descentralizada',
            'smart contract': 'contrato automático'
        }
        
        titulo_simples = titulo
        for original, substituicao in substituicoes.items():
            titulo_simples = titulo_simples.replace(original, substituicao)
        
        return titulo_simples
    
    def _otimizar_para_fala(self, texto: str) -> str:
        """
        Otimiza texto para soar natural na fala.
        
        Args:
            texto: Texto original
            
        Returns:
            str: Texto otimizado para fala
        """
        # Aplicar regras de otimização baseadas no perfil do usuário
        texto_otimizado = texto
        
        # Remover pontuação excessiva
        texto_otimizado = texto_otimizado.replace('**', '')
        texto_otimizado = texto_otimizado.replace('*', '')
        
        # Ajustar vírgulas para pausas naturais
        texto_otimizado = texto_otimizado.replace(', e ', ' e ')
        texto_otimizado = texto_otimizado.replace(', mas ', ' mas ')
        
        # Substituições de pronúncia
        substituicoes_pronuncia = {
            'Bitcoin': 'Bitcoin',
            'Ethereum': 'Ethereum', 
            'está': 'tá',
            'estão': 'tão',
            'porque': 'porque'
        }
        
        for original, substituicao in substituicoes_pronuncia.items():
            texto_otimizado = texto_otimizado.replace(original, substituicao)
        
        return texto_otimizado
    
    def _criar_encerramento(self, segmentos: List[SegmentoRoteiro]) -> str:
        """
        Cria encerramento baseado nos segmentos.
        
        Args:
            segmentos: Lista de segmentos do roteiro
            
        Returns:
            str: Texto de encerramento
        """
        # Resumir temas abordados
        temas = []
        for segmento in segmentos:
            if 'empresa' in segmento.titulo.lower():
                temas.append('empresas adotando cripto')
            elif 'governo' in segmento.titulo.lower() or 'banco central' in segmento.titulo.lower():
                temas.append('movimentos governamentais')
            elif 'blockchain' in segmento.titulo.lower():
                temas.append('casos de uso da tecnologia')
            elif 'regulação' in segmento.titulo.lower():
                temas.append('mudanças regulatórias')
        
        # Criar resumo
        if len(temas) > 1:
            resumo = f"{', '.join(temas[:-1])} e {temas[-1]}"
        else:
            resumo = temas[0] if temas else "várias notícias importantes"
        
        # Enferramentos variados
        encerramentos = [
            f"Por hoje é isso cambada. {resumo.capitalize()}, sempre de olho na nossa liberdade financeira. Sigo de olho.",
            f"E é isso aí cambada. Falamos sobre {resumo}, lembrando sempre que tecnologia boa + liberdade individual = futuro melhor. Sigo de olho.",
            f"Terminando por aqui. {resumo.capitalize()}, sempre analisando os dois lados da moeda. Sigo de olho."
        ]
        
        return random.choice(encerramentos)
    
    def _estimar_duracao_texto(self, texto: str) -> int:
        """
        Estima duração em segundos baseado no texto.
        
        Args:
            texto: Texto para estimar duração
            
        Returns:
            int: Duração estimada em segundos
        """
        palavras_por_segundo = self.config['estrutura_roteiro']['palavras_por_segundo']
        num_palavras = len(texto.split())
        return int(num_palavras / palavras_por_segundo)
    
    def _selecionar_noticias_por_duracao(self, noticias: List[Noticia], duracao_alvo: int) -> List[Noticia]:
        """
        Seleciona notícias baseado na duração alvo.
        
        Args:
            noticias: Lista de notícias disponíveis
            duracao_alvo: Duração alvo em segundos
            
        Returns:
            List[Noticia]: Notícias selecionadas
        """
        config_estrutura = self.config['estrutura_roteiro']
        min_noticias = config_estrutura['min_noticias']
        max_noticias = config_estrutura['max_noticias']
        tempo_introducao = config_estrutura['tempo_introducao_segundos']
        tempo_encerramento = config_estrutura['tempo_encerramento_segundos']
        
        # Tempo disponível para notícias
        tempo_disponivel = duracao_alvo - tempo_introducao - tempo_encerramento
        
        noticias_selecionadas = []
        tempo_usado = 0
        
        for noticia in noticias:
            if len(noticias_selecionadas) >= max_noticias:
                break
            
            # Estimar duração da notícia
            tempo_noticia = self._estimar_duracao_texto(noticia.conteudo)
            
            # Adicionar tempo de transição (5 segundos)
            tempo_total_noticia = tempo_noticia + 5
            
            # Verificar se cabe
            if tempo_usado + tempo_total_noticia <= tempo_disponivel:
                noticias_selecionadas.append(noticia)
                tempo_usado += tempo_total_noticia
            elif len(noticias_selecionadas) >= min_noticias:
                # Já temos o mínimo, parar aqui
                break
        
        # Garantir pelo menos o mínimo de notícias
        if len(noticias_selecionadas) < min_noticias:
            noticias_selecionadas = noticias[:min_noticias]
        
        logger.info(f"Selecionadas {len(noticias_selecionadas)} notícias para duração de {duracao_alvo}s")
        logger.info(f"Tempo estimado usado: {tempo_usado}s de {tempo_disponivel}s disponíveis")
        
        return noticias_selecionadas
    
    def gerar_roteiro_completo(self, duracao_target: int = None) -> Dict[str, Any]:
        """
        Gera um roteiro completo baseado nas notícias mais recentes.
        
        Args:
            duracao_target: Duração alvo em segundos (se None, usa configuração padrão)
            
        Returns:
            Dict: Roteiro completo estruturado
        """
        logger.info("Gerando roteiro completo...")
        
        # Obter configurações de duração
        config_estrutura = self.config['estrutura_roteiro']
        duracao_min = config_estrutura['duracao_target_min']
        duracao_max = config_estrutura['duracao_target_max']
        duracao_alvo = duracao_target or duracao_max
        
        # Obter notícias
        noticias = self.news_collector.obter_noticias_para_roteiro()
        
        if not noticias:
            logger.error("Nenhuma notícia encontrada")
            return None
        
        # Selecionar notícias baseado na duração
        noticias_selecionadas = self._selecionar_noticias_por_duracao(noticias, duracao_alvo)
        
        # Gerar introdução
        introducao = random.choice(self.templates['introducoes_variadas'])
        
        # Gerar segmentos
        segmentos = []
        transicoes = self.templates['transicoes'].copy()
        random.shuffle(transicoes)
        
        for i, noticia in enumerate(noticias_selecionadas):
            transicao = transicoes[i % len(transicoes)]
            segmento = self._criar_segmento_noticia(noticia, transicao)
            segmentos.append(segmento)
        
        # Gerar encerramento
        encerramento = self._criar_encerramento(segmentos)
        
        # Montar roteiro final
        texto_completo = introducao
        for segmento in segmentos:
            texto_completo += f"\n\n{segmento.texto}"
        texto_completo += f"\n\n{encerramento}"
        
        # Calcular duração final
        duracao_estimada = self._estimar_duracao_texto(texto_completo)
        
        # Estruturar dados
        roteiro = {
            "id": f"rapidinha_ia_gerada_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "data_criacao": datetime.now().isoformat(),
            "tipo": "rapidinha_cripto_ia",
            "fonte": "ia_automatica",
            "noticias_utilizadas": [
                {
                    "titulo": n.titulo,
                    "fonte": n.fonte,
                    "relevancia": n.relevancia_score,
                    "duracao_estimada": self._estimar_duracao_texto(n.conteudo)
                } for n in noticias_selecionadas
            ],
            
            "roteiro_estruturado": {
                "introducao": introducao,
                "segmentos": [
                    {
                        "titulo": s.titulo,
                        "texto": s.texto,
                        "categoria": s.categoria,
                        "duracao_estimada": self._estimar_duracao_texto(s.texto)
                    } for s in segmentos
                ],
                "encerramento": encerramento
            },
            
            "texto_completo": texto_completo,
            
            "configuracoes_geracao": {
                "voice_profile": "fluido",
                "voice_id": self.config.get('voice_id', 'default'),
                "formato": "portrait",
                "avatar_rotacao": True
            },
            
            "controle_duracao": {
                "duracao_alvo_segundos": duracao_alvo,
                "duracao_estimada_segundos": duracao_estimada,
                "duracao_minutos": round(duracao_estimada / 60, 1),
                "dentro_limite": duracao_min <= duracao_estimada <= duracao_max,
                "num_noticias": len(noticias_selecionadas),
                "palavras_total": len(texto_completo.split())
            },
            
            "metadados": {
                "num_segmentos": len(segmentos),
                "categorias_abordadas": list(set(s.categoria for s in segmentos)),
                "score_medio_relevancia": sum(n.relevancia_score for n in noticias_selecionadas) / len(noticias_selecionadas),
                "vies_aplicado": "libertario_educativo"
            }
        }
        
        logger.info(f"Roteiro gerado com {len(segmentos)} segmentos")
        logger.info(f"Duração estimada: {duracao_estimada}s ({round(duracao_estimada/60, 1)} min)")
        logger.info(f"Dentro do limite: {'✅' if roteiro['controle_duracao']['dentro_limite'] else '❌'}")
        return roteiro
    
    def salvar_roteiro(self, roteiro: Dict[str, Any], diretorio: str = None) -> str:
        """
        Salva roteiro em arquivo JSON.
        
        Args:
            roteiro: Dados do roteiro
            diretorio: Diretório para salvar
            
        Returns:
            str: Caminho do arquivo salvo
        """
        if not diretorio:
            diretorio = os.path.join(os.path.dirname(__file__), "..", "..", "ml_training", "roteiros_exemplos")
        
        os.makedirs(diretorio, exist_ok=True)
        
        filename = f"{roteiro['id']}.json"
        filepath = os.path.join(diretorio, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(roteiro, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Roteiro salvo em: {filepath}")
        return filepath


if __name__ == "__main__":
    # Teste do gerador
    generator = ScriptGenerator()
    
    print("🤖 Gerando roteiro com IA...")
    roteiro = generator.gerar_roteiro_completo()
    
    if roteiro:
        # Salvar roteiro
        filepath = generator.salvar_roteiro(roteiro)
        
        print(f"\n🎯 ROTEIRO GERADO:")
        print("=" * 60)
        print(f"📝 ID: {roteiro['id']}")
        print(f"📊 Segmentos: {roteiro['metadados']['num_segmentos']}")
        print(f"🏷️ Categorias: {', '.join(roteiro['metadados']['categorias_abordadas'])}")
        print(f"📈 Score médio: {roteiro['metadados']['score_medio_relevancia']:.1f}")
        
        print(f"\n⏱️ CONTROLE DE DURAÇÃO:")
        print("-" * 30)
        duracao_info = roteiro['controle_duracao']
        print(f"🎯 Duração alvo: {duracao_info['duracao_alvo_segundos']}s")
        print(f"📏 Duração estimada: {duracao_info['duracao_estimada_segundos']}s ({duracao_info['duracao_minutos']} min)")
        print(f"📰 Número de notícias: {duracao_info['num_noticias']}")
        print(f"📝 Total de palavras: {duracao_info['palavras_total']}")
        print(f"✅ Dentro do limite: {'Sim' if duracao_info['dentro_limite'] else 'Não'}")
        
        print(f"\n📄 TEXTO COMPLETO:")
        print("-" * 40)
        # Mostrar apenas primeiro parágrafo para economizar espaço
        texto_preview = roteiro['texto_completo'][:500] + "..." if len(roteiro['texto_completo']) > 500 else roteiro['texto_completo']
        print(texto_preview)
        
        print(f"\n📊 DETALHES POR SEGMENTO:")
        print("-" * 40)
        for i, segmento in enumerate(roteiro['roteiro_estruturado']['segmentos'], 1):
            print(f"{i}. {segmento['titulo'][:60]}...")
            print(f"   ⏱️ {segmento['duracao_estimada']}s | 🏷️ {segmento['categoria']}")
            # Mostrar primeiro trecho do texto real
            texto_real = segmento['texto'].split('\n')[0][:80] + "..."
            print(f"   📝 {texto_real}")
            print()
        
        print(f"\n💾 Salvo em: {filepath}")
    else:
        print("❌ Erro ao gerar roteiro")