"""
Módulo para gerar notícias simuladas sobre criptomoedas para testes.
"""
from datetime import datetime

def get_mock_news():
    """
    Gera notícias fictícias para testes quando as APIs reais falham.
    
    Returns:
        list: Lista de notícias fictícias.
    """
    mock_news = [
        {
            "title": "Bitcoin atinge novo recorde histórico ultrapassando US$ 100.000",
            "url": "https://exemplo.com/bitcoin-recorde",
            "source": "Notícias Simuladas",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "title": "Ethereum 2.0 completa transição para Proof of Stake com sucesso",
            "url": "https://exemplo.com/ethereum-pos",
            "source": "Notícias Simuladas",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "title": "Brasil regulamenta uso de criptomoedas para pagamentos no varejo",
            "url": "https://exemplo.com/brasil-cripto-regulacao",
            "source": "Notícias Simuladas",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "title": "Binance lança nova plataforma de NFTs focada em artistas brasileiros",
            "url": "https://exemplo.com/binance-nft-brasil",
            "source": "Notícias Simuladas",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "title": "Cardano implementa smart contracts para DeFi com foco em sustentabilidade",
            "url": "https://exemplo.com/cardano-defi",
            "source": "Notícias Simuladas",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "title": "Banco Central do Brasil anuncia testes com CBDC nacional",
            "url": "https://exemplo.com/bc-cbdc-brasil",
            "source": "Notícias Simuladas",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "title": "Solana supera Ethereum em número de transações diárias",
            "url": "https://exemplo.com/solana-ethereum-transacoes",
            "source": "Notícias Simuladas",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "title": "Grandes empresas brasileiras adotam Bitcoin como reserva de valor",
            "url": "https://exemplo.com/empresas-bitcoin-brasil",
            "source": "Notícias Simuladas",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "title": "Novo projeto de lei pode reduzir impostos para mineradores de criptomoedas",
            "url": "https://exemplo.com/lei-mineracao-cripto",
            "source": "Notícias Simuladas",
            "date": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "title": "Pesquisa revela que 30% dos brasileiros já possuem alguma criptomoeda",
            "url": "https://exemplo.com/pesquisa-adocao-cripto",
            "source": "Notícias Simuladas",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    ]
    return mock_news

if __name__ == "__main__":
    news = get_mock_news()
    for i, item in enumerate(news, 1):
        print(f"{i}. {item['title']} - {item['source']}")
