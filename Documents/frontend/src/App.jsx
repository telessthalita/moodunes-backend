import { useState } from "react";
import ChatInterface from "./components/ChatInterface";
import MusicParticles from './components/MusicParticles';


function App() {
  const [playlist, setPlaylist] = useState(null);

  return (
    <div className="App">
      
      <div className="content-wrapper">
        
        <header>
          <h1> MoodTunes</h1>
        </header>
        <div className="main-container">
          <ChatInterface onPlaylistCreated={setPlaylist} />
        </div>
        <MusicParticles />
      </div>
    </div>
  );
}

export default App;