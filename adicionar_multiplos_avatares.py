#!/usr/bin/env python3
"""
Script para adicionar múltiplos avatares de uma vez
"""

from gerenciar_avatares import GerenciadorAvatares

def adicionar_avatares_batch():
    """Adiciona os 3 novos avatares fornecidos pelo usuário"""
    
    # Novos avatares (o primeiro já existe, mas vou verificar)
    novos_avatares = [
        {
            "id": "670f73152cff47039134d5a2c27a7f76",
            "nome": "avatar_terceiro", 
            "descricao": "Terceiro avatar (já adicionado)"
        },
        {
            "id": "86454c7113894f6f8dc0496025cd8346",
            "nome": "avatar_quarto",
            "descricao": "Quarto avatar adicionado ao sistema"
        },
        {
            "id": "ad46ec4202394d9aa33bcf5974bac416", 
            "nome": "avatar_quinto",
            "descricao": "Quinto avatar adicionado ao sistema"
        }
    ]
    
    print("🎭 ADICIONANDO MÚLTIPLOS AVATARES")
    print("=" * 45)
    
    gerenciador = GerenciadorAvatares()
    
    # Mostrar estado atual
    print("📋 AVATARES ATUAIS:")
    gerenciador.listar_avatares()
    
    print("\n🔄 ADICIONANDO NOVOS AVATARES:")
    print("-" * 30)
    
    avatares_adicionados = 0
    
    for avatar in novos_avatares:
        avatar_id = avatar["id"]
        nome = avatar["nome"]
        descricao = avatar["descricao"]
        
        print(f"\n➕ Tentando adicionar: {nome}")
        print(f"   ID: {avatar_id}")
        
        sucesso = gerenciador.adicionar_avatar(avatar_id, nome, descricao)
        
        if sucesso:
            avatares_adicionados += 1
            print(f"   ✅ Adicionado com sucesso!")
        else:
            print(f"   ⚠️  Já existe ou erro")
    
    print(f"\n📊 RESUMO:")
    print(f"   • Avatares adicionados: {avatares_adicionados}")
    
    # Mostrar estado final
    print(f"\n📋 LISTA FINAL DE AVATARES:")
    gerenciador.listar_avatares()
    
    # Estatísticas
    print(f"\n📈 ESTATÍSTICAS ATUALIZADAS:")
    gerenciador.mostrar_estatisticas()
    
    return avatares_adicionados

def testar_rotacao_completa():
    """Testa a rotação com todos os avatares"""
    
    print(f"\n🔄 TESTANDO ROTAÇÃO COMPLETA")
    print("=" * 35)
    
    gerenciador = GerenciadorAvatares()
    
    total_avatares = len(gerenciador.config["avatares_disponiveis"])
    print(f"🎭 Total de avatares ativos: {total_avatares}")
    
    print(f"\n🎬 Simulando próximos {total_avatares + 2} reels:")
    print("-" * 40)
    
    for i in range(1, total_avatares + 3):
        avatar_id = gerenciador.obter_proximo_avatar()
        
        # Buscar nome do avatar
        avatar_nome = "Desconhecido"
        for avatar in gerenciador.config["avatares_disponiveis"]:
            if avatar["id"] == avatar_id:
                avatar_nome = avatar["nome"]
                break
        
        print(f"Reel {i:2d}: {avatar_nome} ({avatar_id[:8]}...)")
    
    print(f"\n✅ Rotação completa testada!")

if __name__ == "__main__":
    # Adicionar avatares
    adicionados = adicionar_avatares_batch()
    
    if adicionados > 0:
        # Testar rotação
        testar_rotacao_completa()
        
        print(f"\n🎉 PROCESSO CONCLUÍDO!")
        print(f"🎭 Sistema agora tem múltiplos avatares em rotação")
        print(f"🔄 Próximo reel usará o avatar na sequência")
    else:
        print(f"\n⚠️  Nenhum avatar novo foi adicionado")
        print(f"💡 Todos os IDs já existem no sistema")