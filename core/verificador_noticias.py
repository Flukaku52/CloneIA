#!/usr/bin/env python3
"""
Módulo para verificação e cruzamento de informações de notícias.
"""
import re
import logging
import difflib
from typing import List, Dict, Any, Tuple, Set
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('verificador_noticias')

class VerificadorNoticias:
    """
    Classe para verificar a credibilidade de notícias através de cruzamento de informações.
    """
    def __init__(self, limiar_similaridade: float = 0.7,
                 min_confirmacoes: int = 2,
                 bonus_confirmacao: int = 1):
        """
        Inicializa o verificador de notícias.

        Args:
            limiar_similaridade: Limiar de similaridade para considerar duas notícias como relacionadas (0.0 a 1.0)
            min_confirmacoes: Número mínimo de fontes para considerar uma notícia como confirmada
            bonus_confirmacao: Bônus de credibilidade para cada confirmação adicional
        """
        self.limiar_similaridade = limiar_similaridade
        self.min_confirmacoes = min_confirmacoes
        self.bonus_confirmacao = bonus_confirmacao

    def _normalizar_texto(self, texto: str) -> str:
        """
        Normaliza um texto para comparação, removendo caracteres especiais e padronizando.

        Args:
            texto: Texto a ser normalizado

        Returns:
            str: Texto normalizado
        """
        # Converter para minúsculas
        texto = texto.lower()

        # Remover caracteres especiais e pontuação
        texto = re.sub(r'[^\w\s]', '', texto)

        # Remover espaços extras
        texto = re.sub(r'\s+', ' ', texto).strip()

        # Remover palavras comuns que não agregam significado
        stop_words = {'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das',
                     'em', 'no', 'na', 'nos', 'nas', 'por', 'para', 'com', 'e', 'mas', 'ou', 'que'}

        palavras = texto.split()
        palavras_filtradas = [palavra for palavra in palavras if palavra not in stop_words]

        return ' '.join(palavras_filtradas)

    def _calcular_similaridade(self, texto1: str, texto2: str) -> float:
        """
        Calcula a similaridade entre dois textos.

        Args:
            texto1: Primeiro texto
            texto2: Segundo texto

        Returns:
            float: Valor de similaridade entre 0.0 e 1.0
        """
        # Normalizar os textos
        texto1_norm = self._normalizar_texto(texto1)
        texto2_norm = self._normalizar_texto(texto2)

        # Calcular similaridade usando difflib
        return difflib.SequenceMatcher(None, texto1_norm, texto2_norm).ratio()

    def _agrupar_noticias_similares(self, noticias: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Agrupa notícias similares com base no título e conteúdo.

        Args:
            noticias: Lista de notícias a serem agrupadas

        Returns:
            List[List[Dict[str, Any]]]: Lista de grupos de notícias similares
        """
        grupos = []
        noticias_processadas = set()

        # Pré-processar todos os títulos e resumos para comparação mais eficiente
        titulos_normalizados = [self._normalizar_texto(n['titulo']) for n in noticias]
        resumos_normalizados = [
            self._normalizar_texto(n.get('resumo', '')) if n.get('resumo') else ''
            for n in noticias
        ]

        # Matriz de similaridade para evitar recálculos
        similaridades = {}

        # Calcular similaridades entre todas as notícias
        for i in range(len(noticias)):
            for j in range(i+1, len(noticias)):
                # Calcular similaridade entre títulos
                similaridade_titulo = difflib.SequenceMatcher(
                    None, titulos_normalizados[i], titulos_normalizados[j]
                ).ratio()

                # Calcular similaridade entre resumos, se disponíveis
                similaridade_resumo = 0.0
                if resumos_normalizados[i] and resumos_normalizados[j]:
                    similaridade_resumo = difflib.SequenceMatcher(
                        None, resumos_normalizados[i], resumos_normalizados[j]
                    ).ratio()

                # Calcular similaridade combinada (média ponderada)
                similaridade = (similaridade_titulo * 0.7) + (similaridade_resumo * 0.3)

                # Armazenar na matriz de similaridade
                similaridades[(i, j)] = similaridade
                similaridades[(j, i)] = similaridade  # Simetria

        # Agrupar notícias com base nas similaridades calculadas
        for i, noticia1 in enumerate(noticias):
            if i in noticias_processadas:
                continue

            grupo_atual = [noticia1]
            noticias_processadas.add(i)

            # Encontrar notícias similares
            for j, noticia2 in enumerate(noticias):
                if j in noticias_processadas or i == j:
                    continue

                # Obter similaridade da matriz
                similaridade = similaridades.get((i, j), 0.0)

                # Verificar se a similaridade é suficiente para agrupar
                if similaridade >= self.limiar_similaridade:
                    grupo_atual.append(noticia2)
                    noticias_processadas.add(j)

            # Adicionar o grupo
            grupos.append(grupo_atual)

        # Ordenar grupos por tamanho (maiores primeiro)
        grupos.sort(key=len, reverse=True)

        # Log para depuração
        for i, grupo in enumerate(grupos):
            if len(grupo) > 1:
                logger.info(f"Grupo {i+1}: {len(grupo)} notícias similares")
                for noticia in grupo:
                    logger.info(f"  - {noticia['titulo']} ({noticia['portal']})")

        return grupos

    def _analisar_consistencia_grupo(self, grupo: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa a consistência entre notícias de um mesmo grupo.

        Args:
            grupo: Grupo de notícias similares

        Returns:
            Dict[str, Any]: Metadados sobre a consistência do grupo
        """
        # Inicializar metadados
        metadados = {
            'num_fontes': len(grupo),
            'fontes': [noticia['portal'] for noticia in grupo],
            'confirmado': len(grupo) >= self.min_confirmacoes,
            'contradições': [],
            'credibilidade_media': sum(noticia.get('credibilidade', 5) for noticia in grupo) / len(grupo),
            'data_mais_recente': None
        }

        # Encontrar a data mais recente
        datas = []
        for noticia in grupo:
            if noticia.get('data_iso'):
                try:
                    data = datetime.fromisoformat(noticia['data_iso'])
                    datas.append(data)
                except (ValueError, TypeError):
                    pass

        if datas:
            metadados['data_mais_recente'] = max(datas).isoformat()

        # Verificar contradições
        # Implementação simplificada: apenas verifica se há diferenças significativas nos resumos
        if len(grupo) > 1:
            for i, noticia1 in enumerate(grupo):
                for j, noticia2 in enumerate(grupo):
                    if i >= j:
                        continue

                    if noticia1.get('resumo') and noticia2.get('resumo'):
                        similaridade = self._calcular_similaridade(
                            noticia1['resumo'], noticia2['resumo']
                        )

                        # Se a similaridade for muito baixa, pode indicar contradição
                        if similaridade < 0.3:
                            metadados['contradições'].append({
                                'fonte1': noticia1['portal'],
                                'fonte2': noticia2['portal'],
                                'similaridade': similaridade
                            })

        return metadados

    def verificar_noticias(self, noticias: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Verifica a credibilidade de notícias através de cruzamento de informações.

        Args:
            noticias: Lista de notícias a serem verificadas

        Returns:
            List[Dict[str, Any]]: Lista de notícias com informações de credibilidade atualizadas
        """
        logger.info(f"Verificando {len(noticias)} notícias através de cruzamento de informações...")

        # Agrupar notícias similares
        grupos = self._agrupar_noticias_similares(noticias)

        logger.info(f"Notícias agrupadas em {len(grupos)} grupos")

        # Processar cada grupo
        noticias_verificadas = []

        for grupo in grupos:
            # Analisar consistência do grupo
            metadados = self._analisar_consistencia_grupo(grupo)

            # Atualizar cada notícia no grupo
            for noticia in grupo:
                # Copiar a notícia para não modificar a original
                noticia_atualizada = noticia.copy()

                # Adicionar metadados de cruzamento
                noticia_atualizada['cruzamento'] = {
                    'num_fontes': metadados['num_fontes'],
                    'fontes': metadados['fontes'],
                    'confirmado': metadados['confirmado'],
                    'tem_contradicoes': len(metadados['contradições']) > 0
                }

                # Atualizar credibilidade com base no cruzamento
                credibilidade_original = noticia.get('credibilidade', 5)

                # Adicionar bônus para cada confirmação adicional
                bonus = max(0, metadados['num_fontes'] - 1) * self.bonus_confirmacao

                # Penalizar se houver contradições
                penalidade = len(metadados['contradições']) * 2

                # Calcular nova credibilidade
                nova_credibilidade = credibilidade_original + bonus - penalidade

                # Limitar entre 0 e 10
                nova_credibilidade = max(0, min(10, nova_credibilidade))

                noticia_atualizada['credibilidade'] = nova_credibilidade
                noticia_atualizada['credibilidade_original'] = credibilidade_original
                noticia_atualizada['confiavel'] = nova_credibilidade >= 6

                # Adicionar razões para a mudança na credibilidade
                razoes = noticia.get('razoes_credibilidade', []).copy()

                if bonus > 0:
                    razoes.append(f"Confirmada por {metadados['num_fontes']} fontes (+{bonus})")

                if penalidade > 0:
                    razoes.append(f"Contradições entre fontes (-{penalidade})")

                noticia_atualizada['razoes_credibilidade'] = razoes

                # Adicionar à lista de notícias verificadas
                noticias_verificadas.append(noticia_atualizada)

        # Ordenar por credibilidade (mais confiáveis primeiro)
        noticias_verificadas.sort(key=lambda x: x['credibilidade'], reverse=True)

        return noticias_verificadas
