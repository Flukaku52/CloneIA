#!/usr/bin/env python3
"""
Script para adicionar novo avatar rapidamente
"""

from gerenciar_avatares import GerenciadorAvatares

def adicionar_novo_avatar():
    """Adiciona o novo avatar fornecido pelo usuário"""
    
    # Novo avatar fornecido
    novo_avatar_id = "670f73152cff47039134d5a2c27a7f76"
    nome_avatar = "avatar_terceiro"
    descricao = "Terceiro avatar adicionado ao sistema"
    
    print("🎭 ADICIONANDO NOVO AVATAR")
    print("=" * 40)
    
    gerenciador = GerenciadorAvatares()
    
    # Adicionar o avatar
    sucesso = gerenciador.adicionar_avatar(novo_avatar_id, nome_avatar, descricao)
    
    if sucesso:
        print(f"\n✅ Avatar adicionado com sucesso!")
        print(f"ID: {novo_avatar_id}")
        print(f"Nome: {nome_avatar}")
        
        # Mostrar todos os avatares
        print("\n📋 LISTA ATUALIZADA:")
        gerenciador.listar_avatares()
        
        # Mostrar estatísticas
        print("\n📊 ESTATÍSTICAS:")
        gerenciador.mostrar_estatisticas()
        
    else:
        print("❌ Erro ao adicionar avatar")

if __name__ == "__main__":
    adicionar_novo_avatar()