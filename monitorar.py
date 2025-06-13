#!/usr/bin/env python3
"""
Script simplificado para monitorar notícias.
"""
from ia_system.automation.monitor_noticias import NewsMonitor

if __name__ == "__main__":
    print("🔍 MONITOR DE NOTÍCIAS CRIPTO")
    print("=" * 40)
    print("1. Verificar agora (uma vez)")
    print("2. Monitoramento contínuo (15 min)")
    print("3. Monitoramento rápido (5 min)")
    print("=" * 40)
    
    opcao = input("Escolha uma opção (1-3): ").strip()
    
    monitor = NewsMonitor()
    
    if opcao == "1":
        monitor.monitorar_uma_vez()
    elif opcao == "2":
        monitor.monitorar_continuo(intervalo_minutos=15)
    elif opcao == "3":
        monitor.monitorar_continuo(intervalo_minutos=5)
    else:
        print("❌ Opção inválida!")