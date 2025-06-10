#!/usr/bin/env python3
"""
Sistema de análise e aprendizado de padrões de roteiros
"""

import json
import re
import os
from typing import Dict, List, Tuple
from datetime import datetime
from collections import Counter

class AnalisadorRoteiros:
    """Analisa roteiros para extrair padrões e estilo de escrita"""
    
    def __init__(self):
        self.padroes_extraidos = {
            "estrutura": {},
            "linguagem": {},
            "transicoes": [],
            "vocabulario": {},
            "estilos": {},
            "metadata": {}
        }
        
    def analisar_roteiro_atual(self):
        """Analisa o roteiro atual para extrair padrões"""
        
        # Roteiro atual (extraído do generate_reel_correto.py)
        roteiro_atual = {
            "intro": {
                "text": "E aí cambada! Já tô de volta por aqui e bora pras notícias.",
                "funcao": "abertura_energica",
                "elementos": ["saudacao_caracteristica", "chamada_acao"]
            },
            "noticia1": {
                "text": """Empresas já têm mais de 3% do supply de BTC.

Seguinte: segundo o banco Standard Chartered, 61 empresas que têm ações em bolsa já acumulam 3,2% de todo o Bitcoin que vai existir no mundo.

Entre elas estão MicroStrategy, Tesla e outras gigantes que tão comprando BTC pra colocar em caixa, como reserva de valor.

Em vez de só dólar ou ouro, agora tem empresa diversificando com Bitcoin.
Isso reforça que o BTC não é mais só papo de investidor de rede social — tá virando um ativo institucional.""",
                "funcao": "noticia_principal_bitcoin",
                "elementos": ["titulo_impactante", "fonte_credivel", "exemplos_concretos", "contextualizacao", "conclusao_mercado"]
            },
            "noticia2": {
                "text": """Blockchain pode modernizar abertura de empresas no Brasil.

Agora uma que pouca gente tá falando:
Tem projeto de lei no Congresso propondo que a gente use blockchain nos registros de abertura de empresas.

A ideia é garantir que os dados fiquem imutáveis e rastreáveis.
Menos chance de fraude, mais transparência, e processos mais rápidos.

Hoje abrir empresa no Brasil ainda tem muita burocracia e sistema velho.
Se isso andar, seria um baita uso prático de blockchain — além do mercado cripto — que realmente impacta a vida de quem empreende.""",
                "funcao": "noticia_brasil_blockchain",
                "elementos": ["titulo_claro", "gancho_exclusividade", "explicacao_tecnica", "beneficios_praticos", "critica_sistema_atual", "impacto_real"]
            },
            "noticia3": {
                "text": """Drex chega à Amazônia.

Agora presta atenção nessa aqui:
A Caixa Econômica Federal tá testando o Drex, o real digital, em comunidades da Amazônia que não têm nem internet.

A tecnologia permite que o morador faça pagamentos off-line, e quando o celular se conecta à rede, tudo é sincronizado.

É um avanço grande pra inclusão financeira — levar pagamento digital pra quem hoje tá fora do sistema.

Mas... a gente também tem que olhar pro outro lado dessa moeda.
Diferente do dinheiro físico — que você gasta sem deixar rastro — o Drex é uma moeda totalmente rastreável e programável.

Na prática, isso significa que o governo poderia, tecnicamente, monitorar e até controlar como você gasta seu dinheiro.

Então assim:
Tecnologia boa? Sim.
Mas liberdade financeira precisa estar no centro dessa conversa.
A gente tem que ficar muito atento pra isso não virar ferramenta de controle.""",
                "funcao": "noticia_controversa_analise_dupla",
                "elementos": ["titulo_intrigante", "chamada_atencao", "explicacao_tecnica", "lado_positivo", "contraargumento", "analise_critica", "conclusao_equilibrada", "alerta_vigilancia"]
            },
            "encerramento": {
                "text": "Por hoje é isso, cambada. Em breve tô de volta, e sigo de olho.",
                "funcao": "fechamento_promessa_retorno",
                "elementos": ["encerramento_caracteristico", "promessa_continuidade", "reforco_vigilancia"]
            }
        }
        
        print("🔍 ANALISANDO PADRÕES DO ROTEIRO ATUAL")
        print("=" * 50)
        
        # Analisar estrutura
        self._analisar_estrutura(roteiro_atual)
        
        # Analisar linguagem
        self._analisar_linguagem(roteiro_atual)
        
        # Analisar transições
        self._analisar_transicoes(roteiro_atual)
        
        # Analisar vocabulário
        self._analisar_vocabulario(roteiro_atual)
        
        # Analisar estilo narrativo
        self._analisar_estilo(roteiro_atual)
        
        # Salvar padrões
        self._salvar_padroes()
        
        return self.padroes_extraidos
    
    def _analisar_estrutura(self, roteiro: Dict):
        """Analisa a estrutura do roteiro"""
        
        estrutura = {
            "total_segmentos": len(roteiro),
            "ordem_segmentos": list(roteiro.keys()),
            "funcoes_por_segmento": {k: v["funcao"] for k, v in roteiro.items()},
            "tamanho_medio_segmentos": {},
            "proporcao_conteudo": {}
        }
        
        # Calcular tamanhos
        for segmento, dados in roteiro.items():
            texto = dados["text"]
            estrutura["tamanho_medio_segmentos"][segmento] = {
                "caracteres": len(texto),
                "palavras": len(texto.split()),
                "linhas": len(texto.split('\n'))
            }
        
        # Proporções
        total_chars = sum(len(v["text"]) for v in roteiro.values())
        for segmento, dados in roteiro.items():
            chars = len(dados["text"])
            estrutura["proporcao_conteudo"][segmento] = round(chars / total_chars * 100, 1)
        
        self.padroes_extraidos["estrutura"] = estrutura
        
        print("📊 Estrutura identificada:")
        print(f"  • {len(roteiro)} segmentos")
        print(f"  • Proporções: {estrutura['proporcao_conteudo']}")
    
    def _analisar_linguagem(self, roteiro: Dict):
        """Analisa padrões de linguagem"""
        
        linguagem = {
            "tom": "informal_brasileiro",
            "pessoa_verbal": "primeira_pessoa_plural", # "a gente", "tô"
            "expressoes_caracteristicas": [],
            "conectores_frequentes": [],
            "estruturas_frase": [],
            "marcadores_discursivos": []
        }
        
        # Extrair texto completo
        texto_completo = " ".join([v["text"] for v in roteiro.values()])
        
        # Expressões características encontradas
        expressoes = [
            "E aí cambada", "cambada", "Seguinte:", "Agora", "presta atenção", 
            "pouca gente tá falando", "a gente", "tô", "bora", "baita",
            "Então assim:", "Por hoje é isso"
        ]
        
        linguagem["expressoes_caracteristicas"] = [
            expr for expr in expressoes if expr.lower() in texto_completo.lower()
        ]
        
        # Conectores
        conectores = [
            "Seguinte:", "Agora", "Mas...", "Na prática", "Então assim:",
            "Se isso andar", "Entre elas", "Em vez de", "Diferente do"
        ]
        
        linguagem["conectores_frequentes"] = [
            conector for conector in conectores if conector in texto_completo
        ]
        
        # Marcadores discursivos
        marcadores = [
            "segundo o", "presta atenção", "a gente também tem que",
            "tecnicamente", "realmente impacta", "ficar muito atento"
        ]
        
        linguagem["marcadores_discursivos"] = [
            marcador for marcador in marcadores if marcador.lower() in texto_completo.lower()
        ]
        
        self.padroes_extraidos["linguagem"] = linguagem
        
        print("🗣️ Linguagem identificada:")
        print(f"  • Tom: {linguagem['tom']}")
        print(f"  • Expressões características: {len(linguagem['expressoes_caracteristicas'])}")
    
    def _analisar_transicoes(self, roteiro: Dict):
        """Analisa padrões de transição entre segmentos"""
        
        transicoes = []
        segmentos = list(roteiro.keys())
        
        # Padrões identificados
        padroes_transicao = {
            "intro_para_noticia": ["bora pras notícias", "vamos às notícias"],
            "entre_noticias": ["Agora", "Seguinte:", "Agora presta atenção"],
            "para_encerramento": ["Por hoje é isso", "É isso aí"]
        }
        
        # Identificar transições no roteiro atual
        if "intro" in roteiro and "noticia1" in roteiro:
            if "bora pras notícias" in roteiro["intro"]["text"]:
                transicoes.append({
                    "de": "intro",
                    "para": "noticia1", 
                    "mecanismo": "bora pras notícias",
                    "tipo": "chamada_energica"
                })
        
        # Entre notícias
        noticias = [k for k in segmentos if k.startswith("noticia")]
        for i in range(len(noticias) - 1):
            atual = noticias[i]
            proxima = noticias[i + 1]
            
            # Verificar se próxima notícia começa com marcador
            texto_proxima = roteiro[proxima]["text"]
            if texto_proxima.startswith("Agora"):
                transicoes.append({
                    "de": atual,
                    "para": proxima,
                    "mecanismo": "Agora",
                    "tipo": "introducao_nova_perspectiva"
                })
        
        self.padroes_extraidos["transicoes"] = transicoes
        
        print("🔄 Transições identificadas:")
        print(f"  • {len(transicoes)} padrões de transição")
    
    def _analisar_vocabulario(self, roteiro: Dict):
        """Analisa vocabulário específico"""
        
        # Extrair palavras-chave por categoria
        vocabulario = {
            "termos_tecnicos": {
                "crypto": ["Bitcoin", "BTC", "blockchain", "Drex", "cripto", "supply"],
                "financeiro": ["reserva de valor", "ativo institucional", "diversificando", "inclusão financeira"],
                "tecnologia": ["off-line", "sincronizado", "rastreável", "programável", "imutáveis"]
            },
            "expressoes_brasil": [
                "no Brasil", "brasileiro", "Congresso", "Caixa Econômica Federal", 
                "Amazônia", "burocracia", "sistema velho"
            ],
            "linguagem_coloquial": [
                "cambada", "tô", "bora", "baita", "galera", "pouca gente",
                "a gente", "papo de"
            ],
            "conectores_analise": [
                "Na prática", "Então assim", "Mas", "Diferente do",
                "Em vez de", "segundo o", "tecnicamente"
            ]
        }
        
        self.padroes_extraidos["vocabulario"] = vocabulario
        
        print("📚 Vocabulário identificado:")
        print(f"  • Termos técnicos: {len(vocabulario['termos_tecnicos']['crypto']) + len(vocabulario['termos_tecnicos']['financeiro'])}")
        print(f"  • Expressões BR: {len(vocabulario['expressoes_brasil'])}")
    
    def _analisar_estilo(self, roteiro: Dict):
        """Analisa estilo narrativo"""
        
        estilo = {
            "abordagem_noticias": {
                "estrutura_padrao": [
                    "titulo_impactante",
                    "fonte_ou_contexto", 
                    "explicacao_detalhada",
                    "implicacoes_praticas",
                    "opiniao_pessoal"
                ],
                "tecnica_engagement": [
                    "dados_numericos_especificos", # 3,2%, 61 empresas
                    "exemplos_conhecidos", # MicroStrategy, Tesla
                    "contrapontos_equilibrados", # lado bom vs. riscos
                    "alertas_vigilancia" # "ficar atento"
                ]
            },
            "personalidade": {
                "tom_geral": "informativo_descontraido", 
                "posicionamento": "critico_equilibrado",
                "relacionamento_audiencia": "proxima_coloquial",
                "nivel_tecnico": "acessivel_com_profundidade"
            },
            "padroes_narrativos": {
                "uso_dados": "sempre_com_fonte",
                "exemplos": "empresas_conhecidas_e_casos_brasileiros", 
                "conclusoes": "provocativas_mas_equilibradas",
                "call_to_action": "implícito_vigilancia_critica"
            }
        }
        
        self.padroes_extraidos["estilos"] = estilo
        
        print("🎭 Estilo identificado:")
        print(f"  • Tom: {estilo['personalidade']['tom_geral']}")
        print(f"  • Posicionamento: {estilo['personalidade']['posicionamento']}")
    
    def _salvar_padroes(self):
        """Salva padrões extraídos para uso futuro"""
        
        # Adicionar metadata
        self.padroes_extraidos["metadata"] = {
            "versao": "1.0",
            "data_analise": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "roteiro_analisado": "reel_cripto_empresas_drex_junho_2025",
            "total_segmentos_analisados": len(self.padroes_extraidos["estrutura"]["ordem_segmentos"]),
            "objetivo": "aprender_padroes_para_geracao_automatica"
        }
        
        # Criar diretório se não existir
        os.makedirs("ml_training/padroes_aprendidos", exist_ok=True)
        
        # Salvar arquivo JSON
        arquivo_padroes = "ml_training/padroes_aprendidos/padroes_roteiro_v1.json"
        with open(arquivo_padroes, 'w', encoding='utf-8') as f:
            json.dump(self.padroes_extraidos, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Padrões salvos em: {arquivo_padroes}")
        
        # Criar arquivo de resumo legível
        self._criar_resumo_padroes()
    
    def _criar_resumo_padroes(self):
        """Cria resumo legível dos padrões"""
        
        resumo = f"""
# PADRÕES APRENDIDOS DO ROTEIRO
Análise realizada em: {self.padroes_extraidos['metadata']['data_analise']}

## ESTRUTURA DO ROTEIRO
- **Total de segmentos:** {self.padroes_extraidos['estrutura']['total_segmentos']}
- **Ordem:** {' → '.join(self.padroes_extraidos['estrutura']['ordem_segmentos'])}
- **Proporções de conteúdo:** {self.padroes_extraidos['estrutura']['proporcao_conteudo']}

## LINGUAGEM E TOM
- **Tom geral:** {self.padroes_extraidos['estilos']['personalidade']['tom_geral']}
- **Expressões características:** {', '.join(self.padroes_extraidos['linguagem']['expressoes_caracteristicas'][:5])}
- **Conectores frequentes:** {', '.join(self.padroes_extraidos['linguagem']['conectores_frequentes'][:5])}

## PADRÕES NARRATIVOS
- **Abordagem:** Sempre com fonte credível + exemplos concretos + análise crítica
- **Estrutura notícia:** Título → Contexto → Explicação → Implicações → Opinião
- **Estilo de conclusão:** Equilibrado mas provocativo, incentiva pensamento crítico

## VOCABULÁRIO TÉCNICO
- **Crypto:** {', '.join(self.padroes_extraidos['vocabulario']['termos_tecnicos']['crypto'])}
- **Financeiro:** {', '.join(self.padroes_extraidos['vocabulario']['termos_tecnicos']['financeiro'])}

## ELEMENTOS DE ENGAJAMENTO
- Dados numéricos específicos (3,2%, 61 empresas)
- Empresas conhecidas como exemplos (Tesla, MicroStrategy)
- Contrapontos equilibrados (benefícios vs. riscos)
- Linguagem acessível mas com profundidade técnica
"""
        
        with open("ml_training/padroes_aprendidos/resumo_padroes.md", 'w', encoding='utf-8') as f:
            f.write(resumo)
        
        print("📋 Resumo criado: ml_training/padroes_aprendidos/resumo_padroes.md")


if __name__ == "__main__":
    print("🤖 SISTEMA DE APRENDIZADO DE ROTEIROS")
    print("Analisando o roteiro atual para extrair padrões...")
    print()
    
    analisador = AnalisadorRoteiros()
    padroes = analisador.analisar_roteiro_atual()
    
    print("\n✅ ANÁLISE CONCLUÍDA!")
    print("Os padrões foram extraídos e salvos para treinar a IA.")
    print("Próximo passo: Implementar gerador automático de roteiros.")