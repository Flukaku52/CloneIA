#!/usr/bin/env python3
"""
Script para automatizar a geração de vídeos para Reels do Instagram a partir de um script completo.
O script é dividido em partes com base em marcações de corte (por padrão "(Corte)").
"""
import os
import re
import sys
import argparse
import logging
import time
from typing import List, Dict, Tuple, Optional
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gerar_reels_automatico')

# Importar módulos necessários
try:
    from validador_roteiro import ValidadorRoteiro
    from core.utils import ensure_directory, get_timestamp_filename, OUTPUT_DIR
    VALIDADOR_DISPONIVEL = True
except ImportError:
    logger.warning("Módulo validador_roteiro não encontrado. A validação será ignorada.")
    VALIDADOR_DISPONIVEL = False

class ReelsGenerator:
    """
    Classe para gerar vídeos para Reels do Instagram a partir de um script completo.
    """
    def __init__(self, 
                 script_path: str, 
                 output_dir: str = None,
                 avatar_id: str = "01cbe2535df5453a97f4a872ea532b33",
                 folder_name: str = "reels_instagram",
                 corte_marker: str = "(Corte)",
                 validate: bool = True,
                 force: bool = False,
                 skip_video: bool = False,
                 prefix: str = "reels"):
        """
        Inicializa o gerador de Reels.
        
        Args:
            script_path: Caminho para o arquivo de script completo
            output_dir: Diretório de saída para os arquivos gerados
            avatar_id: ID do avatar a ser usado no HeyGen
            folder_name: Nome da pasta no HeyGen onde os vídeos serão salvos
            corte_marker: Marcador que indica onde o script deve ser dividido
            validate: Se True, valida cada parte do script antes de gerar áudio/vídeo
            force: Se True, gera áudio/vídeo mesmo se a validação falhar
            skip_video: Se True, gera apenas os áudios, sem os vídeos
            prefix: Prefixo para os nomes dos arquivos gerados
        """
        self.script_path = script_path
        self.output_dir = output_dir or os.path.join(OUTPUT_DIR)
        self.avatar_id = avatar_id
        self.folder_name = folder_name
        self.corte_marker = corte_marker
        self.validate = validate
        self.force = force
        self.skip_video = skip_video
        self.prefix = prefix
        
        # Garantir que os diretórios de saída existam
        self.audio_dir = os.path.join(self.output_dir, "audio")
        self.video_dir = os.path.join(self.output_dir, "videos")
        self.script_dir = os.path.join(self.output_dir, "scripts")
        
        ensure_directory(self.audio_dir)
        ensure_directory(self.video_dir)
        ensure_directory(self.script_dir)
        
        # Inicializar validador se disponível
        self.validador = ValidadorRoteiro() if VALIDADOR_DISPONIVEL and validate else None
    
    def ler_script_completo(self) -> str:
        """
        Lê o script completo do arquivo.
        
        Returns:
            str: Conteúdo do script
        """
        try:
            with open(self.script_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Erro ao ler o arquivo de script: {e}")
            sys.exit(1)
    
    def dividir_script(self, script_completo: str) -> List[str]:
        """
        Divide o script completo em partes com base no marcador de corte.
        
        Args:
            script_completo: Script completo a ser dividido
            
        Returns:
            List[str]: Lista de partes do script
        """
        # Dividir o script pelo marcador de corte
        partes = re.split(re.escape(self.corte_marker), script_completo)
        
        # Remover espaços em branco extras e linhas vazias
        partes = [parte.strip() for parte in partes]
        partes = [parte for parte in partes if parte]
        
        logger.info(f"Script dividido em {len(partes)} partes")
        return partes
    
    def otimizar_texto(self, texto: str) -> str:
        """
        Otimiza o texto para melhorar a fluidez da fala.
        
        Args:
            texto: Texto a ser otimizado
            
        Returns:
            str: Texto otimizado
        """
        # Remover espaços extras e quebras de linha
        texto = ' '.join(texto.split())
        
        # Substituir termos para melhor pronúncia
        texto = texto.replace("Bitcoin", "Bitcoim")
        
        # Remover pontuação excessiva
        texto = re.sub(r"\.{2,}", ".", texto)
        texto = re.sub(r"\!{2,}", "!", texto)
        texto = re.sub(r"\?{2,}", "?", texto)
        
        return texto
    
    def salvar_parte_script(self, parte: str, indice: int) -> str:
        """
        Salva uma parte do script em um arquivo.
        
        Args:
            parte: Parte do script a ser salva
            indice: Índice da parte (1-based)
            
        Returns:
            str: Caminho para o arquivo salvo
        """
        # Otimizar o texto
        texto_otimizado = self.otimizar_texto(parte)
        
        # Definir o caminho do arquivo
        arquivo_path = os.path.join(self.script_dir, f"{self.prefix}_parte{indice}.txt")
        
        # Salvar o arquivo
        try:
            with open(arquivo_path, 'w', encoding='utf-8') as f:
                f.write(texto_otimizado)
            logger.info(f"Parte {indice} salva em {arquivo_path}")
            return arquivo_path
        except Exception as e:
            logger.error(f"Erro ao salvar a parte {indice}: {e}")
            return None
    
    def validar_parte(self, parte: str, indice: int) -> Tuple[bool, Dict]:
        """
        Valida uma parte do script.
        
        Args:
            parte: Parte do script a ser validada
            indice: Índice da parte (1-based)
            
        Returns:
            Tuple[bool, Dict]: (valido, custos_estimados)
        """
        if not self.validador:
            return True, {}
        
        try:
            valido, problemas = self.validador.validar_texto(parte)
            custos = self.validador.estimar_custos(parte)
            
            logger.info(f"Validação da parte {indice}:")
            logger.info(f"Válido: {'Sim' if valido else 'Não'}")
            
            if not valido:
                for problema in problemas:
                    logger.warning(f"- {problema}")
                
                logger.info(f"Estimativa de custos para a parte {indice}:")
                logger.info(f"Caracteres: {custos.get('caracteres', 0)}")
                logger.info(f"Duração estimada: {custos.get('duracao_segundos', 0):.2f} segundos")
                logger.info(f"Custo ElevenLabs: ${custos.get('custo_elevenlabs', 0):.4f}")
                logger.info(f"Custo HeyGen: ${custos.get('custo_heygen', 0):.2f}")
                logger.info(f"Custo total: ${custos.get('custo_total', 0):.2f}")
            
            return valido, custos
        except Exception as e:
            logger.error(f"Erro ao validar a parte {indice}: {e}")
            return False, {}
    
    def gerar_audio(self, script_path: str, indice: int) -> Optional[str]:
        """
        Gera áudio para uma parte do script.
        
        Args:
            script_path: Caminho para o arquivo de script
            indice: Índice da parte (1-based)
            
        Returns:
            Optional[str]: Caminho para o arquivo de áudio gerado, ou None se falhar
        """
        # Definir o caminho do arquivo de áudio
        audio_path = os.path.join(self.audio_dir, f"{self.prefix}_parte{indice}.mp3")
        
        # Gerar o áudio
        try:
            import gerar_audio_rapido
            logger.info(f"Gerando áudio para a parte {indice}...")
            
            # Chamar o script de geração de áudio
            audio_result = gerar_audio_rapido.generate_audio(
                script_path=script_path,
                output_path=audio_path,
                profile_name="flukakuia",
                validate=self.validate,
                force=self.force
            )
            
            if audio_result:
                logger.info(f"Áudio para a parte {indice} gerado com sucesso: {audio_result}")
                return audio_result
            else:
                logger.error(f"Falha ao gerar áudio para a parte {indice}")
                return None
        except ImportError:
            logger.error("Módulo gerar_audio_rapido não encontrado. Não é possível gerar áudio.")
            return None
        except Exception as e:
            logger.error(f"Erro ao gerar áudio para a parte {indice}: {e}")
            return None
    
    def gerar_video(self, audio_path: str, indice: int) -> Optional[str]:
        """
        Gera vídeo para uma parte do script.
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            indice: Índice da parte (1-based)
            
        Returns:
            Optional[str]: Caminho para o arquivo de vídeo gerado, ou None se falhar
        """
        if self.skip_video:
            logger.info(f"Geração de vídeo desativada. Pulando parte {indice}.")
            return None
        
        # Definir o caminho do arquivo de vídeo
        video_path = os.path.join(self.video_dir, f"{self.prefix}_parte{indice}.mp4")
        
        # Gerar o vídeo
        try:
            import gerar_video_seguro
            logger.info(f"Gerando vídeo para a parte {indice}...")
            
            # Chamar o script de geração de vídeo
            video_result = gerar_video_seguro.generate_heygen_video(
                audio_path=audio_path,
                output_path=video_path,
                avatar_id=self.avatar_id,
                folder_name=self.folder_name,
                validate=self.validate,
                force=self.force
            )
            
            if video_result:
                logger.info(f"Vídeo para a parte {indice} gerado com sucesso: {video_result}")
                return video_result
            else:
                logger.error(f"Falha ao gerar vídeo para a parte {indice}")
                return None
        except ImportError:
            logger.error("Módulo gerar_video_seguro não encontrado. Não é possível gerar vídeo.")
            return None
        except Exception as e:
            logger.error(f"Erro ao gerar vídeo para a parte {indice}: {e}")
            return None
    
    def processar_script(self) -> Dict[str, List[str]]:
        """
        Processa o script completo, gerando áudio e vídeo para cada parte.
        
        Returns:
            Dict[str, List[str]]: Dicionário com os caminhos dos arquivos gerados
        """
        # Ler o script completo
        script_completo = self.ler_script_completo()
        
        # Dividir o script em partes
        partes = self.dividir_script(script_completo)
        
        # Inicializar listas para armazenar os caminhos dos arquivos gerados
        script_paths = []
        audio_paths = []
        video_paths = []
        
        # Estimar custo total
        custo_total_elevenlabs = 0
        custo_total_heygen = 0
        
        # Processar cada parte
        for i, parte in enumerate(partes, 1):
            logger.info(f"Processando parte {i} de {len(partes)}...")
            
            # Validar a parte
            valido, custos = self.validar_parte(parte, i)
            
            # Acumular custos estimados
            custo_total_elevenlabs += custos.get('custo_elevenlabs', 0)
            custo_total_heygen += custos.get('custo_heygen', 0)
            
            # Se a parte não for válida e force=False, pular
            if not valido and not self.force:
                logger.warning(f"Parte {i} inválida. Pulando...")
                continue
            
            # Salvar a parte em um arquivo
            script_path = self.salvar_parte_script(parte, i)
            if not script_path:
                continue
            script_paths.append(script_path)
            
            # Gerar áudio para a parte
            audio_path = self.gerar_audio(script_path, i)
            if not audio_path:
                continue
            audio_paths.append(audio_path)
            
            # Gerar vídeo para a parte
            if not self.skip_video:
                video_path = self.gerar_video(audio_path, i)
                if video_path:
                    video_paths.append(video_path)
            
            # Pequena pausa para evitar sobrecarregar as APIs
            time.sleep(1)
        
        # Exibir resumo dos custos estimados
        logger.info("\n=== Resumo dos Custos Estimados ===")
        logger.info(f"Custo total ElevenLabs: ${custo_total_elevenlabs:.4f}")
        logger.info(f"Custo total HeyGen: ${custo_total_heygen:.2f}")
        logger.info(f"Custo total: ${custo_total_elevenlabs + custo_total_heygen:.2f}")
        
        return {
            "scripts": script_paths,
            "audios": audio_paths,
            "videos": video_paths
        }

def main():
    parser = argparse.ArgumentParser(description="Gerador automático de vídeos para Reels do Instagram")
    parser.add_argument("--script", required=True, help="Caminho para o arquivo de script completo")
    parser.add_argument("--output", help="Diretório de saída para os arquivos gerados")
    parser.add_argument("--avatar", default="01cbe2535df5453a97f4a872ea532b33", 
                      help="ID do avatar a ser usado (padrão: Flukaku Rapidinha)")
    parser.add_argument("--folder", default="reels_instagram", 
                      help="Nome da pasta no HeyGen onde os vídeos serão salvos (padrão: reels_instagram)")
    parser.add_argument("--marker", default="(Corte)", 
                      help="Marcador que indica onde o script deve ser dividido (padrão: (Corte))")
    parser.add_argument("--no-validate", action="store_true", 
                      help="Desativa a validação das partes do script")
    parser.add_argument("--force", action="store_true", 
                      help="Força a geração mesmo se a validação falhar")
    parser.add_argument("--audio-only", action="store_true", 
                      help="Gera apenas os áudios, sem os vídeos")
    parser.add_argument("--prefix", default="reels", 
                      help="Prefixo para os nomes dos arquivos gerados (padrão: reels)")
    
    args = parser.parse_args()
    
    # Criar o gerador de Reels
    reels_generator = ReelsGenerator(
        script_path=args.script,
        output_dir=args.output,
        avatar_id=args.avatar,
        folder_name=args.folder,
        corte_marker=args.marker,
        validate=not args.no_validate,
        force=args.force,
        skip_video=args.audio_only,
        prefix=args.prefix
    )
    
    # Processar o script
    resultados = reels_generator.processar_script()
    
    # Exibir resumo
    logger.info("\n=== Resumo da Geração ===")
    logger.info(f"Scripts gerados: {len(resultados['scripts'])}")
    logger.info(f"Áudios gerados: {len(resultados['audios'])}")
    logger.info(f"Vídeos gerados: {len(resultados['videos'])}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
