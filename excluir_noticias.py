#!/usr/bin/env python3
"""
Script para excluir notícias já abordadas.
"""
import os
import json
from datetime import datetime

def main():
    print("🗑️ EXCLUIR NOTÍCIAS JÁ ABORDADAS")
    print("=" * 50)
    
    # Carregar lista de notícias excluídas
    excluded_file = "ia_system/cache/noticias_excluidas.json"
    os.makedirs(os.path.dirname(excluded_file), exist_ok=True)
    
    if os.path.exists(excluded_file):
        with open(excluded_file, 'r', encoding='utf-8') as f:
            excluded_data = json.load(f)
    else:
        excluded_data = {"noticias_excluidas": [], "ultima_atualizacao": None}
    
    # Palavras-chave das notícias que você quer excluir
    noticias_para_excluir = [
        "drex",
        "microstrategy", 
        "blockchain",
        "projeto de lei",
        "banco central",
        "congress blockchain",
        "registro empresas"
    ]
    
    print("📝 Adicionando à lista de exclusão:")
    
    for palavra_chave in noticias_para_excluir:
        if palavra_chave not in excluded_data["noticias_excluidas"]:
            excluded_data["noticias_excluidas"].append(palavra_chave)
            print(f"✅ Excluído: {palavra_chave}")
        else:
            print(f"⚠️ Já excluído: {palavra_chave}")
    
    # Salvar lista atualizada
    excluded_data["ultima_atualizacao"] = datetime.now().isoformat()
    
    with open(excluded_file, 'w', encoding='utf-8') as f:
        json.dump(excluded_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Lista salva em: {excluded_file}")
    print(f"📊 Total de exclusões: {len(excluded_data['noticias_excluidas'])}")
    
    print("\n🔄 TESTANDO FILTRO...")
    
    # Testar com as últimas notícias
    from ia_system.core.news_collector import NewsCollector
    collector = NewsCollector()
    noticias = collector.obter_noticias_para_roteiro()
    
    print(f"\n📰 NOTÍCIAS ANTES DO FILTRO: {len(noticias)}")
    
    # Aplicar filtro
    noticias_filtradas = filtrar_noticias_excluidas(noticias, excluded_data["noticias_excluidas"])
    
    print(f"📰 NOTÍCIAS APÓS FILTRO: {len(noticias_filtradas)}")
    print(f"🗑️ REMOVIDAS: {len(noticias) - len(noticias_filtradas)}")
    
    if noticias_filtradas:
        print(f"\n✅ NOTÍCIAS RESTANTES:")
        for i, noticia in enumerate(noticias_filtradas[:5], 1):
            print(f"{i}. {noticia.titulo[:80]}...")
            print(f"   📰 {noticia.fonte} | 📊 Score: {noticia.relevancia_score}")
    
    print(f"\n💡 DICA: O sistema agora filtrará automaticamente essas notícias!")

def filtrar_noticias_excluidas(noticias, palavras_excluidas):
    """
    Filtra notícias baseado em palavras-chave excluídas.
    
    Args:
        noticias: Lista de notícias
        palavras_excluidas: Lista de palavras-chave para excluir
        
    Returns:
        Lista de notícias filtradas
    """
    noticias_filtradas = []
    
    for noticia in noticias:
        # Verificar se alguma palavra excluída está no título ou conteúdo
        texto_completo = f"{noticia.titulo} {noticia.conteudo}".lower()
        
        deve_excluir = False
        for palavra in palavras_excluidas:
            if palavra.lower() in texto_completo:
                print(f"🗑️ Excluindo: {noticia.titulo[:60]}... (palavra: {palavra})")
                deve_excluir = True
                break
        
        if not deve_excluir:
            noticias_filtradas.append(noticia)
    
    return noticias_filtradas

if __name__ == "__main__":
    main()