import React, { useState, useEffect, useRef } from 'react';
import { ChatService } from '../services/api';
import '../index.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [step, setStep] = useState('inicio');
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
    if (step === 'inicio' && messages.length === 0) {
      initChat();
    }
  }, [messages]);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const initChat = async () => {
    try {
      if (!ChatService || typeof ChatService.initChat !== 'function') {
        throw new Error('Configuração do serviço de chat inválida');
      }

      if (!navigator.onLine) {
        throw new Error('Sem conexão com a internet');
      }

      const data = await ChatService.initChat();

      if (!data?.pergunta || !data?.etapa) {
        throw new Error('Resposta do servidor inválida');
      }

      setMessages([{ 
        text: data.pergunta, 
        isBot: true,
        playlist: data.playlist 
      }]);
      setStep(data.etapa);

    } catch (error) {
      console.error('Erro:', error);
      const errorMessage = error.message.includes('servidor') 
        ? error.message 
        : 'Erro na comunicação com o serviço';

      setMessages(prev => [...prev, { 
        text: `⚠️ ${errorMessage}`, 
        isBot: true 
      }]);
    }
  };

  const resetChat = () => {
    setMessages([]);
    setInputText('');
    setStep('inicio');
    setIsLoading(false);
    initChat(); // Reinicia o chat
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    setMessages(prev => [...prev, { text: inputText, isBot: false }]);
    setIsLoading(true);
    setInputText('');

    try {
      const data = await ChatService.sendMessage({
        mensagem: inputText,
        etapa: step
      });

      setMessages(prev => [
        ...prev, 
        { 
          text: data.pergunta, 
          isBot: true,
          playlist: data.playlist 
        }
      ]);
      setStep(data.etapa);

      
      if (data.playlist) {
        setTimeout(resetChat, 10000);
      }

    } catch (error) {
      console.error('Erro:', error);
      setMessages(prev => [
        ...prev, 
        { 
          text: `⚠️ ${error.message || 'Erro ao processar sua mensagem'}`, 
          isBot: true 
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-wrapper">
      <div className="chat-history">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.isBot ? 'bot' : 'user'}`}>
            <div className="bubble">
              {msg.text.split('\n').map((line, idx) => (
                <p key={idx}>{line}</p>
              ))}
              
              {msg.playlist && (
                <div className="playlist-box">
                  <a
                    href={msg.playlist.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="playlist-link"
                  >
                    🎧 Ouvir Playlist no Spotify
                  </a>
                  <div className="track-list">
                    {msg.playlist.tracks.map((track, idx) => (
                      <div key={`track-${idx}`} className="track-item">
                        <span className="track-number">{idx + 1}.</span>
                        <div className="track-info">
                          <p className="track-title">{track.name}</p>
                          <p className="track-artist">{track.artist}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      <form className="input-area" onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={getPlaceholderText(step)}
          disabled={isLoading}
          aria-label="Digite sua mensagem"
        />
        <button 
          type="submit" 
          disabled={isLoading}
          className={isLoading ? 'loading' : ''}
        >
          {isLoading ? (
            <div className="loader"></div>
          ) : (
            'Enviar'
          )}
        </button>
      </form>
    </div>
  );
};

const getPlaceholderText = (step) => {
  const placeholders = {
    nome: "Digite seu nome...",
    humor: "Como está se sentindo?",
    dia: "Descreva seu dia...",
    default: "Digite sua mensagem..."
  };
  return placeholders[step] || placeholders.default;
};

export default ChatInterface;
