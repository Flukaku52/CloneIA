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
    """
    def __init__(self, output_dir: str = "output/scripts"):
        """
        Inicializa o gerador de scripts.
        
        Args:
            output_dir: Diretório para salvar os scripts gerados
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
            "Agora, vamos às notícias!",
            "Bora ver o que tá rolando no mundo cripto!",
            "Vamos às novidades da semana!",
            "Olha só o que tá bombando no mercado!",
            "Confere só as notícias que separei pra você!"
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
    
    def _formatar_noticia(self, noticia: Dict[str, Any]) -> str:
        """
        Formata uma notícia para o script.
        
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
        
        # Montar texto
        texto = f"{titulo}\n\n"
        if data_str:
            texto += f"Segundo o {portal} {data_str}, "
        else:
            texto += f"De acordo com o {portal}, "
        
        if resumo:
            texto += f"{resumo}\n\n"
        
        return texto
    
    def _formatar_tweet(self, tweet: Dict[str, Any]) -> str:
        """
        Formata um tweet para o script.
        
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
        
        # Montar texto
        if autor:
            return f"@{autor} tweetou: \"{texto}\"\n\n"
        else:
            return f"Um usuário do Twitter comentou: \"{texto}\"\n\n"
    
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
        Seleciona o conteúdo mais relevante para o script.
        
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
        
        # Selecionar as notícias mais recentes
        noticias_selecionadas = noticias_unicas[:num_noticias]
        
        # Selecionar os tweets com mais engajamento
        tweets_selecionados = sorted(tweets, key=lambda x: x.get("likes", 0) + x.get("retweets", 0), reverse=True)[:num_tweets]
        
        # Combinar e ordenar o conteúdo
        # Vamos intercalar notícias e tweets para variar o conteúdo
        conteudo = []
        for i in range(max(len(noticias_selecionadas), len(tweets_selecionados))):
            if i < len(noticias_selecionadas):
                conteudo.append({
                    "tipo": "noticia",
                    "dados": noticias_selecionadas[i]
                })
            
            if i < len(tweets_selecionados):
                conteudo.append({
                    "tipo": "tweet",
                    "dados": tweets_selecionados[i]
                })
        
        return conteudo[:num_noticias + num_tweets]
    
    def _gerar_perguntas(self, conteudo: List[Dict[str, Any]]) -> List[str]:
        """
        Gera perguntas para engajar a audiência com base no conteúdo.
        
        Args:
            conteudo: Lista de conteúdos selecionados
            
        Returns:
            List[str]: Lista de perguntas geradas
        """
        perguntas = [
            "O que vocês acham disso?",
            "Vocês concordam?",
            "Isso vai mudar o mercado?",
            "Vocês já testaram essa novidade?",
            "Isso é bom para o Bitcoin?",
            "Vocês investiriam nisso?",
            "Qual a opinião de vocês?",
            "Isso vai valorizar ou desvalorizar?",
            "Vocês acreditam nessa tendência?",
            "Isso vai se manter no longo prazo?"
        ]
        
        return random.sample(perguntas, min(3, len(perguntas)))
    
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
    
    def _gerar_secao_tweet(self, tweet: Dict[str, Any], perguntas: List[str]) -> str:
        """
        Gera uma seção do script para um tweet.
        
        Args:
            tweet: Dados do tweet
            perguntas: Lista de perguntas para engajamento
            
        Returns:
            str: Texto da seção
        """
        texto = self._formatar_tweet(tweet)
        
        # Adicionar uma pergunta aleatória para engajamento
        if perguntas:
            texto += f"{random.choice(perguntas)}\n\n"
        
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
                script += self._gerar_secao_tweet(item["dados"], perguntas)
            
            # Adicionar marcador de corte entre as seções
            if i < len(conteudo) - 1:
                script += "(Corte)\n\n"
        
        # Conclusão
        script += random.choice(self.templates_conclusao) + "\n\n"
        
        # Resposta do desafio
        script += random.choice(self.templates_resposta_desafio) + " "
        
        # Despedida
        script += random.choice(self.templates_despedida) + "\n"
        
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
    
    args = parser.parse_args()
    
    # Criar o gerador de scripts
    gerador = GeradorScriptRapidinha()
    
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
