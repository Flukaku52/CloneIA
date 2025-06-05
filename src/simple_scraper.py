"""
Versão simplificada do scraper para demonstração.
"""
import json
import os
from datetime import datetime
from mock_news import get_mock_news

def save_mock_news():
    """
    Salva notícias simuladas em um arquivo JSON.
    """
    # Obter notícias simuladas
    news = get_mock_news()
    
    # Criar diretório de dados se não existir
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Nome do arquivo
    filename = os.path.join(data_dir, f"crypto_news_{datetime.now().strftime('%Y%m%d')}.json")
    
    # Salvar em JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=4)
    
    print(f"Notícias simuladas salvas em {filename}")
    print(f"Total de {len(news)} notícias geradas.")
    
    return news

if __name__ == "__main__":
    save_mock_news()
