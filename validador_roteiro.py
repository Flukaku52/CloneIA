#!/usr/bin/env python3
"""
Validador de roteiros para evitar gastos desnecessários de créditos nas APIs.
Este script verifica se um roteiro está adequado para geração de áudio e vídeo
antes de enviá-lo para as APIs do ElevenLabs ou HeyGen.
"""
import os
import re
import sys
import argparse
import logging
from typing import Dict, List, Tuple, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('validador_roteiro')

# Constantes
MAX_CHARS_ELEVENLABS = 5000  # Limite de caracteres para o ElevenLabs
MAX_CHARS_HEYGEN = 1000      # Limite de caracteres para o HeyGen
CUSTO_POR_CHAR_ELEVENLABS = 0.000003  # Custo aproximado por caractere no ElevenLabs
CUSTO_POR_SEGUNDO_HEYGEN = 0.05       # Custo aproximado por segundo no HeyGen
CHARS_POR_SEGUNDO = 15                # Estimativa de caracteres por segundo de fala

class ValidadorRoteiro:
    """
    Classe para validar roteiros antes de enviá-los para as APIs.
    """
    def __init__(self):
        # Palavras ou frases que podem causar problemas
        self.palavras_problematicas = [
            "<", ">", "&lt;", "&gt;", # Tags HTML que podem interferir
            "prosody", "break", "speak", "voice", "audio", # Tags SSML
            "http://", "https://", "www.", # URLs que podem não ser lidas corretamente
            "\\n", "\\t", "\\r", # Caracteres de escape
        ]
        
        # Padrões de formatação que podem causar problemas
        self.padroes_problematicos = [
            r"<[^>]+>",  # Tags HTML/XML
            r"\{\{[^}]+\}\}",  # Variáveis de template
            r"\$\{[^}]+\}",  # Variáveis de template
        ]
    
    def validar_texto(self, texto: str) -> Tuple[bool, List[str]]:
        """
        Valida um texto para geração de áudio/vídeo.
        
        Args:
            texto: O texto a ser validado
            
        Returns:
            Tuple[bool, List[str]]: (texto_valido, lista_de_problemas)
        """
        problemas = []
        
        # Verificar se o texto está vazio
        if not texto or texto.strip() == "":
            problemas.append("O texto está vazio")
            return False, problemas
        
        # Verificar o comprimento do texto
        if len(texto) > MAX_CHARS_ELEVENLABS:
            problemas.append(f"O texto excede o limite de {MAX_CHARS_ELEVENLABS} caracteres para o ElevenLabs")
        
        if len(texto) > MAX_CHARS_HEYGEN:
            problemas.append(f"O texto excede o limite de {MAX_CHARS_HEYGEN} caracteres para o HeyGen")
        
        # Verificar palavras problemáticas
        for palavra in self.palavras_problematicas:
            if palavra in texto:
                problemas.append(f"O texto contém a palavra/frase problemática: '{palavra}'")
        
        # Verificar padrões problemáticos
        for padrao in self.padroes_problematicos:
            if re.search(padrao, texto):
                problemas.append(f"O texto contém o padrão problemático: '{padrao}'")
        
        # Verificar caracteres especiais em excesso
        caracteres_especiais = re.findall(r'[^\w\s,.!?;:"\'-]', texto)
        if len(caracteres_especiais) > 10:
            problemas.append(f"O texto contém muitos caracteres especiais: {caracteres_especiais[:10]}...")
        
        # Verificar linhas muito longas
        linhas = texto.split('\n')
        for i, linha in enumerate(linhas):
            if len(linha) > 200:
                problemas.append(f"A linha {i+1} é muito longa ({len(linha)} caracteres)")
        
        return len(problemas) == 0, problemas
    
    def estimar_custos(self, texto: str) -> Dict[str, float]:
        """
        Estima os custos de geração de áudio e vídeo.
        
        Args:
            texto: O texto para estimar os custos
            
        Returns:
            Dict[str, float]: Dicionário com os custos estimados
        """
        # Remover espaços extras e quebras de linha para contagem de caracteres
        texto_limpo = ' '.join(texto.split())
        num_caracteres = len(texto_limpo)
        
        # Estimar duração em segundos
        duracao_estimada = num_caracteres / CHARS_POR_SEGUNDO
        
        # Calcular custos
        custo_elevenlabs = num_caracteres * CUSTO_POR_CHAR_ELEVENLABS
        custo_heygen = duracao_estimada * CUSTO_POR_SEGUNDO_HEYGEN
        
        return {
            "caracteres": num_caracteres,
            "duracao_segundos": duracao_estimada,
            "custo_elevenlabs": custo_elevenlabs,
            "custo_heygen": custo_heygen,
            "custo_total": custo_elevenlabs + custo_heygen
        }
    
    def otimizar_texto(self, texto: str) -> str:
        """
        Otimiza o texto para melhor compatibilidade com as APIs.
        
        Args:
            texto: O texto a ser otimizado
            
        Returns:
            str: O texto otimizado
        """
        # Remover caracteres problemáticos
        texto_otimizado = texto
        
        # Substituir tags HTML/XML
        texto_otimizado = re.sub(r"<[^>]+>", "", texto_otimizado)
        
        # Remover caracteres de escape
        texto_otimizado = texto_otimizado.replace("\\n", " ")
        texto_otimizado = texto_otimizado.replace("\\t", " ")
        texto_otimizado = texto_otimizado.replace("\\r", " ")
        
        # Normalizar espaços
        texto_otimizado = ' '.join(texto_otimizado.split())
        
        # Normalizar pontuação
        texto_otimizado = re.sub(r"\.{2,}", ".", texto_otimizado)
        texto_otimizado = re.sub(r"\!{2,}", "!", texto_otimizado)
        texto_otimizado = re.sub(r"\?{2,}", "?", texto_otimizado)
        
        return texto_otimizado

