import random
from textblob import TextBlob
import json

def analisar_sentimento(texto):
    texto = texto.lower()
    blob = TextBlob(texto)

    keywords = {
        'feliz': ['feliz', 'alegre', 'ótimo', 'maravilhoso', 'animado', 'sorrindo', 'bom', 'divertido'],
        'triste': ['triste', 'péssimo', 'horrível', 'deprimido', 'chateado', 'chorando', 'mal', 'cansado'],
        'neutro': ['normal', 'ok', 'tranquilo', 'indiferente', 'meh', 'tanto faz', 'neutro']
    }

    for mood, words in keywords.items():
        if any(word in texto.split() for word in words):  # Verifica palavra exata
            return mood

    polarity = blob.sentiment.polarity
    if polarity > 0.2:
        return 'feliz'
    elif polarity < -0.2:
        return 'triste'
    return 'neutro'


def gerar_resposta_contextualizada(session):
    nome = session.get('nome', 'Amigo')
    humor = session['humor']
    dia = session['descricao_dia']
    
    respostas = {
        'feliz': [
            f"Que incrível, {nome}! 😄 Vou preparar uma playlist energética para combinar com seu dia: {dia}",
            f"{dia} parece ter sido incrível! 💥 Sua playlist positiva está a caminho"
        ],
        'triste': [
            f"Sinto muito pelo seu dia, {nome}. 😢 Vou selecionar músicas para te confortar...",
            f"Todo dia difícil merece uma trilha sonora especial. 🎧 Sua playlist de consolo:"
        ],
        'neutro': [
            f"Vamos dar um toque especial ao seu dia {humor}, {nome}! 🌟 Playlist em construção...",
            f"Dias {humor} pedem músicas equilibradas. 🎶 Sua seleção:"
        ]
    }
    
    return random.choice(respostas[humor])

def carregar_historico():
    try:
        with open('historico.json') as f:
            return json.load(f)
    except:
        return {}

def salvar_interacao(usuario, dados):
    historico = carregar_historico()
    historico.setdefault(usuario, []).append(dados)
    with open('historico.json', 'w') as f:
        json.dump(historico, f)
