#!/usr/bin/env python3
"""
Módulo para verificação e cruzamento de informações de notícias.
Implementa algoritmos para agrupar notícias similares e verificar sua credibilidade.
"""
import re
import logging
from functools import lru_cache
import difflib
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

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

    # Lista de stop words (palavras comuns que não agregam significado)
    STOP_WORDS = {
        'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das',
        'em', 'no', 'na', 'nos', 'nas', 'por', 'para', 'com', 'e', 'mas', 'ou', 'que',
        'se', 'ao', 'aos', 'à', 'às', 'pelo', 'pela', 'pelos', 'pelas', 'este', 'esta',
        'estes', 'estas', 'esse', 'essa', 'esses', 'essas', 'isso', 'aquilo', 'como',
        'quando', 'onde', 'quem', 'qual', 'quais', 'já', 'só', 'sem', 'sobre', 'até',
        'depois', 'antes', 'agora', 'então', 'ainda', 'mesmo', 'também', 'não', 'sim',
        'ter', 'ser', 'estar', 'fazer', 'ir', 'vir', 'pode', 'foi', 'são', 'está'
    }

    # Lista de criptomoedas comuns para detecção
    CRIPTOMOEDAS = {
        'bitcoin': ['btc', 'bitcoin', 'satoshi', 'nakamoto'],
        'ethereum': ['eth', 'ethereum', 'vitalik', 'buterin', 'ether'],
        'cardano': ['ada', 'cardano', 'hoskinson'],
        'ripple': ['xrp', 'ripple'],
        'solana': ['sol', 'solana'],
        'binance': ['bnb', 'binance', 'cz'],
        'polkadot': ['dot', 'polkadot', 'gavin'],
        'dogecoin': ['doge', 'dogecoin'],
        'shiba': ['shib', 'shiba'],
        'tether': ['usdt', 'tether'],
        'usd coin': ['usdc']
    }

    @lru_cache(maxsize=1000)
    def _normalizar_texto(self, texto: str) -> str:
        """
        Normaliza um texto para comparação, removendo caracteres especiais e padronizando.
        Usa cache para melhorar performance em textos repetidos.

        Args:
            texto: Texto a ser normalizado

        Returns:
            str: Texto normalizado
        """
        if not texto:
            return ""

        # Converter para minúsculas
        texto = texto.lower()

        # Remover caracteres especiais e pontuação
        texto = re.sub(r'[^\w\s]', '', texto)

        # Remover espaços extras
        texto = re.sub(r'\s+', ' ', texto).strip()

        # Remover stop words
        palavras = texto.split()
        palavras_filtradas = [palavra for palavra in palavras if palavra not in self.STOP_WORDS]

        return ' '.join(palavras_filtradas)

    def _extrair_palavras_chave(self, texto: str) -> Set[str]:
        """
        Extrai palavras-chave de um texto, incluindo detecção de criptomoedas.

        Args:
            texto: Texto para extrair palavras-chave

        Returns:
            Set[str]: Conjunto de palavras-chave
        """
        if not texto:
            return set()

        # Normalizar o texto
        texto_norm = self._normalizar_texto(texto)
        texto_lower = texto.lower()  # Versão original em minúsculas para detecção de criptomoedas

        # Dividir em palavras e filtrar palavras curtas
        palavras = {p for p in texto_norm.split() if len(p) > 3}

        # Detectar menções a criptomoedas
        for cripto, termos in self.CRIPTOMOEDAS.items():
            if any(termo in texto_lower for termo in termos):
                palavras.add(cripto)

        return palavras

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
        Agrupa notícias similares com base no título, conteúdo e palavras-chave.
        Utiliza algoritmo otimizado para identificar grupos de notícias relacionadas.

        Args:
            noticias: Lista de notícias a serem agrupadas

        Returns:
            List[List[Dict[str, Any]]]: Lista de grupos de notícias similares
        """
        if not noticias:
            return []

        # Estruturas para armazenar resultados
        grupos = []
        noticias_processadas = set()

        # Pré-processar todos os títulos e resumos para comparação mais eficiente
        titulos_normalizados = []
        resumos_normalizados = []
        palavras_chave = []

        # Pré-processamento em lote para melhor performance
        for noticia in noticias:
            # Processar título
            titulo_norm = self._normalizar_texto(noticia['titulo'])
            titulos_normalizados.append(titulo_norm)

            # Processar resumo
            resumo = noticia.get('resumo', '')
            resumo_norm = self._normalizar_texto(resumo) if resumo else ''
            resumos_normalizados.append(resumo_norm)

            # Extrair palavras-chave do texto completo
            texto_completo = f"{noticia['titulo']} {resumo}"
            palavras = self._extrair_palavras_chave(texto_completo)
            palavras_chave.append(palavras)

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

                # Calcular similaridade de palavras-chave (coeficiente de Jaccard)
                palavras_i = palavras_chave[i]
                palavras_j = palavras_chave[j]

                # Calcular coeficiente de Jaccard para palavras-chave
                uniao = len(palavras_i.union(palavras_j))
                intersecao = len(palavras_i.intersection(palavras_j))
                similaridade_palavras = intersecao / uniao if uniao > 0 else 0.0

                # Calcular similaridade combinada (média ponderada)
                similaridade = (similaridade_titulo * 0.4) + (similaridade_resumo * 0.3) + (similaridade_palavras * 0.3)

                # Armazenar na matriz de similaridade
                similaridades[(i, j)] = similaridade
                similaridades[(j, i)] = similaridade  # Simetria

                # Log para depuração de alta similaridade
                if similaridade >= self.limiar_similaridade and logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Alta similaridade ({similaridade:.2f}) entre:")
                    logger.debug(f"  - {noticias[i]['titulo']} ({noticias[i]['portal']})")
                    logger.debug(f"  - {noticias[j]['titulo']} ({noticias[j]['portal']})")
                    logger.debug(f"  - Similaridade título: {similaridade_titulo:.2f}")
                    logger.debug(f"  - Similaridade resumo: {similaridade_resumo:.2f}")
                    logger.debug(f"  - Similaridade palavras: {similaridade_palavras:.2f}")
                    logger.debug(f"  - Palavras em comum: {palavras_i.intersection(palavras_j)}")

        # Algoritmo de agrupamento baseado em similaridade
        for i, noticia in enumerate(noticias):
            if i in noticias_processadas:
                continue

            # Iniciar novo grupo
            grupo_atual = [noticia]
            noticias_processadas.add(i)

            # Encontrar todas as notícias similares
            candidatos = [(j, similaridades.get((i, j), 0.0))
                         for j in range(len(noticias))
                         if j != i and j not in noticias_processadas]

            # Ordenar candidatos por similaridade (mais similares primeiro)
            candidatos.sort(key=lambda x: x[1], reverse=True)

            # Adicionar notícias similares ao grupo
            for j, similaridade in candidatos:
                if similaridade >= self.limiar_similaridade:
                    grupo_atual.append(noticias[j])
                    noticias_processadas.add(j)

            # Adicionar o grupo se tiver pelo menos uma notícia
            if grupo_atual:
                grupos.append(grupo_atual)

        # Ordenar grupos por tamanho (maiores primeiro)
        grupos.sort(key=len, reverse=True)

        # Log para depuração
        for i, grupo in enumerate(grupos):
            if len(grupo) > 1:
                logger.info(f"Grupo {i+1}: {len(grupo)} notícias similares")
                for noticia in grupo:
                    logger.info(f"  - {noticia['titulo']} ({noticia['portal']})")

                # Mostrar palavras-chave em comum
                indices = [noticias.index(n) for n in grupo]
                palavras_comuns = set.intersection(*[palavras_chave[idx] for idx in indices])
                logger.info(f"  - Palavras-chave em comum: {palavras_comuns}")

        return grupos

    def _analisar_consistencia_grupo(self, grupo: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa a consistência entre notícias de um mesmo grupo.
        Identifica contradições e calcula métricas de confiabilidade.

        Args:
            grupo: Grupo de notícias similares

        Returns:
            Dict[str, Any]: Metadados sobre a consistência do grupo
        """
        if not grupo:
            return {
                'num_fontes': 0,
                'fontes': [],
                'confirmado': False,
                'contradições': [],
                'credibilidade_media': 0,
                'data_mais_recente': None
            }

        # Extrair informações básicas
        fontes = [noticia['portal'] for noticia in grupo]

        # Inicializar metadados
        metadados = {
            'num_fontes': len(grupo),
            'fontes': fontes,
            'confirmado': len(grupo) >= self.min_confirmacoes,
            'contradições': [],
            'credibilidade_media': sum(noticia.get('credibilidade', 5) for noticia in grupo) / len(grupo),
            'data_mais_recente': None,
            'fontes_unicas': len(set(fontes))  # Número de fontes únicas
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

        # Verificar contradições entre notícias do grupo
        if len(grupo) > 1:
            # Matriz para evitar comparações duplicadas
            comparacoes_feitas = set()

            for i, noticia1 in enumerate(grupo):
                for j, noticia2 in enumerate(grupo):
                    # Evitar comparações duplicadas ou com a mesma notícia
                    if i >= j or (i, j) in comparacoes_feitas:
                        continue

                    comparacoes_feitas.add((i, j))

                    # Verificar contradições nos resumos
                    if noticia1.get('resumo') and noticia2.get('resumo'):
                        similaridade = self._calcular_similaridade(
                            noticia1['resumo'], noticia2['resumo']
                        )

                        # Se a similaridade for muito baixa, pode indicar contradição
                        if similaridade < 0.3:
                            metadados['contradições'].append({
                                'fonte1': noticia1['portal'],
                                'fonte2': noticia2['portal'],
                                'similaridade': similaridade,
                                'resumo1': noticia1['resumo'][:100] + '...' if len(noticia1['resumo']) > 100 else noticia1['resumo'],
                                'resumo2': noticia2['resumo'][:100] + '...' if len(noticia2['resumo']) > 100 else noticia2['resumo']
                            })

        return metadados

    def verificar_noticias(self, noticias: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Verifica a credibilidade de notícias através de cruzamento de informações.
        Agrupa notícias similares, analisa consistência e atualiza pontuações de credibilidade.

        Args:
            noticias: Lista de notícias a serem verificadas

        Returns:
            List[Dict[str, Any]]: Lista de notícias com informações de credibilidade atualizadas
        """
        if not noticias:
            return []

        logger.info(f"Verificando {len(noticias)} notícias através de cruzamento de informações...")

        # Agrupar notícias similares
        grupos = self._agrupar_noticias_similares(noticias)

        logger.info(f"Notícias agrupadas em {len(grupos)} grupos")

        # Processar cada grupo e atualizar notícias
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
                    'fontes_unicas': metadados.get('fontes_unicas', len(set(metadados['fontes']))),
                    'confirmado': metadados['confirmado'],
                    'tem_contradicoes': len(metadados['contradições']) > 0
                }

                # Atualizar credibilidade com base no cruzamento
                credibilidade_original = noticia.get('credibilidade', 5)

                # Adicionar bônus para cada confirmação adicional (fonte única)
                fontes_unicas = metadados.get('fontes_unicas', len(set(metadados['fontes'])))
                bonus = max(0, fontes_unicas - 1) * self.bonus_confirmacao

                # Penalizar se houver contradições
                penalidade = len(metadados['contradições']) * 2

                # Calcular nova credibilidade
                nova_credibilidade = credibilidade_original + bonus - penalidade

                # Limitar entre 0 e 10
                nova_credibilidade = max(0, min(10, nova_credibilidade))

                # Atualizar campos de credibilidade
                noticia_atualizada['credibilidade'] = nova_credibilidade
                noticia_atualizada['credibilidade_original'] = credibilidade_original
                noticia_atualizada['confiavel'] = nova_credibilidade >= 6

                # Adicionar razões para a mudança na credibilidade
                razoes = noticia.get('razoes_credibilidade', []).copy()

                if bonus > 0:
                    razoes.append(f"Confirmada por {fontes_unicas} fontes diferentes (+{bonus})")

                if penalidade > 0:
                    razoes.append(f"Contradições entre fontes (-{penalidade})")

                noticia_atualizada['razoes_credibilidade'] = razoes

                # Adicionar à lista de notícias verificadas
                noticias_verificadas.append(noticia_atualizada)

        # Ordenar por credibilidade (mais confiáveis primeiro) e depois por data (mais recentes primeiro)
        noticias_verificadas.sort(
            key=lambda x: (x.get('credibilidade', 0), x.get('data_iso', '')),
            reverse=True
        )

        logger.info(f"Verificação concluída: {len(noticias_verificadas)} notícias processadas")

        return noticias_verificadas
