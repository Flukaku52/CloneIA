#!/usr/bin/env python3
"""
Gerador de scripts para a Rapidinha com base em notícias e tweets sobre criptomoedas.
"""
import os
import re
import sys
import json
import random
import logging
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gerador_script_rapidinha')

# Importar módulos de busca
try:
    from buscador_noticias_cripto import NoticiasCriptoScraper, PORTAIS
    from buscador_tweets_cripto import TwitterCriptoScraper, CONTAS_CRIPTO, TERMOS_BUSCA
except ImportError:
    logger.error("Módulos de busca não encontrados. Certifique-se de que os arquivos estão no mesmo diretório.")
    sys.exit(1)

class GeradorScriptRapidinha:
    """
    Classe para gerar scripts para a Rapidinha com base em notícias e tweets.
    Foco em conteúdo acessível para público leigo em criptomoedas.
    Suporta carregamento de padrões extraídos de Reels existentes.
    """
    def __init__(self, output_dir: str = "output/scripts", patterns_file: str = None):
        """
        Inicializa o gerador de scripts.

        Args:
            output_dir: Diretório para salvar os scripts gerados
            patterns_file: Arquivo com padrões extraídos de Reels existentes
        """
        self.output_dir = output_dir

        # Criar diretório de saída se não existir
        os.makedirs(self.output_dir, exist_ok=True)

        # Inicializar scrapers
        self.noticias_scraper = NoticiasCriptoScraper()
        self.twitter_scraper = TwitterCriptoScraper()

        # Templates para o script
        self.templates_intro = [
            "E aí cambada, tô de volta na área e bora de Rapidinha!",
            "Fala cambada! Chegou a Rapidinha com as novidades do mundo cripto!",
            "E aí galera, beleza? Bora de Rapidinha com as últimas do Bitcoin!",
            "Salve salve, cambada! É hora da Rapidinha com as bombas do mercado cripto!",
            "Fala meus amigos, tudo bem? Rapidinha na área com as notícias quentes!"
        ]

        self.templates_desafio = [
            "Mas tem um desafio: algo tá diferente nesse vídeo, adivinha o que?\n\nBota nos comentários, no fim eu revelo!",
            "Desafio pra vocês: tem algo diferente nesse vídeo. Consegue descobrir?\n\nComenta aí embaixo, no final eu conto!",
            "Repara bem: tem algo novo nesse vídeo. Consegue identificar?\n\nDeixa nos comentários, no fim do vídeo eu revelo!",
            "Desafio rápido: algo mudou nesse vídeo. Percebeu o que foi?\n\nComenta aí, no final eu mostro a resposta!",
            "Olha com atenção: tem algo diferente hoje. Sabe dizer o que é?\n\nDeixa sua resposta nos comentários!"
        ]

        self.templates_transicao = [
            "Agora, vamos às notícias que todo mundo consegue entender!",
            "Bora ver o que tá rolando no mundo cripto de forma simples!",
            "Vamos às novidades da semana explicadas de um jeito fácil!",
            "Olha só o que tá bombando no mercado de um jeito que todo mundo entende!",
            "Confere só as notícias que separei pra você, sem complicação!"
        ]

        self.templates_conclusao = [
            "Por hoje é isso, galera!",
            "E é isso aí, pessoal!",
            "Por hoje é só, cambada!",
            "Chegamos ao fim de mais uma Rapidinha!",
            "E assim fechamos mais uma Rapidinha!"
        ]

        self.templates_resposta_desafio = [
            "Resposta do desafio: eu não sou o Renato real, sou o RenatoIA, um clone de IA!",
            "E a resposta do desafio é: este vídeo foi feito por IA! Eu sou o RenatoIA!",
            "Descobriu o desafio? Eu sou uma versão IA do Renato, criada com inteligência artificial!",
            "E o que tinha de diferente? Simples: eu sou o RenatoIA, uma versão digital do Renato original!",
            "Resposta: este vídeo foi 100% gerado por IA! Eu sou o RenatoIA, clone digital do Renato!"
        ]

        self.templates_despedida = [
            "Valeu e um abraço!",
            "Até a próxima e um abraço!",
            "Nos vemos na próxima Rapidinha!",
            "Valeu galera, até mais!",
            "Um abraço e até a próxima!"
        ]

        # Hashtags comuns (serão preenchidas se patterns_file for fornecido)
        self.hashtags_comuns = []

        # Perguntas adicionais (serão preenchidas se patterns_file for fornecido)
        self.perguntas_adicionais = []

        # Estilo de escrita (será preenchido se patterns_file for fornecido)
        self.estilo_escrita = {
            "sentence_length": 12,  # Comprimento médio padrão das frases
            "emoji_frequency": {},
            "common_phrases": []
        }

        # Termos técnicos e suas explicações simplificadas
        self.explicacoes_termos = {
            "blockchain": "tecnologia que funciona como um livro-caixa digital",
            "DeFi": "finanças descentralizadas, um jeito de fazer transações financeiras sem bancos",
            "NFT": "arte digital com certificado de autenticidade",
            "staking": "processo de guardar cripto para ganhar recompensas, tipo uma poupança",
            "wallet": "carteira digital onde você guarda suas criptomoedas",
            "smart contract": "contrato digital que executa automaticamente",
            "token": "moeda digital criada em cima de uma blockchain",
            "altcoin": "qualquer criptomoeda que não seja Bitcoin",
            "mining": "processo de validar transações e ganhar recompensas",
            "halving": "evento que reduz pela metade a recompensa dos mineradores de Bitcoin",
            "hash rate": "poder de processamento da rede Bitcoin",
            "cold storage": "guardar criptomoedas offline para maior segurança",
            "exchange": "corretora onde você compra e vende criptomoedas",
            "gas fee": "taxa que você paga para fazer transações",
            "yield farming": "estratégia para maximizar ganhos com criptomoedas"
        }

        # Temas de interesse para público leigo
        self.temas_interesse_leigos = [
            "adoção de Bitcoin",
            "pagamentos com cripto",
            "compra de Bitcoin",
            "investimento em cripto",
            "carteira de Bitcoin",
            "segurança de criptomoedas",
            "preço do Bitcoin",
            "como começar em cripto",
            "bancos e Bitcoin",
            "empresas aceitando cripto",
            "regulamentação de cripto",
            "impostos sobre cripto",
            "golpes com criptomoedas",
            "dicas para iniciantes",
            "corretoras de cripto"
        ]

        # Carregar padrões se o arquivo for fornecido
        if patterns_file:
            self.carregar_padroes(patterns_file)

    def carregar_padroes(self, patterns_file: str) -> bool:
        """
        Carrega padrões extraídos de Reels existentes.

        Args:
            patterns_file: Caminho para o arquivo de padrões

        Returns:
            bool: True se os padrões foram carregados com sucesso
        """
        try:
            with open(patterns_file, 'r', encoding='utf-8') as f:
                patterns = json.load(f)

            # Atualizar templates com os padrões carregados
            if "intro_phrases" in patterns and patterns["intro_phrases"]:
                # Manter alguns templates padrão e adicionar os extraídos
                self.templates_intro = self.templates_intro[:2] + patterns["intro_phrases"]

            if "transition_phrases" in patterns and patterns["transition_phrases"]:
                # Manter alguns templates padrão e adicionar os extraídos
                self.templates_transicao = self.templates_transicao[:2] + patterns["transition_phrases"]

            if "conclusion_phrases" in patterns and patterns["conclusion_phrases"]:
                # Manter alguns templates padrão e adicionar os extraídos
                self.templates_conclusao = self.templates_conclusao[:2] + patterns["conclusion_phrases"]

            # Adicionar perguntas extraídas
            if "question_patterns" in patterns and patterns["question_patterns"]:
                self.perguntas_adicionais = patterns["question_patterns"]

            # Armazenar hashtags comuns
            if "hashtags" in patterns and patterns["hashtags"]:
                self.hashtags_comuns = patterns["hashtags"]

            # Armazenar estilo de escrita
            if "style_patterns" in patterns:
                style = patterns["style_patterns"]

                if "sentence_length" in style:
                    self.estilo_escrita["sentence_length"] = style["sentence_length"]

                if "emoji_frequency" in style:
                    self.estilo_escrita["emoji_frequency"] = style["emoji_frequency"]

                if "common_phrases" in style:
                    self.estilo_escrita["common_phrases"] = style["common_phrases"]

            logger.info(f"Padrões carregados com sucesso de {patterns_file}")
            logger.info(f"Carregadas {len(self.perguntas_adicionais)} perguntas e {len(self.hashtags_comuns)} hashtags")
            return True

        except Exception as e:
            logger.error(f"Erro ao carregar padrões: {e}")
            return False

    def _formatar_noticia(self, noticia: Dict[str, Any]) -> str:
        """
        Formata uma notícia para o script, simplificando termos técnicos e
        tornando o conteúdo mais acessível para público leigo.

        Args:
            noticia: Dados da notícia

        Returns:
            str: Texto formatado para o script
        """
        # Extrair data da notícia
        data_str = ""
        if noticia.get("data_iso"):
            try:
                data = datetime.fromisoformat(noticia["data_iso"])
                data_str = f"em {data.day} de {self._nome_mes(data.month)}"
            except:
                data_str = noticia.get("data", "")

        # Criar texto da notícia
        titulo = noticia["titulo"]
        portal = noticia["portal"]
        resumo = noticia.get("resumo", "")

        # Limitar o resumo a 1-2 frases
        if resumo:
            frases = re.split(r'[.!?]+', resumo)
            frases = [f for f in frases if f.strip()]
            if frases:
                resumo = '. '.join(frases[:min(2, len(frases))]) + '.'

        # Verificar se a notícia é sobre um tema de interesse para leigos
        relevancia_para_leigos = False
        for tema in self.temas_interesse_leigos:
            if tema.lower() in titulo.lower() or (resumo and tema.lower() in resumo.lower()):
                relevancia_para_leigos = True
                break

        # Adicionar introdução específica para notícias relevantes para leigos
        introducoes_leigos = [
            "Essa notícia é super importante pra quem tá começando: ",
            "Olha só essa notícia que todo mundo precisa saber: ",
            "Essa é fácil de entender e super importante: ",
            "Presta atenção nessa que é relevante pra todo mundo: ",
            "Essa notícia afeta até quem não entende nada de cripto: "
        ]

        # Montar texto
        texto = f"{titulo}\n\n"

        # Adicionar introdução especial para notícias relevantes para leigos
        if relevancia_para_leigos:
            texto += random.choice(introducoes_leigos)

        if data_str:
            texto += f"Segundo o {portal} {data_str}, "
        else:
            texto += f"De acordo com o {portal}, "

        if resumo:
            # Simplificar termos técnicos no resumo
            resumo_simplificado = resumo
            for termo, explicacao in self.explicacoes_termos.items():
                if termo.lower() in resumo_simplificado.lower():
                    # Substituir apenas a primeira ocorrência do termo
                    padrao = re.compile(re.escape(termo), re.IGNORECASE)
                    match = padrao.search(resumo_simplificado)
                    if match:
                        termo_original = match.group(0)
                        resumo_simplificado = resumo_simplificado.replace(
                            termo_original,
                            f"{termo_original} ({explicacao})",
                            1
                        )

            texto += f"{resumo_simplificado}\n\n"

        # Adicionar uma explicação extra para notícias mais técnicas
        termos_encontrados = []
        for termo in self.explicacoes_termos:
            if termo.lower() in titulo.lower() or (resumo and termo.lower() in resumo.lower()):
                termos_encontrados.append(termo)

        if termos_encontrados and not relevancia_para_leigos:
            texto += "Explicando de forma simples: "
            if len(termos_encontrados) == 1:
                termo = termos_encontrados[0]
                texto += f"essa notícia fala sobre {termo} que é {self.explicacoes_termos[termo]}.\n\n"
            else:
                texto += "essa notícia envolve termos técnicos como "
                for i, termo in enumerate(termos_encontrados[:2]):  # Limitar a 2 termos para não ficar muito longo
                    if i > 0:
                        texto += " e "
                    texto += f"{termo} ({self.explicacoes_termos[termo]})"
                texto += ".\n\n"

        # Adicionar dica para iniciantes quando relevante
        dicas_iniciantes = [
            "Dica para iniciantes: comece estudando antes de investir!",
            "Lembre-se: no mundo cripto, conhecimento é tão importante quanto dinheiro!",
            "Para quem tá começando: vá com calma e estude bastante!",
            "Importante: sempre pesquise bem antes de colocar seu dinheiro!",
            "Conselho rápido: nunca invista o que não pode perder!"
        ]

        if relevancia_para_leigos and random.random() < 0.3:  # 30% de chance de adicionar uma dica
            texto += random.choice(dicas_iniciantes) + "\n\n"

        return texto

    def _formatar_tweet(self, tweet: Dict[str, Any]) -> str:
        """
        Formata um tweet para o script, simplificando termos técnicos para o público leigo.

        Args:
            tweet: Dados do tweet

        Returns:
            str: Texto formatado para o script
        """
        # Extrair informações do tweet
        texto = tweet["text"]
        autor = tweet.get("author_username", "")

        # Limpar o texto (remover URLs, etc.)
        texto = re.sub(r'https?://\S+', '', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()

        # Simplificar termos técnicos no texto do tweet
        texto_simplificado = texto
        termos_encontrados = []

        for termo, explicacao in self.explicacoes_termos.items():
            if termo.lower() in texto_simplificado.lower():
                # Substituir apenas a primeira ocorrência do termo
                padrao = re.compile(re.escape(termo), re.IGNORECASE)
                match = padrao.search(texto_simplificado)
                if match:
                    termo_original = match.group(0)
                    texto_simplificado = texto_simplificado.replace(
                        termo_original,
                        f"{termo_original}",
                        1
                    )
                    termos_encontrados.append(termo)

        # Montar texto
        resultado = ""
        if autor:
            resultado = f"@{autor} tweetou: \"{texto_simplificado}\"\n\n"
        else:
            resultado = f"Um usuário do Twitter comentou: \"{texto_simplificado}\"\n\n"

        # Adicionar explicações para termos técnicos encontrados
        if termos_encontrados:
            resultado += "Traduzindo para quem não é expert: "
            for i, termo in enumerate(termos_encontrados[:2]):  # Limitar a 2 termos
                if i > 0:
                    resultado += " e "
                resultado += f"{termo} é {self.explicacoes_termos[termo]}"
            resultado += ".\n\n"

        # Verificar se o tweet é sobre um tema de interesse para leigos
        relevancia_para_leigos = False
        for tema in self.temas_interesse_leigos:
            if tema.lower() in texto.lower():
                relevancia_para_leigos = True
                break

        # Adicionar comentário para tweets relevantes para leigos
        comentarios_leigos = [
            "Esse tweet é super importante pra quem tá começando!",
            "Essa informação é valiosa pra quem quer entender o básico de cripto!",
            "Presta atenção nesse tweet, é conhecimento essencial!",
            "Guarda essa dica, vai te ajudar muito no começo da jornada!",
            "Esse é o tipo de informação que todo iniciante deveria saber!"
        ]

        if relevancia_para_leigos and random.random() < 0.4:  # 40% de chance
            resultado += random.choice(comentarios_leigos) + "\n\n"

        return resultado

    def _nome_mes(self, mes: int) -> str:
        """
        Retorna o nome do mês em português.

        Args:
            mes: Número do mês (1-12)

        Returns:
            str: Nome do mês em português
        """
        meses = [
            "janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
        ]
        return meses[mes - 1] if 1 <= mes <= 12 else ""

    def _selecionar_conteudo(self, noticias: List[Dict[str, Any]], tweets: List[Dict[str, Any]],
                           num_noticias: int = 5, num_tweets: int = 2) -> List[Dict[str, Any]]:
        """
        Seleciona o conteúdo mais relevante para o script, priorizando conteúdo
        acessível para público leigo em criptomoedas.

        Args:
            noticias: Lista de notícias
            tweets: Lista de tweets
            num_noticias: Número de notícias a selecionar
            num_tweets: Número de tweets a selecionar

        Returns:
            List[Dict[str, Any]]: Lista de conteúdos selecionados
        """
        # Filtrar notícias duplicadas (por título similar)
        titulos_vistos = set()
        noticias_unicas = []

        for noticia in noticias:
            # Simplificar o título para comparação
            titulo_simples = re.sub(r'[^\w\s]', '', noticia["titulo"].lower())
            palavras = set(titulo_simples.split())

            # Verificar se já temos uma notícia similar
            duplicada = False
            for titulo in titulos_vistos:
                palavras_titulo = set(titulo.split())
                # Se há mais de 60% de palavras em comum, considerar duplicada
                if len(palavras.intersection(palavras_titulo)) / len(palavras.union(palavras_titulo)) > 0.6:
                    duplicada = True
                    break

            if not duplicada:
                titulos_vistos.add(titulo_simples)
                noticias_unicas.append(noticia)

        # Classificar notícias por relevância para público leigo
        noticias_para_leigos = []
        noticias_gerais = []

        for noticia in noticias_unicas:
            titulo = noticia["titulo"].lower()
            resumo = noticia.get("resumo", "").lower()

            # Verificar se a notícia é sobre um tema de interesse para leigos
            relevante_para_leigos = False
            for tema in self.temas_interesse_leigos:
                if tema.lower() in titulo or tema.lower() in resumo:
                    relevante_para_leigos = True
                    break

            # Verificar se a notícia contém termos técnicos complexos
            termos_tecnicos = 0
            for termo in self.explicacoes_termos:
                if termo.lower() in titulo or termo.lower() in resumo:
                    termos_tecnicos += 1

            # Classificar a notícia
            if relevante_para_leigos and termos_tecnicos <= 2:
                # Notícia relevante para leigos e não muito técnica
                noticias_para_leigos.append(noticia)
            else:
                noticias_gerais.append(noticia)

        # Priorizar notícias para leigos, mas garantir diversidade
        noticias_selecionadas = []

        # Garantir que pelo menos 60% das notícias sejam para leigos
        num_leigos = min(int(num_noticias * 0.6), len(noticias_para_leigos))
        num_gerais = num_noticias - num_leigos

        # Adicionar notícias para leigos (priorizando as mais recentes)
        noticias_selecionadas.extend(noticias_para_leigos[:num_leigos])

        # Adicionar notícias gerais (priorizando as mais recentes)
        noticias_selecionadas.extend(noticias_gerais[:num_gerais])

        # Se ainda não temos notícias suficientes, adicionar mais de qualquer categoria
        if len(noticias_selecionadas) < num_noticias:
            noticias_restantes = [n for n in noticias_unicas if n not in noticias_selecionadas]
            noticias_selecionadas.extend(noticias_restantes[:num_noticias - len(noticias_selecionadas)])

        # Classificar tweets por relevância para público leigo
        tweets_para_leigos = []
        tweets_gerais = []

        for tweet in tweets:
            texto = tweet["text"].lower()

            # Verificar se o tweet é sobre um tema de interesse para leigos
            relevante_para_leigos = False
            for tema in self.temas_interesse_leigos:
                if tema.lower() in texto:
                    relevante_para_leigos = True
                    break

            # Verificar se o tweet contém termos técnicos complexos
            termos_tecnicos = 0
            for termo in self.explicacoes_termos:
                if termo.lower() in texto:
                    termos_tecnicos += 1

            # Classificar o tweet
            if relevante_para_leigos and termos_tecnicos <= 2:
                # Tweet relevante para leigos e não muito técnico
                tweets_para_leigos.append(tweet)
            else:
                tweets_gerais.append(tweet)

        # Ordenar tweets por engajamento dentro de cada categoria
        tweets_para_leigos.sort(key=lambda x: x.get("likes", 0) + x.get("retweets", 0), reverse=True)
        tweets_gerais.sort(key=lambda x: x.get("likes", 0) + x.get("retweets", 0), reverse=True)

        # Priorizar tweets para leigos, mas garantir diversidade
        tweets_selecionados = []

        # Garantir que pelo menos 60% dos tweets sejam para leigos
        num_leigos = min(int(num_tweets * 0.6), len(tweets_para_leigos))
        num_gerais = num_tweets - num_leigos

        # Adicionar tweets para leigos
        tweets_selecionados.extend(tweets_para_leigos[:num_leigos])

        # Adicionar tweets gerais
        tweets_selecionados.extend(tweets_gerais[:num_gerais])

        # Se ainda não temos tweets suficientes, adicionar mais de qualquer categoria
        if len(tweets_selecionados) < num_tweets:
            tweets_restantes = [t for t in tweets if t not in tweets_selecionados]
            tweets_restantes.sort(key=lambda x: x.get("likes", 0) + x.get("retweets", 0), reverse=True)
            tweets_selecionados.extend(tweets_restantes[:num_tweets - len(tweets_selecionados)])

        # Combinar e ordenar o conteúdo
        # Vamos intercalar notícias e tweets para variar o conteúdo
        conteudo = []

        # Começar com uma notícia para leigos, se disponível
        if noticias_para_leigos and noticias_selecionadas:
            primeira_noticia = next((n for n in noticias_selecionadas if n in noticias_para_leigos), noticias_selecionadas[0])
            conteudo.append({
                "tipo": "noticia",
                "dados": primeira_noticia
            })
            noticias_selecionadas.remove(primeira_noticia)

        # Intercalar o restante do conteúdo
        for i in range(max(len(noticias_selecionadas), len(tweets_selecionados))):
            if i < len(tweets_selecionados):
                conteudo.append({
                    "tipo": "tweet",
                    "dados": tweets_selecionados[i]
                })

            if i < len(noticias_selecionadas):
                conteudo.append({
                    "tipo": "noticia",
                    "dados": noticias_selecionadas[i]
                })

        return conteudo[:num_noticias + num_tweets]

    def _gerar_perguntas(self, conteudo: List[Dict[str, Any]]) -> List[str]:
        """
        Gera perguntas para engajar a audiência com base no conteúdo,
        focando em perguntas acessíveis para público leigo.
        Utiliza perguntas extraídas de Reels existentes, se disponíveis.

        Args:
            conteudo: Lista de conteúdos selecionados

        Returns:
            List[str]: Lista de perguntas geradas
        """
        # Perguntas gerais para qualquer público
        perguntas_gerais = [
            "O que vocês acham disso?",
            "Vocês concordam?",
            "Qual a opinião de vocês?",
            "Isso chamou a atenção de vocês?",
            "Vocês já tinham ouvido falar disso?"
        ]

        # Perguntas específicas para público leigo
        perguntas_leigos = [
            "Vocês que estão começando agora, entenderam essa notícia?",
            "Isso parece complicado ou dá pra entender fácil?",
            "Quem tá começando agora em cripto, isso ajuda ou confunde?",
            "Vocês acham que vale a pena estudar mais sobre isso?",
            "Isso deixa vocês mais animados ou com medo de entrar no mundo cripto?",
            "Vocês conseguem ver como isso afeta quem tá começando?",
            "Isso faz vocês quererem aprender mais sobre Bitcoin?",
            "Essa notícia deixou as coisas mais claras ou mais confusas?",
            "Vocês se sentem mais seguros depois de saber disso?",
            "Isso é algo que vocês contariam para um amigo que não entende nada de cripto?"
        ]

        # Perguntas sobre investimentos para iniciantes
        perguntas_investimento = [
            "Quem nunca investiu em cripto, isso anima ou assusta?",
            "Vocês acham que é hora de começar a investir ou melhor esperar?",
            "Para quem tá começando, melhor estudar mais ou já ir testando com pouco dinheiro?",
            "Vocês preferem começar com Bitcoin ou com outras criptomoedas?",
            "Isso faz vocês quererem aprender mais antes de investir?"
        ]

        # Adicionar perguntas extraídas de Reels existentes, se disponíveis
        perguntas_extraidas = []
        if hasattr(self, 'perguntas_adicionais') and self.perguntas_adicionais:
            perguntas_extraidas = self.perguntas_adicionais
            logger.info(f"Adicionando {len(perguntas_extraidas)} perguntas extraídas de Reels existentes")

        # Combinar as perguntas, priorizando as extraídas e as para leigos
        todas_perguntas = perguntas_extraidas + perguntas_leigos + perguntas_investimento + perguntas_gerais

        # Verificar se há termos técnicos no conteúdo
        termos_tecnicos_encontrados = set()
        for item in conteudo:
            if item["tipo"] == "noticia":
                titulo = item["dados"]["titulo"].lower()
                resumo = item["dados"].get("resumo", "").lower()

                for termo in self.explicacoes_termos:
                    if termo.lower() in titulo or (resumo and termo.lower() in resumo):
                        termos_tecnicos_encontrados.add(termo)

            elif item["tipo"] == "tweet":
                texto = item["dados"]["text"].lower()

                for termo in self.explicacoes_termos:
                    if termo.lower() in texto:
                        termos_tecnicos_encontrados.add(termo)

        # Adicionar perguntas específicas sobre termos técnicos encontrados
        for termo in termos_tecnicos_encontrados:
            perguntas_termo = [
                f"Vocês já conheciam o que é {termo}?",
                f"Alguém aí já usou ou teve contato com {termo}?",
                f"Vocês acham que {termo} é algo importante de entender?",
                f"A explicação sobre {termo} ajudou vocês a entenderem melhor?"
            ]
            todas_perguntas.extend(perguntas_termo)

        # Garantir que não temos perguntas duplicadas
        todas_perguntas = list(set(todas_perguntas))

        # Selecionar perguntas aleatoriamente, priorizando as extraídas
        num_perguntas = min(3, len(todas_perguntas))

        # Se temos perguntas extraídas, garantir que pelo menos uma seja usada
        if perguntas_extraidas and num_perguntas > 0:
            perguntas_selecionadas = [random.choice(perguntas_extraidas)]
            todas_perguntas = [p for p in todas_perguntas if p not in perguntas_selecionadas]
            perguntas_selecionadas.extend(random.sample(todas_perguntas, num_perguntas - 1))
            return perguntas_selecionadas
        else:
            return random.sample(todas_perguntas, num_perguntas)

    def _gerar_secao_noticia(self, noticia: Dict[str, Any], perguntas: List[str]) -> str:
        """
        Gera uma seção do script para uma notícia.

        Args:
            noticia: Dados da notícia
            perguntas: Lista de perguntas para engajamento

        Returns:
            str: Texto da seção
        """
        texto = self._formatar_noticia(noticia)

        # Adicionar uma pergunta aleatória para engajamento
        if perguntas:
            texto += f"{random.choice(perguntas)}\n\n"

        return texto

    def _gerar_secao_tweet(self, tweet: Dict[str, Any]) -> str:
        """
        Gera uma seção do script para um tweet.

        Args:
            tweet: Dados do tweet

        Returns:
            str: Texto da seção
        """
        texto = self._formatar_tweet(tweet)
        return texto

    def gerar_script(self, num_noticias: int = 5, num_tweets: int = 2,
                    max_noticias_busca: int = 15, max_tweets_busca: int = 10) -> str:
        """
        Gera um script completo para a Rapidinha.

        Args:
            num_noticias: Número de notícias a incluir no script
            num_tweets: Número de tweets a incluir no script
            max_noticias_busca: Número máximo de notícias a buscar
            max_tweets_busca: Número máximo de tweets a buscar

        Returns:
            str: Script completo
        """
        logger.info("Gerando script para a Rapidinha...")

        # Buscar notícias
        logger.info("Buscando notícias...")
        noticias = self.noticias_scraper.buscar_todas_noticias(
            max_por_portal=5,
            max_total=max_noticias_busca
        )

        # Buscar tweets
        logger.info("Buscando tweets...")
        tweets_termos = self.twitter_scraper.buscar_tweets_por_termos(
            TERMOS_BUSCA,
            max_por_termo=2,
            max_total=max_tweets_busca // 2
        )

        tweets_contas = self.twitter_scraper.buscar_tweets_por_contas(
            CONTAS_CRIPTO,
            max_por_conta=1,
            max_total=max_tweets_busca // 2
        )

        tweets = tweets_termos + tweets_contas

        # Selecionar conteúdo
        logger.info("Selecionando conteúdo...")
        conteudo = self._selecionar_conteudo(noticias, tweets, num_noticias, num_tweets)

        # Gerar perguntas para engajamento
        perguntas = self._gerar_perguntas(conteudo)

        # Construir o script
        logger.info("Construindo o script...")

        # Introdução
        script = random.choice(self.templates_intro) + "\n\n"

        # Desafio
        script += random.choice(self.templates_desafio) + "\n\n"

        # Marcador de corte
        script += "(Corte)\n\n"

        # Transição
        script += random.choice(self.templates_transicao) + "\n\n"

        # Conteúdo principal
        for i, item in enumerate(conteudo):
            if item["tipo"] == "noticia":
                script += self._gerar_secao_noticia(item["dados"], perguntas)
            else:  # tweet
                script += self._gerar_secao_tweet(item["dados"])

            # Adicionar marcador de corte entre as seções
            if i < len(conteudo) - 1:
                script += "(Corte)\n\n"

        # Conclusão
        script += random.choice(self.templates_conclusao) + "\n\n"

        # Resposta do desafio
        script += random.choice(self.templates_resposta_desafio) + " "

        # Despedida
        script += random.choice(self.templates_despedida) + "\n\n"

        # Adicionar hashtags extraídas dos Reels, se disponíveis
        if hasattr(self, 'hashtags_comuns') and self.hashtags_comuns:
            # Selecionar algumas hashtags aleatórias
            num_hashtags = min(5, len(self.hashtags_comuns))
            hashtags_selecionadas = random.sample(self.hashtags_comuns, num_hashtags)

            # Adicionar hashtags padrão
            hashtags_padrao = ["#bitcoin", "#cripto", "#criptomoedas", "#rapidinha", "#flukaku"]

            # Combinar e remover duplicatas
            todas_hashtags = list(set(hashtags_padrao + hashtags_selecionadas))

            # Adicionar ao script
            script += " ".join(todas_hashtags)

            logger.info(f"Adicionadas {len(todas_hashtags)} hashtags ao script")

        logger.info("Script gerado com sucesso!")

        return script

    def salvar_script(self, script: str, nome_arquivo: str = None) -> str:
        """
        Salva o script em um arquivo.

        Args:
            script: Texto do script
            nome_arquivo: Nome do arquivo (se None, gera um nome baseado na data)

        Returns:
            str: Caminho para o arquivo salvo
        """
        if nome_arquivo is None:
            data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"rapidinha_{data_hora}.txt"

        caminho_arquivo = os.path.join(self.output_dir, nome_arquivo)

        try:
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(script)

            logger.info(f"Script salvo em {caminho_arquivo}")
            return caminho_arquivo
        except Exception as e:
            logger.error(f"Erro ao salvar o script: {e}")
            return None

def main():
    """
    Função principal para gerar um script para a Rapidinha.
    """
    parser = argparse.ArgumentParser(description="Gerador de scripts para a Rapidinha")
    parser.add_argument("--noticias", type=int, default=5, help="Número de notícias a incluir no script")
    parser.add_argument("--tweets", type=int, default=2, help="Número de tweets a incluir no script")
    parser.add_argument("--output", help="Nome do arquivo de saída")
    parser.add_argument("--gerar-video", action="store_true", help="Gerar vídeo automaticamente após criar o script")
    parser.add_argument("--patterns", help="Arquivo com padrões extraídos de Reels existentes")

    args = parser.parse_args()

    # Criar o gerador de scripts
    gerador = GeradorScriptRapidinha(patterns_file=args.patterns)

    # Verificar se carregou padrões
    if args.patterns:
        logger.info(f"Usando padrões do arquivo: {args.patterns}")

    # Gerar o script
    script = gerador.gerar_script(
        num_noticias=args.noticias,
        num_tweets=args.tweets
    )

    # Salvar o script
    caminho_script = gerador.salvar_script(script, args.output)

    # Exibir o script
    print("\n" + "="*50)
    print("SCRIPT GERADO PARA A RAPIDINHA")
    print("="*50 + "\n")
    print(script)
    print("\n" + "="*50)

    # Gerar vídeo se solicitado
    if args.gerar_video and caminho_script:
        try:
            from gerar_reels_automatico import ReelsGenerator

            print("\nGerando vídeo automaticamente...")

            # Criar o gerador de vídeos
            reels_generator = ReelsGenerator(
                script_path=caminho_script,
                prefix="rapidinha_auto"
            )

            # Processar o script
            resultados = reels_generator.processar_script()

            print(f"\nVídeo gerado com sucesso!")
            print(f"Scripts: {len(resultados['scripts'])}")
            print(f"Áudios: {len(resultados['audios'])}")
            print(f"Vídeos: {len(resultados['videos'])}")
        except ImportError:
            print("\nNão foi possível gerar o vídeo automaticamente.")
            print("Certifique-se de que o módulo 'gerar_reels_automatico.py' está disponível.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
