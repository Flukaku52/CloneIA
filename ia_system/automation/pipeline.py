#!/usr/bin/env python3
"""
Pipeline completo de automação para geração de reels cripto.
"""
import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Adicionar diretório pai ao path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
sys.path.insert(0, project_root)

from ia_system.core.script_generator import ScriptGenerator
from core.audio import AudioGenerator
from clean_project.heygen_video_generator_optimized import HeyGenVideoGenerator
from gerenciar_avatares import GerenciadorAvatares

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomationPipeline:
    """
    Pipeline completo de automação para geração de reels.
    """
    
    def __init__(self, config_path: str = None):
        """
        Inicializa o pipeline de automação.
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.config_path = config_path
        
        # Inicializar componentes
        self.script_generator = ScriptGenerator(config_path)
        self.audio_generator = AudioGenerator()
        self.video_generator = HeyGenVideoGenerator()
        self.avatar_manager = GerenciadorAvatares()
        
        # Diretórios de output
        self.output_dir = os.path.join(os.getcwd(), "output", "ia_automated")
        self.audio_dir = os.path.join(self.output_dir, "audio")
        self.video_dir = os.path.join(self.output_dir, "video")
        self.roteiros_dir = os.path.join(self.output_dir, "roteiros")
        
        # Criar diretórios
        for dir_path in [self.output_dir, self.audio_dir, self.video_dir, self.roteiros_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def gerar_roteiro_automatico(self) -> Optional[Dict[str, Any]]:
        """
        Gera um roteiro automático baseado em notícias recentes.
        
        Returns:
            Dict: Dados do roteiro gerado ou None se falhar
        """
        logger.info("🤖 Iniciando geração automática de roteiro...")
        
        try:
            # Gerar roteiro
            roteiro = self.script_generator.gerar_roteiro_completo()
            
            if not roteiro:
                logger.error("Falha ao gerar roteiro")
                return None
            
            # Salvar roteiro
            roteiro_path = os.path.join(self.roteiros_dir, f"{roteiro['id']}.json")
            with open(roteiro_path, 'w', encoding='utf-8') as f:
                json.dump(roteiro, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Roteiro salvo: {roteiro_path}")
            return roteiro
            
        except Exception as e:
            logger.error(f"Erro ao gerar roteiro: {e}")
            return None
    
    def gerar_audio_automatico(self, roteiro: Dict[str, Any]) -> Optional[str]:
        """
        Gera áudio baseado no roteiro.
        
        Args:
            roteiro: Dados do roteiro
            
        Returns:
            str: Caminho do arquivo de áudio gerado ou None se falhar
        """
        logger.info("🎵 Gerando áudio automaticamente...")
        
        try:
            texto_completo = roteiro['texto_completo']
            
            # Configurações de voz das configurações padrão
            config_padrao_path = os.path.join(os.getcwd(), "config", "configuracoes_padrao_sistema.json")
            
            with open(config_padrao_path, 'r', encoding='utf-8') as f:
                config_padrao = json.load(f)
            
            audio_config = config_padrao['configuracoes_padrao_sistema']['audio_padrao']
            
            # Gerar áudio
            audio_path = os.path.join(self.audio_dir, f"{roteiro['id']}.mp3")
            
            success = self.audio_generator.generate_audio(
                text=texto_completo,
                output_path=audio_path,
                optimize=True,
                dry_run=False
            )
            
            if success:
                logger.info(f"✅ Áudio gerado: {success}")
                return success
            else:
                logger.error("Falha ao gerar áudio")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao gerar áudio: {e}")
            return None
    
    def gerar_video_automatico(self, roteiro: Dict[str, Any], audio_path: str) -> Optional[str]:
        """
        Gera vídeo com avatar baseado no roteiro e áudio.
        
        Args:
            roteiro: Dados do roteiro
            audio_path: Caminho do arquivo de áudio
            
        Returns:
            str: Caminho do arquivo de vídeo gerado ou None se falhar
        """
        logger.info("🎬 Gerando vídeo automaticamente...")
        
        try:
            # Obter próximo avatar
            avatar_id = self.avatar_manager.obter_proximo_avatar()
            
            if not avatar_id:
                logger.warning("Nenhum avatar disponível, usando padrão")
                avatar_id = "bde6a19874124e12b230248bff9ed903"  # Avatar padrão
            
            # Gerar vídeo
            video_path = os.path.join(self.video_dir, f"{roteiro['id']}.mp4")
            
            resultado = self.video_generator.generate_video(
                script=roteiro['texto_completo'],
                audio_path=audio_path,
                output_path=video_path,
                folder_name="ia_automated",
                avatar_id=avatar_id
            )
            
            if resultado:
                logger.info(f"✅ Vídeo gerado: {resultado}")
                
                # Atualizar estatísticas do avatar
                self.avatar_manager.registrar_uso_avatar(avatar_id)
                
                return resultado
            else:
                logger.error("Falha ao gerar vídeo")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao gerar vídeo: {e}")
            return None
    
    def executar_pipeline_completo(self) -> Dict[str, Any]:
        """
        Executa o pipeline completo de geração automática.
        
        Returns:
            Dict: Resultados do pipeline
        """
        logger.info("🚀 INICIANDO PIPELINE COMPLETO DE AUTOMAÇÃO")
        logger.info("=" * 60)
        
        inicio = time.time()
        resultados = {
            "sucesso": False,
            "timestamp": datetime.now().isoformat(),
            "etapas": {},
            "arquivos_gerados": {},
            "tempo_total": 0,
            "erros": []
        }
        
        try:
            # ETAPA 1: Gerar roteiro
            logger.info("📝 ETAPA 1: Gerando roteiro...")
            roteiro = self.gerar_roteiro_automatico()
            
            if not roteiro:
                resultados["erros"].append("Falha na geração do roteiro")
                return resultados
            
            resultados["etapas"]["roteiro"] = True
            resultados["arquivos_gerados"]["roteiro"] = roteiro['id']
            
            # ETAPA 2: Gerar áudio
            logger.info("🎵 ETAPA 2: Gerando áudio...")
            audio_path = self.gerar_audio_automatico(roteiro)
            
            if not audio_path:
                resultados["erros"].append("Falha na geração do áudio")
                return resultados
            
            resultados["etapas"]["audio"] = True
            resultados["arquivos_gerados"]["audio"] = audio_path
            
            # ETAPA 3: Gerar vídeo
            logger.info("🎬 ETAPA 3: Gerando vídeo...")
            video_path = self.gerar_video_automatico(roteiro, audio_path)
            
            if not video_path:
                resultados["erros"].append("Falha na geração do vídeo")
                return resultados
            
            resultados["etapas"]["video"] = True
            resultados["arquivos_gerados"]["video"] = video_path
            
            # Pipeline concluído com sucesso
            resultados["sucesso"] = True
            tempo_total = time.time() - inicio
            resultados["tempo_total"] = round(tempo_total, 2)
            
            logger.info("🎉 PIPELINE CONCLUÍDO COM SUCESSO!")
            logger.info(f"⏱️ Tempo total: {tempo_total:.2f} segundos")
            logger.info(f"📁 Arquivos em: {self.output_dir}")
            
            return resultados
            
        except Exception as e:
            logger.error(f"Erro crítico no pipeline: {e}")
            resultados["erros"].append(f"Erro crítico: {str(e)}")
            return resultados
    
    def gerar_relatorio(self, resultados: Dict[str, Any]) -> str:
        """
        Gera relatório detalhado dos resultados.
        
        Args:
            resultados: Dados dos resultados do pipeline
            
        Returns:
            str: Caminho do arquivo de relatório
        """
        relatorio_path = os.path.join(self.output_dir, f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 Relatório salvo: {relatorio_path}")
        return relatorio_path
    
    def status_sistema(self) -> Dict[str, Any]:
        """
        Verifica status dos componentes do sistema.
        
        Returns:
            Dict: Status de cada componente
        """
        status = {
            "timestamp": datetime.now().isoformat(),
            "componentes": {}
        }
        
        # Verificar APIs
        try:
            # ElevenLabs
            elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
            status["componentes"]["elevenlabs"] = {
                "configurado": bool(elevenlabs_key),
                "key_presente": bool(elevenlabs_key)
            }
            
            # HeyGen
            heygen_key = os.getenv("HEYGEN_API_KEY")
            status["componentes"]["heygen"] = {
                "configurado": bool(heygen_key),
                "key_presente": bool(heygen_key)
            }
            
            # Avatares
            try:
                avatares_lista = self.avatar_manager.listar_avatares()
                avatares_disponiveis = len(avatares_lista) if avatares_lista else 0
            except:
                avatares_disponiveis = 0
                
            status["componentes"]["avatares"] = {
                "total_disponivel": avatares_disponiveis,
                "rotacao_ativa": avatares_disponiveis > 1
            }
            
            # Sistema IA
            status["componentes"]["ia_system"] = {
                "news_collector": True,
                "script_generator": True,
                "configurado": True
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar status: {e}")
            status["erro"] = str(e)
        
        return status


if __name__ == "__main__":
    # Teste do pipeline
    pipeline = AutomationPipeline()
    
    # Verificar status primeiro
    print("🔍 VERIFICANDO STATUS DO SISTEMA...")
    status = pipeline.status_sistema()
    
    print(f"\n📊 STATUS:")
    print("-" * 30)
    for componente, info in status["componentes"].items():
        print(f"• {componente}: {info}")
    
    print(f"\n🚀 EXECUTANDO PIPELINE AUTOMÁTICO...")
    print("=" * 50)
    
    # Executar pipeline
    resultados = pipeline.executar_pipeline_completo()
    
    # Gerar relatório
    relatorio_path = pipeline.gerar_relatorio(resultados)
    
    print(f"\n📋 RESULTADOS FINAIS:")
    print("-" * 25)
    print(f"✅ Sucesso: {resultados['sucesso']}")
    print(f"⏱️ Tempo: {resultados['tempo_total']}s")
    
    if resultados["sucesso"]:
        print(f"🎬 Reel gerado automaticamente!")
        print(f"📁 Arquivos: {len(resultados['arquivos_gerados'])}")
    else:
        print(f"❌ Erros: {len(resultados['erros'])}")
        for erro in resultados["erros"]:
            print(f"   • {erro}")
    
    print(f"\n📊 Relatório: {relatorio_path}")