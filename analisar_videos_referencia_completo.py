#!/usr/bin/env python3
"""
Script principal para analisar vídeos de referência e gerar análise de estilo.
"""
import os
import sys
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('analisar_completo')

def executar_script(script, args=None):
    """
    Executa um script Python.
    
    Args:
        script: Caminho para o script
        args: Argumentos para o script
        
    Returns:
        bool: True se o script foi executado com sucesso, False caso contrário
    """
    try:
        # Construir comando
        cmd = [sys.executable, script]
        if args:
            cmd.extend(args)
        
        # Executar comando
        logger.info(f"Executando script: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True)
        
        return result.returncode == 0
    
    except Exception as e:
        logger.error(f"Erro ao executar script {script}: {e}")
        return False

def analisar_videos_referencia(videos_dir, output_dir, debug=False):
    """
    Analisa vídeos de referência e gera análise de estilo.
    
    Args:
        videos_dir: Diretório contendo os vídeos de referência
        output_dir: Diretório de saída para os resultados
        debug: Ativar modo de depuração
        
    Returns:
        bool: True se a análise foi concluída com sucesso, False caso contrário
    """
    try:
        # Criar diretórios de saída
        analysis_dir = os.path.join(output_dir, 'videos')
        estilo_dir = os.path.join(output_dir, 'estilo')
        docs_dir = os.path.join(output_dir, 'docs')
        
        os.makedirs(analysis_dir, exist_ok=True)
        os.makedirs(estilo_dir, exist_ok=True)
        os.makedirs(docs_dir, exist_ok=True)
        
        # Definir argumentos para os scripts
        debug_arg = ['--debug'] if debug else []
        
        # Etapa 1: Analisar vídeos
        logger.info("Etapa 1: Analisando vídeos...")
        analisar_args = [
            '--videos', videos_dir,
            '--output', analysis_dir
        ]
        analisar_args.extend(debug_arg)
        
        if not executar_script('analisar_videos_referencia.py', analisar_args):
            logger.error("Falha na etapa 1: Analisar vídeos")
            return False
        
        # Etapa 2: Extrair características de estilo
        logger.info("Etapa 2: Extraindo características de estilo...")
        extrair_args = [
            '--analysis', analysis_dir,
            '--output', estilo_dir
        ]
        extrair_args.extend(debug_arg)
        
        if not executar_script('extrair_caracteristicas_estilo.py', extrair_args):
            logger.error("Falha na etapa 2: Extrair características de estilo")
            return False
        
        # Etapa 3: Gerar análise de estilo
        logger.info("Etapa 3: Gerando análise de estilo...")
        gerar_args = [
            '--estilo', estilo_dir,
            '--output', docs_dir
        ]
        gerar_args.extend(debug_arg)
        
        if not executar_script('gerar_analise_estilo.py', gerar_args):
            logger.error("Falha na etapa 3: Gerar análise de estilo")
            return False
        
        # Etapa 4: Atualizar base de conhecimento
        logger.info("Etapa 4: Atualizando base de conhecimento...")
        if not atualizar_base_conhecimento(docs_dir):
            logger.error("Falha na etapa 4: Atualizar base de conhecimento")
            return False
        
        logger.info("Análise de vídeos de referência concluída com sucesso!")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao analisar vídeos de referência: {e}")
        return False

def atualizar_base_conhecimento(docs_dir):
    """
    Atualiza a base de conhecimento com a análise de estilo.
    
    Args:
        docs_dir: Diretório contendo os documentos de análise
        
    Returns:
        bool: True se a atualização foi concluída com sucesso, False caso contrário
    """
    try:
        # Verificar se o arquivo de análise existe
        analise_file = os.path.join(docs_dir, 'analise_estilo.md')
        if not os.path.exists(analise_file):
            logger.error(f"Arquivo de análise não encontrado: {analise_file}")
            return False
        
        # Verificar se o arquivo de base de conhecimento existe
        knowledge_base_file = 'config/knowledge_base.json'
        if not os.path.exists(knowledge_base_file):
            logger.error(f"Arquivo de base de conhecimento não encontrado: {knowledge_base_file}")
            return False
        
        # Copiar arquivo de análise para a pasta docs
        import shutil
        destino = 'docs/analise_videos_referencia.md'
        shutil.copy2(analise_file, destino)
        logger.info(f"Arquivo de análise copiado para: {destino}")
        
        # Atualizar base de conhecimento
        import json
        with open(knowledge_base_file, 'r', encoding='utf-8') as f:
            knowledge_base = json.load(f)
        
        # Verificar se o documento já existe na base de conhecimento
        doc_id = 'analise_videos_referencia'
        doc_exists = False
        
        for doc in knowledge_base.get('documentos', []):
            if doc.get('id') == doc_id:
                doc_exists = True
                doc['caminho'] = destino
                doc['descricao'] = 'Análise detalhada do estilo de comunicação com base nos vídeos de referência'
                doc['prioridade'] = 'máxima'
                doc['categoria'] = 'estilo'
                doc['atualizado_em'] = datetime.now().isoformat()
                break
        
        # Adicionar documento se não existir
        if not doc_exists:
            if 'documentos' not in knowledge_base:
                knowledge_base['documentos'] = []
            
            knowledge_base['documentos'].append({
                'id': doc_id,
                'caminho': destino,
                'descricao': 'Análise detalhada do estilo de comunicação com base nos vídeos de referência',
                'prioridade': 'máxima',
                'categoria': 'estilo',
                'criado_em': datetime.now().isoformat()
            })
        
        # Salvar base de conhecimento atualizada
        with open(knowledge_base_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, indent=2)
        
        logger.info(f"Base de conhecimento atualizada: {knowledge_base_file}")
        
        return True
    
    except Exception as e:
        logger.error(f"Erro ao atualizar base de conhecimento: {e}")
        return False

def main():
    """
    Função principal.
    """
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Analisador completo de vídeos de referência")
    parser.add_argument("--videos", help="Diretório contendo os vídeos de referência", 
                        default="/Users/renatosantannasilva/Documents/augment-projects/CloneIA/reference/videos")
    parser.add_argument("--output", help="Diretório de saída para os resultados", 
                        default="analysis")
    parser.add_argument("--debug", action="store_true", help="Ativar modo de depuração")

    args = parser.parse_args()

    # Configurar nível de log
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Analisar vídeos de referência
    if analisar_videos_referencia(args.videos, args.output, args.debug):
        logger.info("Processo concluído com sucesso!")
        return 0
    else:
        logger.error("Falha no processo de análise")
        return 1

if __name__ == "__main__":
    sys.exit(main())
