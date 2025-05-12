#!/usr/bin/env python3
"""
Script para gerar vídeo no HeyGen com validação de roteiro para evitar gastos desnecessários.
"""
import os
import sys
import argparse
import logging
from heygen_video_generator import HeyGenVideoGenerator
from core.utils import ensure_directory, get_timestamp_filename, OUTPUT_DIR

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gerar_video_seguro')

def generate_heygen_video(audio_path: str = None, script_path: str = None, output_path: str = None, 
                         avatar_id: str = None, folder_name: str = "augment",
                         validate: bool = True, force: bool = False):
    """
    Gera um vídeo no HeyGen usando um arquivo de áudio ou script, com validação prévia.
    
    Args:
        audio_path: Caminho para o arquivo de áudio
        script_path: Caminho para o arquivo de script (obrigatório se audio_path não for fornecido)
        output_path: Caminho para salvar o vídeo (se None, gera um nome baseado no timestamp)
        avatar_id: ID do avatar a ser usado (se None, usa o avatar configurado)
        folder_name: Nome da pasta no HeyGen onde o vídeo será salvo
        validate: Se True, valida o roteiro antes de gerar o vídeo
        force: Se True, gera o vídeo mesmo se a validação falhar
        
    Returns:
        str: Caminho para o vídeo gerado, ou None se falhar
    """
    # Verificar se temos áudio ou script
    if not audio_path and not script_path:
        logger.error("É necessário fornecer um arquivo de áudio ou um script")
        return None
    
    # Se temos um script, validar antes de prosseguir
    script_content = None
    if script_path and os.path.exists(script_path):
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
        except Exception as e:
            logger.error(f"Erro ao ler o arquivo de script: {e}")
            return None
    
    # Validar o roteiro antes de gerar o vídeo
    if validate and script_content:
        try:
            from validador_roteiro import ValidadorRoteiro
            validador = ValidadorRoteiro()
            valido, problemas = validador.validar_texto(script_content)
            custos = validador.estimar_custos(script_content)
            
            logger.info("\n=== Validação do Roteiro ===")
            logger.info(f"Válido: {'Sim' if valido else 'Não'}")
            
            if not valido:
                for problema in problemas:
                    logger.warning(f"- {problema}")
                
                logger.info("\n=== Estimativa de Custos ===")
                logger.info(f"Caracteres: {custos.get('caracteres', 0)}")
                logger.info(f"Duração estimada: {custos.get('duracao_segundos', 0):.2f} segundos")
                logger.info(f"Custo ElevenLabs: ${custos.get('custo_elevenlabs', 0):.4f}")
                logger.info(f"Custo HeyGen: ${custos.get('custo_heygen', 0):.2f}")
                logger.info(f"Custo total: ${custos.get('custo_total', 0):.2f}")
                
                if not force:
                    logger.error("Geração de vídeo cancelada devido a problemas no roteiro. Use --force para ignorar.")
                    return None
                else:
                    logger.warning("Ignorando problemas no roteiro devido à flag --force.")
        except ImportError:
            logger.warning("Módulo validador_roteiro não encontrado. Pulando validação.")
    
    # Verificar o arquivo de áudio
    if audio_path and not os.path.exists(audio_path):
        logger.error(f"Arquivo de áudio não encontrado: {audio_path}")
        return None
    
    # Criar o gerador de vídeo do HeyGen
    heygen_generator = HeyGenVideoGenerator()
    
    # Definir o ID do avatar se fornecido
    if avatar_id:
        heygen_generator.avatar_id = avatar_id
        logger.info(f"Usando avatar com ID: {avatar_id}")
    
    # Definir o caminho para o vídeo de saída
    if not output_path:
        timestamp = get_timestamp_filename("heygen", "mp4")
        output_path = os.path.join(OUTPUT_DIR, "videos", timestamp)
    
    # Garantir que o diretório existe
    ensure_directory(os.path.dirname(output_path))
    
    # Gerar o vídeo
    logger.info("Gerando vídeo com o HeyGen...")
    
    video_result = heygen_generator.generate_video(
        script=script_content,  # Texto para fallback ou uso direto
        audio_path=audio_path,  # Usar o áudio se fornecido
        output_path=output_path,
        folder_name=folder_name  # Salvar na pasta especificada do HeyGen
    )
    
    if video_result:
        logger.info(f"Vídeo gerado com sucesso: {video_result}")
        return video_result
    else:
        logger.error("Falha ao gerar o vídeo")
        return None

def main():
    parser = argparse.ArgumentParser(description="Gerador de vídeo seguro para o CloneIA")
    parser.add_argument("--audio", help="Caminho para o arquivo de áudio")
    parser.add_argument("--script", help="Caminho para o arquivo de script")
    parser.add_argument("--output", help="Caminho para salvar o vídeo")
    parser.add_argument("--avatar", default="01cbe2535df5453a97f4a872ea532b33", 
                      help="ID do avatar a ser usado (padrão: Flukaku Rapidinha)")
    parser.add_argument("--folder", default="augment", 
                      help="Nome da pasta no HeyGen onde o vídeo será salvo (padrão: augment)")
    parser.add_argument("--no-validate", action="store_true", help="Desativa a validação do roteiro")
    parser.add_argument("--force", action="store_true", help="Força a geração mesmo com problemas no roteiro")
    parser.add_argument("--validate-only", action="store_true", help="Apenas valida o roteiro, sem gerar vídeo")
    
    args = parser.parse_args()
    
    # Verificar se temos áudio ou script
    if not args.audio and not args.script:
        logger.error("É necessário fornecer um arquivo de áudio (--audio) ou um script (--script)")
        return 1
    
    # Se a opção --validate-only foi especificada, apenas validar o roteiro
    if args.validate_only and args.script:
        try:
            from validador_roteiro import validar_arquivo
            valido, mensagem, custos = validar_arquivo(args.script, corrigir=False)
            
            print("\n=== Resultado da Validação ===")
            print(f"Arquivo: {args.script}")
            print(f"Válido: {'Sim' if valido else 'Não'}")
            print(mensagem)
            
            print("\n=== Estimativa de Custos ===")
            print(f"Caracteres: {custos.get('caracteres', 0)}")
            print(f"Duração estimada: {custos.get('duracao_segundos', 0):.2f} segundos")
            print(f"Custo ElevenLabs: ${custos.get('custo_elevenlabs', 0):.4f}")
            print(f"Custo HeyGen: ${custos.get('custo_heygen', 0):.2f}")
            print(f"Custo total: ${custos.get('custo_total', 0):.2f}")
            
            return 0 if valido else 1
        except ImportError:
            logger.error("Módulo validador_roteiro não encontrado. Não é possível validar o roteiro.")
            return 1
    
    # Gerar o vídeo
    video_path = generate_heygen_video(
        audio_path=args.audio,
        script_path=args.script,
        output_path=args.output,
        avatar_id=args.avatar,
        folder_name=args.folder,
        validate=not args.no_validate,
        force=args.force
    )
    
    # Retornar o caminho do vídeo para uso em outros scripts
    if video_path:
        print(f"VIDEO_PATH={video_path}")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
