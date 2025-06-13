#!/usr/bin/env python3
"""
Script para ver rapidamente as últimas notícias detectadas.
"""
from ia_system.core.news_collector import NewsCollector

def main():
    print("📰 ÚLTIMAS NOTÍCIAS DETECTADAS")
    print("=" * 60)
    
    collector = NewsCollector()
    noticias = collector.obter_noticias_para_roteiro()
    
    if not noticias:
        print("📭 Nenhuma notícia encontrada")
        return
    
    print(f"🎯 ENCONTRADAS {len(noticias)} NOTÍCIAS VERIFICADAS:")
    print("-" * 60)
    
    for i, noticia in enumerate(noticias[:8], 1):
        # Indicador de prioridade
        if noticia.relevancia_score >= 60:
            prioridade = "🔥 ALTA"
        elif noticia.relevancia_score >= 40:
            prioridade = "📈 MÉDIA"
        else:
            prioridade = "📊 BAIXA"
        
        print(f"\n{i}. {noticia.titulo}")
        print(f"   📰 Fonte: {noticia.fonte}")
        print(f"   🏷️ Categoria: {', '.join(noticia.categorias)}")
        print(f"   📊 Score: {noticia.relevancia_score} ({prioridade})")
        print(f"   📅 Data: {noticia.data_publicacao.strftime('%d/%m/%Y %H:%M')}")
        
        # Prévia do conteúdo
        preview = noticia.conteudo[:120] + "..." if len(noticia.conteudo) > 120 else noticia.conteudo
        print(f"   📝 Prévia: {preview}")
    
    # Contagem por categoria
    categorias = {}
    for noticia in noticias:
        for cat in noticia.categorias:
            categorias[cat] = categorias.get(cat, 0) + 1
    
    print(f"\n" + "=" * 60)
    print("📊 RESUMO POR CATEGORIA:")
    for categoria, count in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
        print(f"• {categoria}: {count} notícia(s)")
    
    print(f"\n💡 DICAS:")
    print("• Para gerar roteiro automaticamente: python ia_system/core/script_generator.py")
    print("• Para pipeline completo (áudio+vídeo): python ia_system/automation/pipeline.py")
    print("• Para monitorar continuamente: python monitorar.py")

if __name__ == "__main__":
    main()