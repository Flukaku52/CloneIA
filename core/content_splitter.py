#!/usr/bin/env python3
"""
Módulo para dividir o conteúdo em seções para os vídeos Rapidinha.
"""
import re
import logging
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('content_splitter')

# Marcador de corte para separar notícias
MARCADOR_CORTE = "[CORTE]"

class ContentSplitter:
    """
    Classe para dividir o conteúdo em seções para os vídeos Rapidinha.
    """
    def __init__(self):
        """
        Inicializa o divisor de conteúdo.
        """
        logger.info("Divisor de conteúdo inicializado.")

    def remover_fontes_datas(self, texto: str) -> str:
        """
        Remove fontes e datas do texto.

        Args:
            texto: Texto a ser processado

        Returns:
            str: Texto sem fontes e datas
        """
        # Remover padrões como (Fonte: Nome, DD/MM/AAAA)
        texto = re.sub(r'\(Fonte:.*?\)', '', texto)

        # Remover datas no formato DD/MM/AAAA
        texto = re.sub(r'\d{1,2}/\d{1,2}/\d{2,4}', '', texto)

        # Remover espaços extras
        texto = re.sub(r'\s+', ' ', texto)
        texto = re.sub(r'\s+\.', '.', texto)

        return texto.strip()

    def dividir_em_secoes(self, conteudo: str) -> List[str]:
        """
        Divide o conteúdo em seções baseadas em padrões de títulos de notícias.

        Args:
            conteudo: Conteúdo completo do script

        Returns:
            List[str]: Lista de seções
        """
        # Remover fontes e datas
        conteudo = self.remover_fontes_datas(conteudo)

        # Dividir o conteúdo em parágrafos
        paragrafos = [p.strip() for p in conteudo.split('\n\n') if p.strip()]

        # Identificar parágrafos que são títulos de notícias
        titulos_indices = []

        for i, paragrafo in enumerate(paragrafos):
            if re.search(r'Notícia \d+:', paragrafo, re.IGNORECASE) or \
               re.search(r'E para finalizar:', paragrafo, re.IGNORECASE):
                titulos_indices.append(i)

        # Se não encontrou nenhum título, tentar identificar a primeira notícia
        if not titulos_indices and len(paragrafos) > 1:
            # Assumir que o primeiro parágrafo é a introdução e o segundo é o título da primeira notícia
            titulos_indices = [1]

        # Se ainda não encontrou nenhum título, retornar o conteúdo completo como uma única seção
        if not titulos_indices:
            return [conteudo]

        # Dividir o conteúdo em seções
        secoes = []

        # Adicionar a introdução (tudo antes do primeiro título)
        introducao = '\n\n'.join(paragrafos[:titulos_indices[0]])
        secoes.append(introducao)

        # Adicionar as notícias
        for i in range(len(titulos_indices)):
            inicio = titulos_indices[i]

            # Determinar o fim da seção atual
            if i < len(titulos_indices) - 1:
                fim = titulos_indices[i + 1]
            else:
                fim = len(paragrafos)

            # Juntar os parágrafos da seção atual
            secao = '\n\n'.join(paragrafos[inicio:fim])
            secoes.append(secao)

        return secoes

    def formatar_com_cortes(self, secoes: List[str]) -> str:
        """
        Formata as seções com marcadores de corte.

        Args:
            secoes: Lista de seções

        Returns:
            str: Texto formatado com marcadores de corte
        """
        return f"\n\n{MARCADOR_CORTE}\n\n".join(secoes)

    def processar_script(self, script: str) -> Dict[str, Any]:
        """
        Processa o script completo, dividindo-o em seções e adicionando marcadores de corte.

        Args:
            script: Script completo

        Returns:
            Dict[str, Any]: Dicionário com o script processado e informações adicionais
        """
        # Dividir o script em seções
        secoes = self.dividir_em_secoes(script)

        # Formatar com marcadores de corte
        script_formatado = self.formatar_com_cortes(secoes)

        return {
            "script_original": script,
            "script_formatado": script_formatado,
            "num_secoes": len(secoes),
            "num_cortes": len(secoes) - 1,
            "secoes": secoes
        }
