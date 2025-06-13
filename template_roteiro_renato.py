#!/usr/bin/env python3
"""
Template para gerar roteiros no estilo Renato
Baseado no aprendizado do processo anterior
"""

def gerar_template_roteiro(tema, noticias):
    """
    Gera roteiro seguindo o padrão aprendido
    
    Args:
        tema (str): Tema principal do reel
        noticias (list): Lista de notícias para abordar
    """
    
    # ABERTURA PADRÃO (sempre igual)
    abertura = "E aí cambada! Olha eu aí de novo. Bora pras novas!"
    
    # SEGMENTOS DE NOTÍCIAS (2-3 notícias)
    segmentos = []
    
    for i, noticia in enumerate(noticias[:3], 1):
        if 'governo' in noticia.lower() or 'proib' in noticia.lower():
            # Notícia de crítica governamental
            segmento = f"""
{noticia}

Enquanto isso, [contraponto positivo].

Quando o governo corre pra proibir um tipo de dinheiro, é porque ele não quer perder o controle sobre como você transaciona.

Curioso.

Para o Drex, por exemplo, ninguém reclama. Mas pra uma moeda descentralizada que você controla? Aí já vira perigo!
"""
        
        elif 'dados' in noticia.lower() or '%' in noticia:
            # Notícia com estatísticas
            segmento = f"""
Olha esse dado que pouca gente sabe: {noticia}

Pra você ter uma ideia, isso é mais do que: [comparações].

Ou seja: [interpretação dos dados].

A tendência é clara: cada vez mais gente tá buscando alternativas fora do sistema financeiro tradicional.

E isso, querendo ou não, é um movimento que combina muito com a proposta das criptos: dar mais autonomia pro cidadão sobre o próprio dinheiro.
"""
        
        elif 'bitcoin' in noticia.lower() or 'btc' in noticia.lower():
            # Notícia sobre Bitcoin/preço
            segmento = f"""
E agora falando de preço, {noticia}

Isso mostra que não é só hype de gráfico. O BTC já tem consistência pra se manter em patamares altos, apontando pra maturidade e confiança.

Enquanto governos tentam segurar ou proibir, o mercado segue validando uma moeda que não depende de bancos centrais.
"""
        
        else:
            # Template genérico
            segmento = f"""
{noticia}

[Análise crítica da notícia]

[Conexão com filosofia cripto]

Querendo ou não, [reflexão sobre o impacto].
"""
        
        segmentos.append(segmento.strip())
    
    # FECHAMENTO PADRÃO
    fechamento = f"""
Por hoje é isso cambada.

[Resumo das principais notícias].

[Reflexão final sobre o tema].



Sigo de olho.
"""
    
    # ROTEIRO COMPLETO
    roteiro_completo = {
        "titulo": f"Rapidinha no Cripto - {tema}",
        "segmentos": {
            "01_abertura": abertura,
            **{f"0{i+1}_{tipo}": segmento for i, (tipo, segmento) in enumerate([
                ("noticia_principal", segmentos[0] if segmentos else ""),
                ("noticia_secundaria", segmentos[1] if len(segmentos) > 1 else ""),
                ("noticia_terciaria", segmentos[2] if len(segmentos) > 2 else "")
            ]) if segmento},
            f"0{len(segmentos)+2}_fechamento": fechamento
        },
        "configuracoes": {
            "voice_id": "25NR0sM9ehsgXaoknsxO",
            "avatar_id": "3034bbd37f2540ddb70c90c7f67b4f5c",
            "formato": "9:16",
            "background": "#000000"
        },
        "caracteristicas_linguisticas": {
            "expressoes_marca": ["cambada", "bora", "sigo de olho", "querendo ou não", "olha esse dado"],
            "tom_geral": "libertário, crítico ao controle estatal, otimista com cripto",
            "pausas_dramaticas": ["Curioso.", "Sigo de olho."],
            "numeros_por_extenso": True
        }
    }
    
    return roteiro_completo

def exemplo_uso():
    """Exemplo de como usar o template"""
    
    tema = "Regulação vs Adoção"
    
    noticias = [
        "O estado de Conecticut aprovou uma lei que impede o governo estadual e prefeituras de comprar, manter ou investir em criptomoedas.",
        "Quinze por cento dos brasileiros já investiram em criptomoedas, mais do que em dólar, renda fixa, ouro e ações.",
        "O Bitcoin passou trinta dias seguidos acima de cem mil dólares, algo inédito no mercado."
    ]
    
    roteiro = gerar_template_roteiro(tema, noticias)
    
    print("🎬 ROTEIRO GERADO:")
    print("=" * 60)
    print(f"📰 {roteiro['titulo']}")
    print()
    
    for nome_segmento, texto in roteiro['segmentos'].items():
        print(f"[{nome_segmento.upper()}]")
        print(texto)
        print("-" * 40)
    
    return roteiro

if __name__ == "__main__":
    roteiro_exemplo = exemplo_uso()
    
    print("\n✅ TEMPLATE PRONTO!")
    print("Use este padrão para manter consistência nos próximos reels.")