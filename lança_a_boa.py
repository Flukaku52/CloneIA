#!/usr/bin/env python3
"""
🚀 LANÇA A BOA - Varredura inteligente de notícias cripto
Comando: python lança_a_boa.py
"""
import os
import json
from datetime import datetime, timedelta
from ia_system.core.news_collector import NewsCollector

def main():
    print("🚀 LANÇA A BOA - VARREDURA DE NOTÍCIAS")
    print("=" * 60)
    
    # Verificar timestamp da última varredura
    timestamp_file = "ia_system/cache/ultima_varredura.json"
    os.makedirs(os.path.dirname(timestamp_file), exist_ok=True)
    
    agora = datetime.now()
    
    if os.path.exists(timestamp_file):
        with open(timestamp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            ultima_varredura = datetime.fromisoformat(data['ultima_varredura'])
            tempo_desde = agora - ultima_varredura
            
        print(f"⏰ Última varredura: {ultima_varredura.strftime('%d/%m/%Y %H:%M')}")
        print(f"🕒 Tempo decorrido: {tempo_desde}")
    else:
        print("🆕 Primeira varredura!")
        ultima_varredura = agora - timedelta(hours=24)  # Buscar últimas 24h na primeira vez
    
    print(f"🔍 Buscando notícias desde {ultima_varredura.strftime('%d/%m/%Y %H:%M')}...")
    print("-" * 60)
    
    # Coletar notícias
    collector = NewsCollector()
    noticias = collector.obter_noticias_para_roteiro()
    
    if not noticias:
        print("📭 Nenhuma notícia nova encontrada")
        print("💡 Tente novamente em algumas horas!")
        return
    
    # Filtrar por data (só notícias desde última varredura)
    noticias_novas = []
    for noticia in noticias:
        if noticia.data_publicacao > ultima_varredura:
            noticias_novas.append(noticia)
    
    if not noticias_novas:
        print("📰 Todas as notícias já foram analisadas na última varredura")
        print("💡 Aguarde novas notícias surgirem!")
        return
    
    print(f"🎯 ENCONTRADAS {len(noticias_novas)} NOTÍCIAS NOVAS:")
    print("=" * 60)
    
    # Classificar por prioridade
    alta_prioridade = [n for n in noticias_novas if n.relevancia_score >= 60]
    media_prioridade = [n for n in noticias_novas if 40 <= n.relevancia_score < 60]
    baixa_prioridade = [n for n in noticias_novas if n.relevancia_score < 40]
    
    # Mostrar notícias organizadas por prioridade
    if alta_prioridade:
        print(f"\n🔥 ALTA PRIORIDADE ({len(alta_prioridade)} notícias):")
        print("-" * 40)
        for i, noticia in enumerate(alta_prioridade, 1):
            print(f"\n{i}. 🔥 {noticia.titulo}")
            print(f"   📰 {noticia.fonte}")
            print(f"   🏷️ {', '.join(noticia.categorias)}")
            print(f"   📊 Score: {noticia.relevancia_score}")
            print(f"   📅 {noticia.data_publicacao.strftime('%d/%m %H:%M')}")
            preview = noticia.conteudo[:150] + "..." if len(noticia.conteudo) > 150 else noticia.conteudo
            print(f"   📝 {preview}")
    
    if media_prioridade:
        print(f"\n📈 MÉDIA PRIORIDADE ({len(media_prioridade)} notícias):")
        print("-" * 40)
        for i, noticia in enumerate(media_prioridade, 1):
            print(f"\n{i}. 📈 {noticia.titulo}")
            print(f"   📰 {noticia.fonte} | 📊 {noticia.relevancia_score} | 📅 {noticia.data_publicacao.strftime('%d/%m %H:%M')}")
            preview = noticia.conteudo[:100] + "..." if len(noticia.conteudo) > 100 else noticia.conteudo
            print(f"   📝 {preview}")
    
    if baixa_prioridade:
        print(f"\n📊 BAIXA PRIORIDADE ({len(baixa_prioridade)} notícias):")
        print("-" * 40)
        for i, noticia in enumerate(baixa_prioridade, 1):
            print(f"{i}. 📊 {noticia.titulo[:60]}...")
            print(f"   📰 {noticia.fonte} | 📊 {noticia.relevancia_score}")
    
    # Análise rápida
    print(f"\n" + "=" * 60)
    print("📊 ANÁLISE RÁPIDA:")
    
    # Contagem por categoria
    categorias = {}
    for noticia in noticias_novas:
        for cat in noticia.categorias:
            categorias[cat] = categorias.get(cat, 0) + 1
    
    if categorias:
        print("🏷️ Por categoria:")
        for categoria, count in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {categoria}: {count}")
    
    # Contagem por fonte
    fontes = {}
    for noticia in noticias_novas:
        fonte_limpa = noticia.fonte.split(' - ')[0]  # Remove detalhes após -
        fontes[fonte_limpa] = fontes.get(fonte_limpa, 0) + 1
    
    if fontes:
        print("📰 Por fonte:")
        for fonte, count in sorted(fontes.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {fonte}: {count}")
    
    # Recomendações
    print(f"\n💡 RECOMENDAÇÕES:")
    if len(alta_prioridade) >= 2:
        print("✅ Tem material suficiente para um reel completo!")
        print("🎬 Recomendo usar as notícias de ALTA PRIORIDADE")
    elif len(alta_prioridade) + len(media_prioridade) >= 2:
        print("⚠️ Combine ALTA + MÉDIA prioridade para um reel")
    else:
        print("⏳ Aguarde mais notícias ou use uma notícia + análise mais aprofundada")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print("• Para gerar roteiro completo: python ia_system/core/script_generator.py")
    print("• Para excluir notícias: python excluir_noticias.py")
    print("• Para monitorar contínuo: python monitorar.py")
    
    # Salvar timestamp desta varredura
    with open(timestamp_file, 'w', encoding='utf-8') as f:
        json.dump({
            'ultima_varredura': agora.isoformat(),
            'noticias_encontradas': len(noticias_novas),
            'alta_prioridade': len(alta_prioridade),
            'media_prioridade': len(media_prioridade)
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n⏰ Timestamp salvo para próxima varredura: {agora.strftime('%d/%m/%Y %H:%M')}")

if __name__ == "__main__":
    main()