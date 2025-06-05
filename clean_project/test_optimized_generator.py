#!/usr/bin/env python3
"""
Script para testar o gerador de vídeo otimizado.
"""
import os
import logging
import argparse
from heygen_video_generator_optimized import HeyGenVideoGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_optimized')

def main():
    """
    Função principal para testar o gerador de vídeo otimizado.
    """
    parser = argparse.ArgumentParser(description="Teste do gerador de vídeo otimizado")
    parser.add_argument("--list-avatars", action="store_true", help="Listar avatares disponíveis")
    parser.add_argument("--generate", action="store_true", help="Gerar um vídeo de teste")
    parser.add_argument("--script", help="Texto do script para o vídeo")
    parser.add_argument("--avatar-id", help="ID do avatar a ser usado (opcional)")
    
    args = parser.parse_args()
    
    # Criar instância do gerador
    generator = HeyGenVideoGenerator()
    
    if args.list_avatars:
        logger.info("Listando avatares disponíveis...")
        avatars = generator.list_avatars()
        logger.info(f"Total de avatares: {len(avatars)}")
    
    elif args.generate:
        script = args.script
        if not script:
            script = "E aí cambada! Este é um teste do gerador de vídeo otimizado para o quadro Rapidinha Cripto. Estamos testando a geração de vídeo com o avatar personalizado."
        
        logger.info(f"Gerando vídeo com o script: {script[:50]}...")
        video_path = generator.generate_video(script, avatar_id=args.avatar_id)
        
        if video_path:
            logger.info(f"Vídeo gerado com sucesso: {video_path}")
        else:
            logger.error("Falha ao gerar o vídeo.")
    
    else:
        logger.info("Nenhuma ação especificada. Use --list-avatars ou --generate.")
        parser.print_help()

if __name__ == "__main__":
    main()
