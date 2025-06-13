#!/usr/bin/env python3
"""
Script para configurar sistema de notificações.
"""
from ia_system.core.notificador import Notificador
import json
import os

def main():
    print("🔔 CONFIGURAÇÃO DE NOTIFICAÇÕES")
    print("=" * 50)
    
    notificador = Notificador()
    
    print("\n📱 TIPOS DE NOTIFICAÇÃO DISPONÍVEIS:")
    print("1. Desktop (macOS/Windows/Linux)")
    print("2. Som de alerta")
    print("3. Arquivo de log")
    print("4. Discord (webhook)")
    print("5. Telegram (em breve)")
    
    print("\n🎯 CONFIGURAÇÃO ATUAL:")
    config = notificador.config
    
    metodos = config.get("metodos_ativos", [])
    print(f"• Métodos ativos: {', '.join(metodos) if metodos else 'Nenhum'}")
    print(f"• Webhook Discord: {'✅ Configurado' if config.get('webhook_discord') else '❌ Não configurado'}")
    
    print("\n" + "=" * 50)
    print("OPÇÕES:")
    print("1. Testar notificações")
    print("2. Configurar webhook Discord")
    print("3. Ativar/desativar métodos")
    print("4. Ver arquivos de notificação")
    print("0. Sair")
    
    while True:
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            testar_notificacoes(notificador)
        elif opcao == "2":
            configurar_discord(notificador)
        elif opcao == "3":
            configurar_metodos(notificador)
        elif opcao == "4":
            ver_arquivos_notificacao()
        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida!")

def testar_notificacoes(notificador):
    """Testa todas as notificações."""
    print("\n🧪 TESTANDO NOTIFICAÇÕES...")
    
    # Teste desktop + som
    notificador.notificar_completo(
        titulo="Teste do Sistema de Monitoramento",
        mensagem="Bitcoin atinge nova máxima histórica!",
        prioridade="alta",
        detalhes={
            "fonte": "CoinDesk",
            "categoria": "mercado",
            "timestamp": "agora"
        }
    )
    
    print("✅ Teste enviado!")
    print("Verifique:")
    print("• Notificação desktop apareceu")
    print("• Som foi tocado")
    print("• Arquivo salvo em output/notificacoes/")

def configurar_discord(notificador):
    """Configura webhook do Discord."""
    print("\n🎮 CONFIGURAÇÃO DO DISCORD")
    print("-" * 30)
    print("Para receber alertas no Discord:")
    print("1. Vá no seu servidor Discord")
    print("2. Configurações do Canal > Integrações > Webhooks")
    print("3. Criar Webhook")
    print("4. Copiar a URL do webhook")
    
    webhook_url = input("\nCole a URL do webhook (ou Enter para pular): ").strip()
    
    if webhook_url:
        if "discord.com/api/webhooks/" in webhook_url:
            notificador.configurar_webhook_discord(webhook_url)
            print("✅ Webhook Discord configurado!")
            
            # Testar
            teste = input("Testar agora? (s/n): ").lower()
            if teste == 's':
                notificador.enviar_webhook_discord(
                    "🧪 Teste do Sistema",
                    "Sistema de monitoramento cripto funcionando!",
                    [{"titulo": "Bitcoin atinge $100k", "fonte": "CoinDesk"}]
                )
                print("📤 Mensagem de teste enviada para Discord!")
        else:
            print("❌ URL inválida. Deve conter 'discord.com/api/webhooks/'")

def configurar_metodos(notificador):
    """Configura quais métodos usar."""
    print("\n⚙️ CONFIGURAÇÃO DE MÉTODOS")
    print("-" * 30)
    
    metodos_disponiveis = ["desktop", "som", "arquivo", "discord"]
    metodos_ativos = notificador.config.get("metodos_ativos", [])
    
    print("Métodos disponíveis:")
    for i, metodo in enumerate(metodos_disponiveis, 1):
        status = "✅" if metodo in metodos_ativos else "❌"
        print(f"{i}. {status} {metodo}")
    
    print("\nDigite os números dos métodos que deseja ATIVAR (ex: 1,2,3):")
    escolha = input("Métodos: ").strip()
    
    if escolha:
        try:
            indices = [int(x.strip()) - 1 for x in escolha.split(",")]
            novos_metodos = [metodos_disponiveis[i] for i in indices if 0 <= i < len(metodos_disponiveis)]
            
            notificador.config["metodos_ativos"] = novos_metodos
            notificador._salvar_config()
            
            print(f"✅ Métodos atualizados: {', '.join(novos_metodos)}")
        except:
            print("❌ Formato inválido. Use números separados por vírgula.")

def ver_arquivos_notificacao():
    """Mostra arquivos de notificação."""
    notif_dir = "output/notificacoes"
    
    if os.path.exists(notif_dir):
        arquivos = [f for f in os.listdir(notif_dir) if f.endswith('.txt')]
        
        if arquivos:
            print(f"\n📁 ARQUIVOS DE NOTIFICAÇÃO ({len(arquivos)} encontrados):")
            print("-" * 40)
            
            for arquivo in sorted(arquivos)[-5:]:  # Últimos 5
                caminho = os.path.join(notif_dir, arquivo)
                tamanho = os.path.getsize(caminho)
                print(f"• {arquivo} ({tamanho} bytes)")
            
            # Mostrar último arquivo
            if arquivos:
                ultimo = sorted(arquivos)[-1]
                print(f"\n📄 CONTEÚDO DO ÚLTIMO ARQUIVO ({ultimo}):")
                print("-" * 40)
                
                with open(os.path.join(notif_dir, ultimo), 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    print(conteudo[-500:])  # Últimos 500 chars
        else:
            print("📭 Nenhum arquivo de notificação encontrado")
    else:
        print("📂 Diretório de notificações não existe ainda")

if __name__ == "__main__":
    main()