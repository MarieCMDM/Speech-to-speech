import React, { useState, useRef } from "react";
import axios from "axios";

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState("");
  const [audioSrc, setAudioSrc] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunks = useRef([]);

  // Funzione per iniziare la registrazione
  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    mediaRecorderRef.current = new MediaRecorder(stream);
    mediaRecorderRef.current.ondataavailable = handleDataAvailable;
    mediaRecorderRef.current.onstop = handleStopRecording;
    mediaRecorderRef.current.start();
    setIsRecording(true);
  };

  // Funzione per gestire i chunk di audio
  const handleDataAvailable = async (event) => {
    if (event.data.size > 0) {
      audioChunks.current.push(event.data);

      // Invia l'audio al backend per la trascrizione
      const formData = new FormData();
      formData.append("audio", event.data, "audio.wav");

      try {
        const response = await axios.post("http://localhost:5000/transcribe", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        setTranscription((prev) => prev + " " + response.data.text);
      } catch (error) {
        console.error("Error sending audio chunk:", error);
      }
    }
  };

  // Funzione per gestire la fine della registrazione
  const handleStopRecording = async () => {
    const blob = new Blob(audioChunks.current, { type: "audio/wav" });
    const audioUrl = URL.createObjectURL(blob);
    setAudioSrc(audioUrl);

    // Invia l'ultima parte dell'audio al backend
    const formData = new FormData();
    formData.append("audio", blob, "final_audio.wav");

    try {
      const response = await axios.post("http://localhost:5000/finish", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setTranscription((prev) => prev + " " + response.data.text);
      setAudioSrc(response.data.audioUrl);
    } catch (error) {
      console.error("Error sending final audio:", error);
    }

    setIsRecording(false);
    audioChunks.current = [];
  };

  return (
    <div className="App">
      <h1>Audio Recorder</h1>
      <textarea value={transcription} readOnly rows="10" cols="50" />
      <div>
        <button onClick={startRecording} disabled={isRecording}>
          Start Recording
        </button>
        <button onClick={handleStopRecording} disabled={!isRecording}>
          Stop Recording
        </button>
      </div>
      {audioSrc && (
        <div>
          <h2>Playback Audio</h2>
          <audio controls src={audioSrc}></audio>
        </div>
      )}
    </div>
  );
}

export default App;
