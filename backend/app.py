import os
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
from chatbot import analisar_sentimento, gerar_resposta_contextualizada
from spotify_integration import obter_spotify_client, criar_playlist_contextualizada

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  
CORS(app, supports_credentials=True)

sp = obter_spotify_client()

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('mensagem', '').strip()
        current_step = data.get('etapa', 'inicio')

        
        if current_step == 'inicio' or 'etapa' not in session:
            session.clear()
            session['etapa'] = 'nome'
            return jsonify({
                'pergunta': "👋 Olá! Qual é o seu nome?",
                'etapa': 'nome'
            })

      
        if session['etapa'] == 'nome':
            if not user_message:
                return jsonify({'error': 'Nome não pode ser vazio'}), 400
                
            session['nome'] = user_message
            session['etapa'] = 'humor' 
            return jsonify({
                'pergunta': f"Prazer, {user_message}! 😊 Como está se sentindo hoje?",
                'etapa': 'humor'
            })

        elif session['etapa'] == 'humor':
            if not user_message:
                return jsonify({'error': 'Descreva seu humor'}), 400
                
            session['humor'] = analisar_sentimento(user_message)
            session['etapa'] = 'dia'  
            return jsonify({
                'pergunta': "Agora conte-me como foi seu dia:",
                'etapa': 'dia'
            })

        elif session['etapa'] == 'dia':
            if not user_message:
                return jsonify({'error': 'Descreva seu dia'}), 400

            session['descricao_dia'] = user_message
            resposta, playlist_data = criar_playlist_contextualizada(sp, session)
            
            session['etapa'] = 'final'
            return jsonify({
                'pergunta': resposta,
                'playlist': playlist_data,
                'etapa': 'final'
            })

        return jsonify({'error': 'Etapa inválida'}), 400

    except Exception as e:
        print(f"ERRO: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)