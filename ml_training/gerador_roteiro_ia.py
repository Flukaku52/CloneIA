#!/usr/bin/env python3
"""
Gerador automático de roteiros baseado em padrões aprendidos
"""

import json
import random
import re
from typing import Dict, List, Optional
from datetime import datetime

class GeradorRoteiro:
    """Gera roteiros automaticamente seguindo os padrões aprendidos"""
    
    def __init__(self):
        self.padroes = self._carregar_padroes()
        self.templates_estrutura = self._criar_templates()
    
    def _carregar_padroes(self) -> Dict:
        """Carrega padrões aprendidos"""
        try:
            with open("ml_training/padroes_aprendidos/padroes_roteiro_v1.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Padrões não encontrados! Execute analisador_roteiros.py primeiro")
            return {}
    
    def _criar_templates(self) -> Dict:
        """Cria templates baseados nos padrões"""
        
        return {
            "intro": {
                "templates": [
                    "E aí cambada! Já tô de volta por aqui e bora pras notícias.",
                    "E aí cambada! Mais um dia, mais notícias do cripto. Bora lá!",
                    "Fala cambada! Tô aqui de novo e vamos às notícias que tão movimentando."
                ],
                "elementos": ["saudacao_energica", "promessa_conteudo", "call_to_action"]
            },
            
            "noticia_estrutura": {
                "template_base": [
                    "titulo_impactante",
                    "transicao_contextual", 
                    "fonte_dados_especificos",
                    "exemplos_concretos",
                    "implicacoes_praticas",
                    "conclusao_critica"
                ],
                "conectores_inicio": [
                    "Seguinte:",
                    "Agora uma que pouca gente tá falando:",
                    "Presta atenção nessa aqui:",
                    "Olha só isso:"
                ],
                "conectores_fonte": [
                    "segundo",
                    "de acordo com",
                    "conforme dados de",
                    "segundo relatório do/da"
                ],
                "conectores_implicacao": [
                    "Na prática, isso significa",
                    "Em outras palavras",
                    "O que isso quer dizer?",
                    "Traduzindo:"
                ],
                "conclusoes_criticas": [
                    "Então assim:",
                    "Mas a gente tem que",
                    "Por outro lado,",
                    "Isso levanta uma questão importante:"
                ]
            },
            
            "encerramento": {
                "templates": [
                    "Por hoje é isso, cambada. Em breve tô de volta, e sigo de olho.",
                    "É isso aí por hoje, cambada. Continuo acompanhando e já volto com mais.",
                    "Por hoje fica por aqui, cambada. Em breve tô de volta com mais novidades."
                ],
                "elementos": ["fechamento_caracteristico", "promessa_retorno", "vigilancia_continuada"]
            }
        }
    
    def gerar_roteiro_automatico(self, noticias_input: List[Dict]) -> Dict:
        """
        Gera roteiro completo baseado em notícias fornecidas
        
        Args:
            noticias_input: Lista de dicts com keys: titulo, conteudo, fonte, categoria
        """
        
        print("🤖 GERANDO ROTEIRO AUTOMÁTICO")
        print("=" * 40)
        
        if not noticias_input:
            print("❌ Nenhuma notícia fornecida!")
            return {}
        
        # Gerar cada segmento
        roteiro = {}
        
        # 1. Intro
        roteiro["intro"] = self._gerar_intro()
        
        # 2. Notícias (máximo 3)
        noticias_selecionadas = noticias_input[:3]
        for i, noticia in enumerate(noticias_selecionadas, 1):
            roteiro[f"noticia{i}"] = self._gerar_segmento_noticia(noticia, i)
        
        # 3. Encerramento
        roteiro["encerramento"] = self._gerar_encerramento()
        
        # Salvar roteiro gerado
        self._salvar_roteiro_gerado(roteiro)
        
        return roteiro
    
    def _gerar_intro(self) -> Dict:
        """Gera introdução seguindo padrões"""
        
        template = random.choice(self.templates_estrutura["intro"]["templates"])
        
        return {
            "id": "intro",
            "title": "Abertura",
            "text": template,
            "gerado_automaticamente": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def _gerar_segmento_noticia(self, noticia: Dict, numero: int) -> Dict:
        """Gera segmento de notícia seguindo padrões aprendidos"""
        
        # Componentes baseados nos padrões
        titulo = noticia.get("titulo", "Notícia importante")
        conteudo = noticia.get("conteudo", "")
        fonte = noticia.get("fonte", "fontes do mercado")
        categoria = noticia.get("categoria", "geral")
        
        # Escolher conector de início baseado no número da notícia
        if numero == 1:
            conector_inicio = "Seguinte:"
        else:
            conector_inicio = random.choice(self.templates_estrutura["noticia_estrutura"]["conectores_inicio"])
        
        # Montar texto seguindo estrutura aprendida
        texto_segmentos = []
        
        # 1. Título impactante (adaptado)
        titulo_adaptado = self._adaptar_titulo(titulo)
        texto_segmentos.append(titulo_adaptado)
        
        # 2. Transição contextual
        texto_segmentos.append(f"\n{conector_inicio}")
        
        # 3. Conteúdo com fonte
        conector_fonte = random.choice(self.templates_estrutura["noticia_estrutura"]["conectores_fonte"])
        if fonte:
            conteudo_com_fonte = f"{conector_fonte} {fonte}, {conteudo}"
        else:
            conteudo_com_fonte = conteudo
        
        texto_segmentos.append(conteudo_com_fonte)
        
        # 4. Implicação prática (usando padrões)
        conector_implicacao = random.choice(self.templates_estrutura["noticia_estrutura"]["conectores_implicacao"])
        implicacao = self._gerar_implicacao_categoria(categoria)
        
        if implicacao:
            texto_segmentos.append(f"\n{conector_implicacao} {implicacao}")
        
        # 5. Conclusão crítica (seguindo estilo)
        conclusao = self._gerar_conclusao_critica(categoria)
        if conclusao:
            conector_conclusao = random.choice(self.templates_estrutura["noticia_estrutura"]["conclusoes_criticas"])
            texto_segmentos.append(f"\n{conector_conclusao} {conclusao}")
        
        texto_final = "".join(texto_segmentos)
        
        return {
            "id": f"noticia{numero}",
            "title": titulo,
            "text": texto_final,
            "categoria": categoria,
            "fonte": fonte,
            "gerado_automaticamente": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def _adaptar_titulo(self, titulo_original: str) -> str:
        """Adapta título para o estilo do canal"""
        
        # Remover pontuação excessiva, manter direto
        titulo_limpo = re.sub(r'[!?]{2,}', '.', titulo_original)
        titulo_limpo = titulo_limpo.rstrip('.')
        
        # Adicionar ponto final se não tiver
        if not titulo_limpo.endswith(('.', '!', '?')):
            titulo_limpo += '.'
        
        return titulo_limpo
    
    def _gerar_implicacao_categoria(self, categoria: str) -> str:
        """Gera implicação prática baseada na categoria"""
        
        implicacoes_por_categoria = {
            "bitcoin": [
                "isso mostra que o Bitcoin tá consolidando como reserva de valor institucional",
                "cada vez mais empresas veem BTC como proteção contra inflação",
                "o mercado institucional tá validando Bitcoin como ativo sério"
            ],
            "blockchain": [
                "isso pode revolucionar a transparência de processos burocráticos",
                "blockchain resolve problemas reais de confiança e rastreabilidade",
                "é um uso prático da tecnologia além do mercado cripto"
            ],
            "regulamentacao": [
                "isso define como o mercado cripto vai funcionar no Brasil",
                "regulamentação clara traz mais segurança pros investidores",
                "é o primeiro passo pra adoção mainstream"
            ],
            "cbdc": [
                "moedas digitais de bancos centrais são o futuro dos pagamentos",
                "isso pode incluir milhões de pessoas no sistema financeiro digital",
                "mas também levanta questões sobre privacidade e controle"
            ],
            "geral": [
                "isso impacta diretamente quem investe em cripto",
                "são mudanças que vão afetar o mercado como um todo",
                "é uma tendência que tá ganhando força globalmente"
            ]
        }
        
        categoria_lower = categoria.lower()
        opcoes = implicacoes_por_categoria.get(categoria_lower, implicacoes_por_categoria["geral"])
        
        return random.choice(opcoes)
    
    def _gerar_conclusao_critica(self, categoria: str) -> str:
        """Gera conclusão crítica/equilibrada baseada na categoria"""
        
        conclusoes_por_categoria = {
            "bitcoin": [
                "adoção institucional é boa, mas concentração também preocupa.",
                "mais legitimidade pro Bitcoin, mas será que não tá ficando muito centralizado?",
                "é evolução natural, mas a gente tem que acompanhar se isso não muda a essência descentralizada."
            ],
            "regulamentacao": [
                "regulamentação é necessária, mas não pode sufocar a inovação.",
                "clareza é boa, mas a gente tem que garantir que não limite demais.",
                "equilíbrio entre proteção e liberdade é fundamental."
            ],
            "cbdc": [
                "tecnologia boa? Sim. Mas liberdade financeira precisa estar no centro dessa conversa.",
                "inclusão é importante, mas vigilância excessiva é um risco real.",
                "avanço tecnológico é positivo, mas controle governamental pode ser problemático."
            ],
            "geral": [
                "evolução é natural, mas sempre com olho crítico nas consequências.",
                "novidades são empolgantes, mas prudência nunca é demais.",
                "mudanças trazem oportunidades e riscos - importante equilibrar ambos."
            ]
        }
        
        categoria_lower = categoria.lower() 
        opcoes = conclusoes_por_categoria.get(categoria_lower, conclusoes_por_categoria["geral"])
        
        return random.choice(opcoes)
    
    def _gerar_encerramento(self) -> Dict:
        """Gera encerramento seguindo padrões"""
        
        template = random.choice(self.templates_estrutura["encerramento"]["templates"])
        
        return {
            "id": "encerramento", 
            "title": "Fechamento",
            "text": template,
            "gerado_automaticamente": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def _salvar_roteiro_gerado(self, roteiro: Dict):
        """Salva roteiro gerado"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo = f"ml_training/roteiros_exemplos/roteiro_gerado_{timestamp}.json"
        
        metadata = {
            "gerado_em": datetime.now().isoformat(),
            "versao_ia": "1.0",
            "baseado_em_padroes": "padroes_roteiro_v1.json",
            "total_segmentos": len(roteiro),
            "roteiro": roteiro
        }
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Roteiro salvo: {arquivo}")


def exemplo_uso():
    """Exemplo de como usar o gerador"""
    
    # Exemplo de notícias que você forneceria
    noticias_exemplo = [
        {
            "titulo": "BlackRock compra mais R$ 500 milhões em Bitcoin",
            "conteudo": "O maior gestor de ativos do mundo aumentou sua posição em Bitcoin através do ETF IBIT, comprando mais 8.000 BTC na última semana.",
            "fonte": "SEC filings",
            "categoria": "bitcoin"
        },
        {
            "titulo": "Banco Central lança piloto do Drex em 5 cidades",
            "conteudo": "Programa piloto vai testar pagamentos instantâneos com moeda digital em São Paulo, Rio, Brasília, Salvador e Recife.",
            "fonte": "Banco Central",
            "categoria": "cbdc"
        },
        {
            "titulo": "CVM aprova novo marco regulatório para exchanges",
            "conteudo": "Novas regras exigem segregação de ativos dos clientes e seguro obrigatório para todas as corretoras de criptomoedas.",
            "fonte": "CVM",
            "categoria": "regulamentacao"
        }
    ]
    
    gerador = GeradorRoteiro()
    roteiro_automatico = gerador.gerar_roteiro_automatico(noticias_exemplo)
    
    print("\n📺 ROTEIRO GERADO:")
    print("=" * 30)
    for segmento_id, dados in roteiro_automatico.items():
        print(f"\n🎬 {dados['title'].upper()}")
        print(f"📝 {dados['text']}")


if __name__ == "__main__":
    print("🤖 GERADOR AUTOMÁTICO DE ROTEIROS")
    print("Baseado em padrões aprendidos do seu estilo")
    print()
    
    exemplo_uso()