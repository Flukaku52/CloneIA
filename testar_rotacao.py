#!/usr/bin/env python3
"""
Testar sistema de rotação com 3 avatares
"""

from gerenciar_avatares import GerenciadorAvatares

def testar_rotacao():
    """Testa a rotação dos avatares"""
    
    print("🔄 TESTANDO ROTAÇÃO DE AVATARES")
    print("=" * 40)
    
    gerenciador = GerenciadorAvatares()
    
    print("📋 Avatares disponíveis:")
    gerenciador.listar_avatares()
    
    print("\n🎬 Simulando próximos 5 reels:")
    print("-" * 30)
    
    for i in range(1, 6):
        avatar_id = gerenciador.obter_proximo_avatar()
        
        # Buscar nome do avatar
        avatar_nome = "Desconhecido"
        for avatar in gerenciador.config["avatares_disponiveis"]:
            if avatar["id"] == avatar_id:
                avatar_nome = avatar["nome"]
                break
        
        print(f"Reel {i}: {avatar_nome} ({avatar_id})")
    
    print(f"\n📊 Estatísticas após simulação:")
    gerenciador.mostrar_estatisticas()

if __name__ == "__main__":
    testar_rotacao()