def validar_arquivo(caminho_arquivo: str, corrigir: bool = False) -> Tuple[bool, str, Dict[str, float]]:
    """
    Valida um arquivo de roteiro.
    
    Args:
        caminho_arquivo: Caminho para o arquivo de roteiro
        corrigir: Se True, tenta corrigir problemas encontrados
        
    Returns:
        Tuple[bool, str, Dict[str, float]]: (arquivo_valido, mensagem, custos_estimados)
    """
    if not os.path.exists(caminho_arquivo):
        return False, f"Arquivo não encontrado: {caminho_arquivo}", {}
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            texto = f.read()
    except Exception as e:
        return False, f"Erro ao ler o arquivo: {e}", {}
    
    validador = ValidadorRoteiro()
    valido, problemas = validador.validar_texto(texto)
    custos = validador.estimar_custos(texto)
    
    if not valido and corrigir:
        texto_corrigido = validador.otimizar_texto(texto)
        
        # Verificar se a correção resolveu os problemas
        valido_apos_correcao, problemas_apos_correcao = validador.validar_texto(texto_corrigido)
        
        if valido_apos_correcao or len(problemas_apos_correcao) < len(problemas):
            # Salvar o texto corrigido
            caminho_corrigido = caminho_arquivo.replace(".txt", "_corrigido.txt")
            try:
                with open(caminho_corrigido, 'w', encoding='utf-8') as f:
                    f.write(texto_corrigido)
                
                return valido_apos_correcao, f"Texto corrigido salvo em: {caminho_corrigido}\nProblemas restantes: {problemas_apos_correcao}", custos
            except Exception as e:
                return False, f"Erro ao salvar o texto corrigido: {e}", custos
    
    if valido:
        return True, "O roteiro é válido para geração de áudio e vídeo.", custos
    else:
        return False, f"Problemas encontrados no roteiro:\n" + "\n".join([f"- {p}" for p in problemas]), custos

def main():
    parser = argparse.ArgumentParser(description="Validador de roteiros para evitar gastos desnecessários de créditos nas APIs")
    parser.add_argument("--arquivo", required=True, help="Caminho para o arquivo de roteiro")
    parser.add_argument("--corrigir", action="store_true", help="Tenta corrigir problemas encontrados")
    
    args = parser.parse_args()
    
    valido, mensagem, custos = validar_arquivo(args.arquivo, args.corrigir)
    
    print("\n=== Resultado da Validação ===")
    print(f"Arquivo: {args.arquivo}")
    print(f"Válido: {'Sim' if valido else 'Não'}")
    print(mensagem)
    
    print("\n=== Estimativa de Custos ===")
    print(f"Caracteres: {custos.get('caracteres', 0)}")
    print(f"Duração estimada: {custos.get('duracao_segundos', 0):.2f} segundos")
    print(f"Custo ElevenLabs: ${custos.get('custo_elevenlabs', 0):.4f}")
    print(f"Custo HeyGen: ${custos.get('custo_heygen', 0):.2f}")
    print(f"Custo total: ${custos.get('custo_total', 0):.2f}")
    
    return 0 if valido else 1

if __name__ == "__main__":
    sys.exit(main())
