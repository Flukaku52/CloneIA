#!/usr/bin/env python3
"""
Script de configuração para o projeto CloneIA.
"""
import os
import sys
import subprocess

def main():
    """
    Configura o ambiente para o projeto CloneIA.
    """
    print("\n=== Configurando o ambiente para o projeto CloneIA ===\n")
    
    # Verificar se o Python está instalado
    print("Verificando a versão do Python...")
    python_version = sys.version.split()[0]
    print(f"Python {python_version} encontrado.")
    
    # Criar diretórios necessários
    print("\nCriando diretórios necessários...")
    directories = [
        "output/audio",
        "output/videos",
        "scripts",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Diretório '{directory}' criado ou já existente.")
    
    # Instalar dependências
    print("\nInstalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependências instaladas com sucesso.")
    except subprocess.CalledProcessError:
        print("Erro ao instalar dependências. Verifique se o pip está instalado.")
    
    # Verificar arquivo .env
    print("\nVerificando arquivo .env...")
    if not os.path.exists(".env"):
        print("Arquivo .env não encontrado. Criando um modelo...")
        with open(".env", "w") as f:
            f.write("# Chaves de API para serviços\n")
            f.write("ELEVENLABS_API_KEY=sua_chave_elevenlabs_aqui\n")
            f.write("HEYGEN_API_KEY=sua_chave_heygen_aqui\n")
        print("Arquivo .env criado. Por favor, edite-o com suas chaves de API.")
    else:
        print("Arquivo .env encontrado.")
    
    print("\n=== Configuração concluída ===\n")
    print("Para começar a usar o projeto, edite o arquivo .env com suas chaves de API.")
    print("Em seguida, execute 'python rapidinha_generator_optimized.py' para gerar um vídeo.")

if __name__ == "__main__":
    main()
