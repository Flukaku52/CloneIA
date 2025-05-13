#!/usr/bin/env python3
"""
Script para analisar os dados dos Reels da Rapidinha e extrair padrões.
"""
import os
import re
import json
import logging
import argparse
from typing import List, Dict, Any, Set, Tuple
from datetime import datetime
from collections import Counter

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('rapidinha_analyzer')

class RapidinhaPatternsAnalyzer:
    """
    Classe para analisar padrões nos Reels da Rapidinha.
    """
    def __init__(self, output_dir: str = "output/patterns"):
        """
        Inicializa o analisador de padrões.
        
        Args:
            output_dir: Diretório para salvar os padrões extraídos
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Padrões a serem extraídos
        self.patterns = {
            "intro_phrases": [],
            "transition_phrases": [],
            "conclusion_phrases": [],
            "question_patterns": [],
            "hashtags": [],
            "topics": [],
            "engagement_patterns": [],
            "style_patterns": {
                "sentence_length": 0,
                "emoji_frequency": {},
                "common_phrases": [],
                "tone": "informative"
            }
        }
        
        # Palavras-chave para identificar diferentes partes do conteúdo
        self.intro_keywords = [
            "e aí cambada", "fala cambada", "e aí galera", "salve salve", 
            "fala meus amigos", "bora de rapidinha", "chegou a rapidinha"
        ]
        
        self.transition_keywords = [
            "agora vamos", "bora ver", "vamos às", "olha só", "confere só"
        ]
        
        self.conclusion_keywords = [
            "por hoje é isso", "e é isso aí", "por hoje é só", 
            "chegamos ao fim", "e assim fechamos", "valeu galera", "até a próxima"
        ]
        
        # Palavras-chave relacionadas a criptomoedas
        self.crypto_keywords = [
            "bitcoin", "btc", "ethereum", "eth", "cripto", "criptomoeda", 
            "blockchain", "defi", "nft", "token", "altcoin", "halving",
            "wallet", "carteira", "exchange", "corretora", "investimento"
        ]
    
    def analyze_reels_data(self, reels_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa os dados dos Reels para extrair padrões.
        
        Args:
            reels_data: Lista de dados dos Reels
            
        Returns:
            Dict[str, Any]: Padrões extraídos
        """
        logger.info(f"Analisando {len(reels_data)} Reels...")
        
        # Extrair legendas
        captions = [reel.get("caption", "") for reel in reels_data if reel.get("caption")]
        
        # Analisar hashtags
        self._analyze_hashtags(captions)
        
        # Analisar tópicos
        self._analyze_topics(captions)
        
        # Analisar frases de introdução, transição e conclusão
        self._analyze_phrases(captions)
        
        # Analisar perguntas
        self._analyze_questions(captions)
        
        # Analisar padrões de estilo
        self._analyze_style(captions)
        
        # Analisar padrões de engajamento
        self._analyze_engagement(reels_data)
        
        return self.patterns
    
    def _analyze_hashtags(self, captions: List[str]) -> None:
        """
        Analisa as hashtags nas legendas.
        
        Args:
            captions: Lista de legendas
        """
        # Extrair todas as hashtags
        all_hashtags = []
        for caption in captions:
            # Encontrar todas as hashtags (palavras que começam com #)
            hashtags = re.findall(r'#\w+', caption.lower())
            all_hashtags.extend(hashtags)
        
        # Contar frequência
        hashtag_counter = Counter(all_hashtags)
        
        # Obter as hashtags mais comuns
        most_common = hashtag_counter.most_common(20)
        self.patterns["hashtags"] = [tag for tag, count in most_common]
        
        logger.info(f"Extraídas {len(self.patterns['hashtags'])} hashtags comuns")
    
    def _analyze_topics(self, captions: List[str]) -> None:
        """
        Analisa os tópicos nas legendas.
        
        Args:
            captions: Lista de legendas
        """
        # Contar ocorrências de palavras-chave
        topic_counts = {}
        for caption in captions:
            lower_caption = caption.lower()
            for keyword in self.crypto_keywords:
                if keyword in lower_caption:
                    topic_counts[keyword] = topic_counts.get(keyword, 0) + 1
        
        # Ordenar por frequência
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        self.patterns["topics"] = [topic for topic, count in sorted_topics[:15]]
        
        logger.info(f"Extraídos {len(self.patterns['topics'])} tópicos comuns")
    
    def _analyze_phrases(self, captions: List[str]) -> None:
        """
        Analisa frases de introdução, transição e conclusão.
        
        Args:
            captions: Lista de legendas
        """
        intro_phrases = []
        transition_phrases = []
        conclusion_phrases = []
        
        for caption in captions:
            lines = caption.split("\n")
            
            # Analisar introduções (geralmente nas primeiras linhas)
            for line in lines[:3]:
                lower_line = line.lower()
                for keyword in self.intro_keywords:
                    if keyword in lower_line:
                        intro_phrases.append(line.strip())
                        break
            
            # Analisar transições (podem estar em qualquer lugar)
            for line in lines:
                lower_line = line.lower()
                for keyword in self.transition_keywords:
                    if keyword in lower_line:
                        transition_phrases.append(line.strip())
                        break
            
            # Analisar conclusões (geralmente nas últimas linhas)
            for line in lines[-5:]:
                lower_line = line.lower()
                for keyword in self.conclusion_keywords:
                    if keyword in lower_line:
                        conclusion_phrases.append(line.strip())
                        break
        
        # Remover duplicatas e limitar
        self.patterns["intro_phrases"] = list(set(intro_phrases))[:10]
        self.patterns["transition_phrases"] = list(set(transition_phrases))[:10]
        self.patterns["conclusion_phrases"] = list(set(conclusion_phrases))[:10]
        
        logger.info(f"Extraídas {len(self.patterns['intro_phrases'])} frases de introdução")
        logger.info(f"Extraídas {len(self.patterns['transition_phrases'])} frases de transição")
        logger.info(f"Extraídas {len(self.patterns['conclusion_phrases'])} frases de conclusão")
    
    def _analyze_questions(self, captions: List[str]) -> None:
        """
        Analisa perguntas nas legendas.
        
        Args:
            captions: Lista de legendas
        """
        questions = []
        
        for caption in captions:
            # Dividir por linhas
            lines = caption.split("\n")
            
            for line in lines:
                # Verificar se é uma pergunta (contém ponto de interrogação)
                if "?" in line and len(line) < 150:
                    questions.append(line.strip())
        
        # Remover duplicatas e limitar
        self.patterns["question_patterns"] = list(set(questions))[:15]
        
        logger.info(f"Extraídas {len(self.patterns['question_patterns'])} perguntas")
    
    def _analyze_style(self, captions: List[str]) -> None:
        """
        Analisa o estilo de escrita nas legendas.
        
        Args:
            captions: Lista de legendas
        """
        # Calcular comprimento médio das frases
        sentence_lengths = []
        all_sentences = []
        
        for caption in captions:
            # Dividir em frases
            sentences = re.split(r'[.!?]+', caption)
            sentences = [s.strip() for s in sentences if s.strip()]
            all_sentences.extend(sentences)
            
            # Calcular comprimentos
            lengths = [len(s.split()) for s in sentences]
            sentence_lengths.extend(lengths)
        
        # Comprimento médio das frases
        if sentence_lengths:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            self.patterns["style_patterns"]["sentence_length"] = round(avg_length, 1)
        
        # Analisar emojis
        emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)
        all_emojis = []
        
        for caption in captions:
            emojis = emoji_pattern.findall(caption)
            all_emojis.extend(emojis)
        
        # Contar frequência de emojis
        emoji_counter = Counter(all_emojis)
        self.patterns["style_patterns"]["emoji_frequency"] = {
            emoji: count for emoji, count in emoji_counter.most_common(10)
        }
        
        # Extrair frases comuns (n-gramas)
        common_phrases = self._extract_common_phrases(all_sentences)
        self.patterns["style_patterns"]["common_phrases"] = common_phrases
        
        logger.info(f"Analisado estilo de escrita: comprimento médio de frase = {self.patterns['style_patterns']['sentence_length']}")
    
    def _extract_common_phrases(self, sentences: List[str], min_count: int = 2) -> List[str]:
        """
        Extrai frases comuns (n-gramas) das sentenças.
        
        Args:
            sentences: Lista de sentenças
            min_count: Contagem mínima para considerar uma frase comum
            
        Returns:
            List[str]: Frases comuns
        """
        # Extrair bigramas e trigramas
        bigrams = []
        trigrams = []
        
        for sentence in sentences:
            words = sentence.lower().split()
            
            # Bigramas
            for i in range(len(words) - 1):
                bigrams.append(f"{words[i]} {words[i+1]}")
            
            # Trigramas
            for i in range(len(words) - 2):
                trigrams.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        
        # Contar frequência
        bigram_counter = Counter(bigrams)
        trigram_counter = Counter(trigrams)
        
        # Filtrar por contagem mínima
        common_bigrams = [b for b, c in bigram_counter.items() if c >= min_count]
        common_trigrams = [t for t, c in trigram_counter.items() if c >= min_count]
        
        # Combinar e limitar
        common_phrases = common_trigrams + common_bigrams
        return common_phrases[:20]
    
    def _analyze_engagement(self, reels_data: List[Dict[str, Any]]) -> None:
        """
        Analisa padrões de engajamento nos Reels.
        
        Args:
            reels_data: Lista de dados dos Reels
        """
        # Calcular engajamento médio
        likes = [reel.get("like_count", 0) for reel in reels_data]
        comments = [reel.get("comments_count", 0) for reel in reels_data]
        
        if likes:
            avg_likes = sum(likes) / len(likes)
        else:
            avg_likes = 0
        
        if comments:
            avg_comments = sum(comments) / len(comments)
        else:
            avg_comments = 0
        
        # Identificar Reels com maior engajamento
        engagement_scores = []
        
        for i, reel in enumerate(reels_data):
            score = (reel.get("like_count", 0) + reel.get("comments_count", 0) * 3)  # Comentários têm peso maior
            engagement_scores.append((i, score))
        
        # Ordenar por pontuação de engajamento
        engagement_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Extrair características dos Reels mais engajados
        top_reels_indices = [idx for idx, _ in engagement_scores[:5]]
        top_reels = [reels_data[idx] for idx in top_reels_indices]
        
        # Extrair hashtags dos Reels mais engajados
        top_hashtags = []
        for reel in top_reels:
            caption = reel.get("caption", "")
            hashtags = re.findall(r'#\w+', caption.lower())
            top_hashtags.extend(hashtags)
        
        # Contar frequência
        top_hashtag_counter = Counter(top_hashtags)
        
        # Salvar padrões de engajamento
        self.patterns["engagement_patterns"] = {
            "avg_likes": round(avg_likes, 1),
            "avg_comments": round(avg_comments, 1),
            "top_engagement_hashtags": [tag for tag, _ in top_hashtag_counter.most_common(5)]
        }
        
        logger.info(f"Analisados padrões de engajamento: média de likes = {round(avg_likes, 1)}, média de comentários = {round(avg_comments, 1)}")
    
    def save_patterns(self, filename: str = None) -> str:
        """
        Salva os padrões extraídos em um arquivo JSON.
        
        Args:
            filename: Nome do arquivo (opcional)
            
        Returns:
            str: Caminho para o arquivo salvo
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rapidinha_patterns_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Padrões salvos em: {filepath}")
        return filepath

def main():
    """
    Função principal para analisar os Reels da Rapidinha.
    """
    parser = argparse.ArgumentParser(description="Analisador de padrões para Reels da Rapidinha")
    parser.add_argument("--reels-data", required=True, help="Arquivo JSON com dados dos Reels")
    parser.add_argument("--output-dir", default="output/patterns", help="Diretório para salvar os padrões")
    parser.add_argument("--output-file", help="Nome do arquivo de saída (opcional)")
    
    args = parser.parse_args()
    
    try:
        # Carregar dados dos Reels
        with open(args.reels_data, 'r', encoding='utf-8') as f:
            reels_data = json.load(f)
        
        # Verificar se os dados estão no formato esperado
        if not isinstance(reels_data, list):
            logger.error("Formato de dados inválido. Deve ser uma lista de Reels.")
            return 1
        
        # Analisar padrões
        analyzer = RapidinhaPatternsAnalyzer(output_dir=args.output_dir)
        patterns = analyzer.analyze_reels_data(reels_data)
        
        # Salvar padrões
        filepath = analyzer.save_patterns(args.output_file)
        
        # Exibir resumo
        print("\n=== Padrões Extraídos dos Reels da Rapidinha ===")
        print(f"Total de Reels analisados: {len(reels_data)}")
        print(f"Hashtags mais comuns: {', '.join(patterns['hashtags'][:5])}")
        print(f"Tópicos principais: {', '.join(patterns['topics'][:5])}")
        print(f"Comprimento médio das frases: {patterns['style_patterns']['sentence_length']} palavras")
        print(f"Padrões salvos em: {filepath}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Erro ao analisar Reels: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
