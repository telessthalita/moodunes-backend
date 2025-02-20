import os
import spotipy
import random
from spotipy.oauth2 import SpotifyOAuth
from chatbot import carregar_historico, salvar_interacao  

def obter_spotify_client():
    """Retorna o cliente autenticado do Spotify"""
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri='http://localhost:8888/callback',
        scope='playlist-modify-public',
        cache_path='.spotify_cache'
    ))

def criar_playlist_contextualizada(sp, session):
    """Cria playlist baseada no contexto da conversa"""
    try:

        params_map = {
            'feliz': {
                'genres': ['pop', 'dance'],
                'keywords': 'mood:happy'
            },
            'triste': {
                'genres': ['indie', 'acoustic'],
                'keywords': 'mood:sad'
            },
            'neutro': {
                'genres': ['lofi', 'ambient'],
                'keywords': 'mood:calm'
            }
        }
        
        params = params_map.get(session['humor'], params_map['neutro'])
        query = f"{random.choice(['happy', 'sad', 'chill', 'party'])} {random.choice(params['genres'])}"



        results = sp.search(
            q=query,
            limit=15,
            type='track',
            market='BR'
        )


        if not results['tracks']['items']:
            raise Exception("Nenhuma música encontrada para os parâmetros atuais")


        tracks = []
        for track in results['tracks']['items']:
            tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'url': track['external_urls']['spotify']
            })
            if len(tracks) >= 5:
                break


        if not tracks:
            raise Exception("Nenhuma música válida encontrada")


        playlist = sp.user_playlist_create(
            user=sp.me()['id'],
            name=f"PlayList criada pelo MoodTunes: {session['nome']} - {session['humor']}",
            description=f"Baseado em: {session['descricao_dia']}",
            public=True
        )

        track_ids = [t['id'] for t in tracks]
        sp.playlist_add_items(playlist['id'], track_ids)
        
        return (
            "🎵 Playlist criada com sucesso!",
            {
                'link': playlist['external_urls']['spotify'],
                'tracks': tracks
            }
        )

    except Exception as e:
        print(f"Erro no Spotify: {str(e)}")
        return (
            f"😥 Não consegui criar a playlist: {str(e)}",
            None
        )