#!/usr/bin/env python3
"""
Script para definir qual avatar será usado no próximo reel
"""

import json
from gerenciar_avatares import GerenciadorAvatares

def definir_proximo_avatar(avatar_id_desejado):
    """Define qual avatar será usado no próximo reel"""
    
    print("🎯 DEFININDO PRÓXIMO AVATAR")
    print("=" * 40)
    
    gerenciador = GerenciadorAvatares()
    
    # Encontrar o índice do avatar desejado
    index_desejado = None
    avatar_nome = None
    
    for i, avatar in enumerate(gerenciador.config["avatares_disponiveis"]):
        if avatar["id"] == avatar_id_desejado:
            index_desejado = i
            avatar_nome = avatar["nome"]
            break
    
    if index_desejado is None:
        print(f"❌ Avatar {avatar_id_desejado} não encontrado!")
        return False
    
    # Mostrar estado atual
    index_atual = gerenciador.config["configuracao_rotacao"]["proximo_avatar_index"]
    avatar_atual = gerenciador.config["avatares_disponiveis"][index_atual]
    
    print(f"📍 Estado atual:")
    print(f"   • Próximo na fila: {avatar_atual['nome']}")
    print(f"   • Índice: {index_atual}")
    
    # Ajustar para o avatar desejado
    gerenciador.config["configuracao_rotacao"]["proximo_avatar_index"] = index_desejado
    
    # Salvar configuração
    gerenciador._salvar_config()
    
    print(f"\n✅ AJUSTE REALIZADO!")
    print(f"   • Novo próximo: {avatar_nome}")
    print(f"   • ID: {avatar_id_desejado}")
    print(f"   • Índice: {index_desejado}")
    
    # Mostrar próxima sequência
    print(f"\n🔄 PRÓXIMA SEQUÊNCIA DE REELS:")
    print("-" * 30)
    
    total_avatares = len(gerenciador.config["avatares_disponiveis"])
    
    for i in range(5):
        index = (index_desejado + i) % total_avatares
        avatar = gerenciador.config["avatares_disponiveis"][index]
        print(f"Reel {i+1}: {avatar['nome']} ({avatar['id'][:8]}...)")
    
    return True

def main():
    """Função principal"""
    
    # Avatar que o usuário quer usar primeiro
    avatar_desejado = "ad46ec4202394d9aa33bcf5974bac416"
    
    print(f"🎭 SOLICITAÇÃO DO USUÁRIO")
    print(f"Definir como próximo: {avatar_desejado}")
    print()
    
    sucesso = definir_proximo_avatar(avatar_desejado)
    
    if sucesso:
        print(f"\n🎬 PRONTO!")
        print(f"O próximo reel que você gerar usará o avatar solicitado")
        print(f"Execute: python gerar_videos_reel.py")
    else:
        print(f"\n❌ Falha ao ajustar avatar")

if __name__ == "__main__":
    main()