#!/usr/bin/env python3
"""
Gerador de áudio para os vídeos Rapidinha.
"""
import os
import json
import logging
import requests
from datetime import datetime
from typing import Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('audio_generator')

class AudioGenerator:
    """
    Classe para gerar áudio a partir de texto usando a API do ElevenLabs.
    """
    def __init__(self):
        """
        Inicializa o gerador de áudio.
        """
        # Verificar API key
        self.api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not self.api_key:
            logger.warning("API key do ElevenLabs não encontrada. Usando valor padrão.")
            self.api_key = "sk_2eeadfe816f7442422d9a3a508e5d912797de421403ba9d6"
            
        # ID da voz FlukakuIA
        self.voice_id = "oG30eP3GaYrCwnabbDCw"  # FlukakuIA
        
        # Configurações de voz otimizadas
        self.voice_settings = {
            "stability": 0.71,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
        
        logger.info("Gerador de áudio inicializado.")

    def generate_audio(self, text: str, output_file: Optional[str] = None) -> Optional[str]:
        """
        Gera áudio a partir de texto usando a API do ElevenLabs.
        
        Args:
            text: Texto para gerar áudio
            output_file: Caminho para o arquivo de saída (opcional)
            
        Returns:
            Optional[str]: Caminho para o arquivo de áudio gerado, ou None em caso de erro
        """
        if not text:
            logger.error("Texto vazio. Não é possível gerar áudio.")
            return None
            
        # Definir URL da API
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        
        # Configurar headers
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Configurar payload
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": self.voice_settings
        }
        
        try:
            # Fazer requisição para a API
            response = requests.post(url, json=payload, headers=headers)
            
            # Verificar se a requisição foi bem-sucedida
            if response.status_code != 200:
                logger.error(f"Erro ao gerar áudio: {response.status_code} - {response.text}")
                return None
                
            # Definir nome do arquivo de saída se não for fornecido
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"output/audio/rapidinha_audio_{timestamp}.mp3"
                
            # Criar diretório de saída se não existir
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
                
            # Salvar áudio
            with open(output_file, "wb") as f:
                f.write(response.content)
                
            logger.info(f"Áudio gerado com sucesso: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Erro ao gerar áudio: {e}")
            return None
