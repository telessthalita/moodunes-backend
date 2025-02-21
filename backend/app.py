import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from flasgger import Swagger
from chatbot import analisar_sentimento, gerar_resposta_contextualizada
from spotify_integration import obter_spotify_client, criar_playlist_contextualizada
from flask_session import Session 

load_dotenv()
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"  
Session(app)

CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
Swagger(app)

sp = obter_spotify_client()

@app.route("/")
def home():
    return "API está rodando!"

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Interage com o chatbot para gerar uma playlist baseada no humor do usuário.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            mensagem:
              type: string
              description: Mensagem do usuário
              example: "Estou muito feliz hoje!"
            etapa:
              type: string
              description: Etapa atual da conversa
              example: "humor"
    responses:
      200:
        description: Resposta do chatbot com pergunta e possível playlist
        schema:
          type: object
          properties:
            pergunta:
              type: string
              example: "Que incrível! Vou preparar uma playlist animada!"
            playlist:
              type: object
              example: { "id": "12345", "link": "https://open.spotify.com/playlist/12345" }
            etapa:
              type: string
              example: "final"
      400:
        description: Erro de requisição inválida
      500:
        description: Erro interno do servidor
    """
    try:
        data = request.get_json()
        user_message = data.get('mensagem', '').strip()
        current_step = data.get('etapa', 'inicio')

        if current_step == 'inicio' or 'etapa' not in session:
            session.clear()
            session['etapa'] = 'nome'
            return jsonify({'pergunta': "👋 Olá! Qual é o seu nome?", 'etapa': 'nome'})

        if session['etapa'] == 'nome':
            if not user_message:
                return jsonify({'error': 'Nome não pode ser vazio'}), 400

            session['nome'] = user_message
            session['etapa'] = 'humor'
            return jsonify({'pergunta': f"Prazer, {user_message}! 😊 Como está se sentindo hoje?", 'etapa': 'humor'})

        if session['etapa'] == 'humor':
            if not user_message:
                return jsonify({'error': 'Descreva seu humor'}), 400

            session['humor'] = analisar_sentimento(user_message)
            session['etapa'] = 'dia'
            return jsonify({'pergunta': "Agora conte-me como foi seu dia:", 'etapa': 'dia'})

        if session['etapa'] == 'dia':
            if not user_message:
                return jsonify({'error': 'Descreva seu dia'}), 400

            session['descricao_dia'] = user_message
            resposta = gerar_resposta_contextualizada(session)
            resposta_playlist, playlist_data = criar_playlist_contextualizada(sp, session)

            session['etapa'] = 'final'
            return jsonify({'pergunta': resposta, 'playlist': playlist_data, 'etapa': 'final'})

        return jsonify({'error': 'Etapa inválida'}), 400

    except Exception as e:
        print(f"ERRO: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
