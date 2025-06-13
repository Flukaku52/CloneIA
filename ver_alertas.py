#!/usr/bin/env python3
"""
Script para visualizar alertas de notícias de forma organizada.
"""
import os
import json
from datetime import datetime
import glob

def main():
    print("🔔 ALERTAS DE NOTÍCIAS CRIPTO")
    print("=" * 50)
    
    # Buscar arquivos de alerta
    alertas_dir = "output/notificacoes"
    if not os.path.exists(alertas_dir):
        print("📭 Nenhum alerta encontrado ainda")
        return
    
    arquivos = glob.glob(os.path.join(alertas_dir, "alertas_*.txt"))
    
    if not arquivos:
        print("📭 Nenhum arquivo de alerta encontrado")
        return
    
    # Pegar arquivo mais recente
    arquivo_mais_recente = max(arquivos, key=os.path.getmtime)
    nome_arquivo = os.path.basename(arquivo_mais_recente)
    
    print(f"📄 Arquivo: {nome_arquivo}")
    print(f"📅 Modificado: {datetime.fromtimestamp(os.path.getmtime(arquivo_mais_recente)).strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Ler e mostrar conteúdo
    with open(arquivo_mais_recente, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Separar alertas
    alertas = conteudo.split("============================================================")
    alertas = [a.strip() for a in alertas if a.strip()]
    
    print(f"🚨 TOTAL DE ALERTAS: {len(alertas)}")
    print("=" * 50)
    
    for i, alerta in enumerate(alertas, 1):
        if not alerta:
            continue
            
        linhas = alerta.split('\n')
        titulo_linha = None
        
        # Encontrar linha do título
        for linha in linhas:
            if '🚨' in linha and ' - ' in linha:
                titulo_linha = linha
                break
        
        if titulo_linha:
            # Extrair timestamp e título
            partes = titulo_linha.split(' - ', 1)
            if len(partes) == 2:
                timestamp = partes[0].replace('🚨 ', '')
                titulo = partes[1]
                
                print(f"\n📌 ALERTA #{i}")
                print(f"⏰ Horário: {timestamp}")
                print(f"📰 Título: {titulo}")
                
                # Mostrar detalhes
                detalhes_iniciaram = False
                for linha in linhas:
                    if 'DETALHES:' in linha:
                        detalhes_iniciaram = True
                        continue
                    elif detalhes_iniciaram and linha.strip():
                        if linha.startswith('• '):
                            print(f"   {linha}")
                        elif 'noticias' in linha and '[{' in linha:
                            # Parse das notícias do JSON
                            try:
                                import ast
                                noticias_str = linha.split(': ', 1)[1]
                                noticias = ast.literal_eval(noticias_str)
                                
                                print(f"   📊 {len(noticias)} notícias detectadas:")
                                for j, noticia in enumerate(noticias[:3], 1):  # Mostrar só 3
                                    print(f"      {j}. {noticia['titulo'][:60]}...")
                                    print(f"         📰 {noticia['fonte']} | 🏷️ {noticia['categoria']} | 📈 Score: {noticia['score']}")
                                
                                if len(noticias) > 3:
                                    print(f"      ... e mais {len(noticias) - 3} notícias")
                            except:
                                print(f"   {linha}")
    
    print("\n" + "=" * 50)
    print("💡 PRÓXIMOS PASSOS:")
    print("• Para gerar roteiro: python ia_system/automation/pipeline.py")
    print("• Para monitorar contínuo: python monitorar.py")
    print("• Para configurar Discord: python configurar_notificacoes.py")

if __name__ == "__main__":
    main()