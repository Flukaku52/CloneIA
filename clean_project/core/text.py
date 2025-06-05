#!/usr/bin/env python3
"""
Text processing module for the CloneIA project.
"""
import os
import re
import logging
from typing import Dict, List, Optional, Tuple, Any

from core.utils import optimize_text

logger = logging.getLogger('cloneia.text')

class TextProcessor:
    """
    Class for processing and optimizing text for speech synthesis.
    """

    def __init__(self):
        """
        Initialize the text processor.
        """
        # Common crypto terms and their pronunciations
        self.crypto_terms = {
            "Bitcoin": "Bitcoim",
            "Ethereum": "Etherium",
            "Cardano": "Cardâno",
            "Solana": "Solâna",
            "Polkadot": "Polcadot",
            "Binance": "Bináns",
            "Coinbase": "Cóinbeis",
            "NFT": "ÊnÊfeTê",
            "DeFi": "DêFai",
            "staking": "stêiking",
            "blockchain": "blókcheim",
            "wallet": "wólet",
            "token": "tôken",
            "altcoin": "ôltcoin",
            "mining": "máining",
            "miner": "máiner"
        }

        # Words to emphasize
        self.emphasis_words = [
            "bombando", "muito", "super", "mega", "alta", "subindo",
            "disparou", "explodiu", "recorde", "máxima", "forte",
            "incrível", "enorme", "gigante", "absurdo", "impressionante",
            "surpreendente", "extraordinário", "fenomenal", "espetacular"
        ]

        # Greeting patterns
        self.greeting_patterns = [
            (r"e\s+aí\s+cambada", "EAÍCAMBADA"),
            (r"fala\s+cambada", "FALACAMBADA"),
            (r"e\s+aí\s+galera", "EAÍGALERA"),
            (r"fala\s+galera", "FALAGALERA")
        ]

        logger.info("TextProcessor initialized")

    def optimize_for_speech(self, text: str) -> str:
        """
        Optimize text for speech synthesis.

        Args:
            text: Original text

        Returns:
            str: Optimized text
        """
        if not text:
            return text

        # Make a copy of the original text
        optimized = text

        # Replace greetings with more fluid versions
        for pattern, replacement in self.greeting_patterns:
            optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)

        # Selectively replace punctuation to maintain some natural flow
        # Keep some punctuation for rhythm but remove those that cause awkward pauses
        optimized = re.sub(r'[!?]', '', optimized)  # Remove exclamation and question marks completely
        optimized = re.sub(r'\.{3,}', '', optimized)  # Remove ellipses
        optimized = re.sub(r'[;:]', ' ', optimized)  # Replace semicolons and colons with spaces

        # Replace commas and periods with spaces only when they would cause unnatural pauses
        optimized = re.sub(r',\s+', ' ', optimized)  # Replace ", " with space
        optimized = re.sub(r'\.\s+', ' ', optimized)  # Replace ". " with space

        # Keep commas and periods that are part of numbers
        optimized = re.sub(r'(\d),(\d)', r'\1\2', optimized)  # Remove commas in numbers

        # Add subtle pauses with hyphens at natural break points
        optimized = re.sub(r'\s+mas\s+', ' mas- ', optimized, flags=re.IGNORECASE)
        optimized = re.sub(r'\s+e\s+', ' e- ', optimized, flags=re.IGNORECASE)
        optimized = re.sub(r'\s+então\s+', ' então- ', optimized, flags=re.IGNORECASE)
        optimized = re.sub(r'\s+porém\s+', ' porém- ', optimized, flags=re.IGNORECASE)

        # Replace crypto terms for better pronunciation
        for term, pronunciation in self.crypto_terms.items():
            # Use word boundaries to avoid replacing parts of words
            optimized = re.sub(r'\b' + re.escape(term) + r'\b', pronunciation, optimized)

        # Emphasize certain words
        for word in self.emphasis_words:
            # Use word boundaries to avoid replacing parts of words
            pattern = r'\b' + re.escape(word) + r'\b'
            replacement = word.upper()
            optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)

        logger.debug(f"Optimized text: {optimized[:50]}...")
        return optimized

    def parse_script(self, script_content: str) -> Dict[str, Any]:
        """
        Parse a script into sections (intro, news items, outro).

        Args:
            script_content: Content of the script

        Returns:
            Dict[str, Any]: Parsed script with sections
        """
        lines = script_content.strip().split('\n')
        intro_lines = []
        news_items = []
        outro_lines = []

        current_section = 'intro'
        current_news = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if it's a numbered news line
            if re.match(r'^\d+\.\s+', line):
                current_section = 'news'
                if current_news:
                    news_items.append(current_news)
                current_news = {'title': line, 'content': []}
            elif current_section == 'news' and current_news:
                if len(news_items) >= 2 and not current_news['content']:
                    # Probably in the conclusion
                    current_section = 'outro'
                    outro_lines.append(line)
                else:
                    current_news['content'].append(line)
            elif current_section == 'intro':
                intro_lines.append(line)
            else:
                outro_lines.append(line)

        # Add the last news item
        if current_news and current_news['content']:
            news_items.append(current_news)

        # Optimize each section
        intro = '\n'.join(intro_lines)
        optimized_intro = self.optimize_for_speech(intro)

        optimized_news = []
        for news in news_items:
            title = news['title']
            content = '\n'.join(news['content'])
            optimized_news.append({
                'title': self.optimize_for_speech(title),
                'content': self.optimize_for_speech(content)
            })

        outro = '\n'.join(outro_lines)
        optimized_outro = self.optimize_for_speech(outro)

        return {
            'intro': optimized_intro,
            'news': optimized_news,
            'outro': optimized_outro,
            'original': {
                'intro': intro,
                'news': news_items,
                'outro': outro
            }
        }

    def generate_script(self, topic: str, num_items: int = 3) -> str:
        """
        Generate a simple script template.

        Args:
            topic: Main topic for the script
            num_items: Number of news items

        Returns:
            str: Generated script template
        """
        script = f"E aí cambada! Tô de volta com mais uma Rapidinha Cripto!\n\n"
        script += f"Hoje vamos falar sobre {topic}.\n\n"

        for i in range(1, num_items + 1):
            script += f"{i}. Notícia {i} sobre {topic}\n"
            script += f"   Detalhes da notícia {i}...\n\n"

        script += f"É isso cambada! Se gostou, deixa o like e compartilha com a galera. Até a próxima Rapidinha Cripto!"

        return script

    def split_long_text(self, text: str, max_length: int = 1000) -> List[str]:
        """
        Split long text into smaller chunks for processing.

        Args:
            text: Long text to split
            max_length: Maximum length of each chunk

        Returns:
            List[str]: List of text chunks
        """
        if len(text) <= max_length:
            return [text]

        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


# For backward compatibility
def optimize_text_legacy(text: str) -> str:
    """
    Legacy function for text optimization (for backward compatibility).

    Args:
        text: Original text

    Returns:
        str: Optimized text
    """
    return optimize_text(text)
