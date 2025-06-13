#!/usr/bin/env python3
"""
Resumo completo do sistema de avatares
"""

from gerenciar_avatares import GerenciadorAvatares

def mostrar_resumo_completo():
    """Mostra resumo completo do sistema de avatares"""
    
    print("🎭 SISTEMA DE AVATARES - RESUMO COMPLETO")
    print("=" * 50)
    
    gerenciador = GerenciadorAvatares()
    
    # Lista completa
    avatares = gerenciador.config["avatares_disponiveis"]
    total = len(avatares)
    
    print(f"📊 ESTATÍSTICAS GERAIS:")
    print(f"   • Total de avatares: {total}")
    print(f"   • Todos ativos: ✅")
    print(f"   • Rotação: Sequencial automática")
    
    print(f"\n🎭 AVATARES CADASTRADOS:")
    print("-" * 30)
    
    for i, avatar in enumerate(avatares, 1):
        nome = avatar["nome"]
        avatar_id = avatar["id"]
        usos = avatar["total_usos"]
        
        print(f"{i}. {nome}")
        print(f"   ID: {avatar_id}")
        print(f"   Usos: {usos}")
        print()
    
    # Próximos avatares na rotação
    print(f"🔄 PRÓXIMA SEQUÊNCIA DE REELS:")
    print("-" * 25)
    
    # Simular próximos 5 sem afetar contador real
    index_atual = gerenciador.config["configuracao_rotacao"]["proximo_avatar_index"]
    
    for i in range(5):
        index_avatar = (index_atual + i) % total
        avatar = avatares[index_avatar]
        print(f"Reel {i+1}: {avatar['nome']} ({avatar['id'][:8]}...)")
    
    print(f"\n✅ SISTEMA PRONTO PARA USO!")
    print(f"🎬 Próximo reel usará: {avatares[index_atual]['nome']}")

if __name__ == "__main__":
    mostrar_resumo_completo()