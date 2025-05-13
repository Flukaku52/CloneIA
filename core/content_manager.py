#!/usr/bin/env python3
"""
Gerenciador de parâmetros de conteúdo para os vídeos Rapidinha.
"""
import os
import json
import random
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('content_manager')

class ContentManager:
    """
    Classe para gerenciar parâmetros de conteúdo para os vídeos Rapidinha.
    """
    def __init__(self, config_path: str = "config/content_params.json"):
        """
        Inicializa o gerenciador de conteúdo.
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        self.config_path = config_path
        self.params = self._load_params()
        
        # Parâmetros específicos para Rapidinha
        self.rapidinha_params = self.params.get("rapidinha", {})
        self.saudacao_inicial = self.rapidinha_params.get("saudacao_inicial", "Cambada")
        self.duracao_maxima = self.rapidinha_params.get("duracao_maxima_segundos", 180)
        self.palavras_por_minuto = self.rapidinha_params.get("palavras_por_minuto", 150)
        self.limite_palavras = self.rapidinha_params.get("limite_palavras", 450)
        
        logger.info(f"Gerenciador de conteúdo inicializado. Saudação: '{self.saudacao_inicial}', "
                   f"Duração máxima: {self.duracao_maxima} segundos")
    
    def _load_params(self) -> Dict[str, Any]:
        """
        Carrega os parâmetros de conteúdo do arquivo de configuração.
        
        Returns:
            Dict[str, Any]: Parâmetros de conteúdo
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Arquivo de configuração não encontrado: {self.config_path}")
                return self._get_default_params()
        except Exception as e:
            logger.error(f"Erro ao carregar parâmetros de conteúdo: {e}")
            return self._get_default_params()
    
    def _get_default_params(self) -> Dict[str, Any]:
        """
        Retorna parâmetros padrão caso o arquivo de configuração não seja encontrado.
        
        Returns:
            Dict[str, Any]: Parâmetros padrão
        """
        return {
            "rapidinha": {
                "saudacao_inicial": "Cambada",
                "duracao_maxima_segundos": 180,
                "palavras_por_minuto": 150,
                "limite_palavras": 450
            }
        }
    
    def get_random_intro_phrase(self, assunto: str) -> str:
        """
        Retorna uma frase introdutória aleatória.
        
        Args:
            assunto: Assunto principal do vídeo
            
        Returns:
            str: Frase introdutória
        """
        frases = self.rapidinha_params.get("frases_introdutorias", [
            "hoje vamos falar sobre {{assunto}}!",
            "tudo bem com vocês? Hoje o assunto é {{assunto}}!"
        ])
        
        if not frases:
            return f"hoje vamos falar sobre {assunto}!"
        
        frase = random.choice(frases)
        return frase.replace("{{assunto}}", assunto)
    
    def get_random_transition(self) -> str:
        """
        Retorna uma frase de transição aleatória.
        
        Returns:
            str: Frase de transição
        """
        transicoes = self.rapidinha_params.get("transicoes", [
            "Mas o que isso significa?",
            "Vamos entender melhor:"
        ])
        
        if not transicoes:
            return "Vamos entender melhor:"
        
        return random.choice(transicoes)
    
    def get_random_emphasis(self) -> str:
        """
        Retorna uma expressão de ênfase aleatória.
        
        Returns:
            str: Expressão de ênfase
        """
        enfases = self.rapidinha_params.get("expressoes_enfase", [
            "Isso mesmo!",
            "Acreditem!"
        ])
        
        if not enfases:
            return "Isso mesmo!"
        
        return random.choice(enfases)
    
    def get_intro_template(self, assunto: str) -> str:
        """
        Retorna o template de introdução preenchido.
        
        Args:
            assunto: Assunto principal do vídeo
            
        Returns:
            str: Template de introdução preenchido
        """
        formato = self.rapidinha_params.get("formato", {})
        intro = formato.get("introducao", {})
        template = intro.get("template", "{{saudacao_inicial}}, {{frase_introdutoria}}")
        
        frase_introdutoria = self.get_random_intro_phrase(assunto)
        
        return template.replace("{{saudacao_inicial}}", self.saudacao_inicial) \
                      .replace("{{frase_introdutoria}}", frase_introdutoria)
    
    def get_conclusion_template(self) -> str:
        """
        Retorna o template de conclusão preenchido.
        
        Returns:
            str: Template de conclusão preenchido
        """
        formato = self.rapidinha_params.get("formato", {})
        conclusao = formato.get("conclusao", {})
        template = conclusao.get("template", 
                               "E aí, {{saudacao_inicial}}? O que vocês acharam? Deixem nos comentários. Até a próxima!")
        
        return template.replace("{{saudacao_inicial}}", self.saudacao_inicial)
    
    def get_legal_disclaimer(self) -> str:
        """
        Retorna o aviso legal para o vídeo.
        
        Returns:
            str: Aviso legal
        """
        avisos = self.rapidinha_params.get("avisos_legais", {})
        if avisos.get("obrigatorio", True):
            return avisos.get("texto", 
                            "Lembre-se: isso não é recomendação de investimento. Faça sua própria pesquisa.")
        return ""
    
    def check_forbidden_words(self, texto: str) -> List[str]:
        """
        Verifica se o texto contém palavras proibidas.
        
        Args:
            texto: Texto a ser verificado
            
        Returns:
            List[str]: Lista de palavras proibidas encontradas
        """
        palavras_proibidas = self.rapidinha_params.get("palavras_proibidas", [])
        if not palavras_proibidas:
            return []
        
        texto_lower = texto.lower()
        encontradas = []
        
        for palavra in palavras_proibidas:
            # Verificar palavra completa (com limites de palavra)
            padrao = r'\b' + re.escape(palavra.lower()) + r'\b'
            if re.search(padrao, texto_lower):
                encontradas.append(palavra)
        
        return encontradas
    
    def validate_script_length(self, script: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Valida se o script está dentro do limite de duração.
        
        Args:
            script: Texto do script
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (válido, informações)
        """
        # Contar palavras (excluindo pontuação)
        palavras = re.findall(r'\b\w+\b', script)
        num_palavras = len(palavras)
        
        # Calcular duração estimada
        duracao_estimada = (num_palavras / self.palavras_por_minuto) * 60
        
        # Verificar se está dentro do limite
        valido = duracao_estimada <= self.duracao_maxima
        
        info = {
            "num_palavras": num_palavras,
            "limite_palavras": self.limite_palavras,
            "duracao_estimada_segundos": duracao_estimada,
            "duracao_maxima_segundos": self.duracao_maxima,
            "dentro_limite": valido
        }
        
        return valido, info
    
    def format_script(self, titulo: str, conteudo: str) -> str:
        """
        Formata o script completo para o vídeo Rapidinha.
        
        Args:
            titulo: Título do vídeo
            conteudo: Conteúdo principal do vídeo
            
        Returns:
            str: Script formatado
        """
        # Extrair assunto principal do título
        assunto = titulo.split(':')[-1].strip() if ':' in titulo else titulo
        
        # Criar introdução
        introducao = self.get_intro_template(assunto)
        
        # Criar conclusão
        conclusao = self.get_conclusion_template()
        
        # Adicionar aviso legal
        aviso_legal = self.get_legal_disclaimer()
        if aviso_legal:
            conclusao = f"{conclusao}\n\n{aviso_legal}"
        
        # Montar script completo
        script = f"{introducao}\n\n{conteudo}\n\n{conclusao}"
        
        # Verificar comprimento
        valido, info = self.validate_script_length(script)
        if not valido:
            logger.warning(f"Script excede o limite de duração: {info['duracao_estimada_segundos']:.1f}s "
                          f"(máximo: {info['duracao_maxima_segundos']}s)")
        
        # Verificar palavras proibidas
        palavras_proibidas = self.check_forbidden_words(script)
        if palavras_proibidas:
            logger.warning(f"Script contém palavras proibidas: {', '.join(palavras_proibidas)}")
        
        return script
