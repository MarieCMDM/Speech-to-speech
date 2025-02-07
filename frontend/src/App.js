import React, { useState, useRef } from "react";
import axios from "axios";

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState("");
  const [audioSrc, setAudioSrc] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunks = useRef([]);
  let recordingState = false

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    mediaRecorderRef.current = new MediaRecorder(stream);
    mediaRecorderRef.current.ondataavailable = handleDataAvailable;
    mediaRecorderRef.current.onstop = handleStopRecording;
    mediaRecorderRef.current.start(1000);
    setIsRecording(true);
    recordingState = true;
  };

  const handleDataAvailable = async (event) => {
    console.log(recordingState, event.data)
    if (event.data.size > 0 && recordingState) {
      audioChunks.current.push(event.data);
      const blob = new Blob(audioChunks.current, { type: "audio/ogg; codecs=opus" });
      const formData = new FormData();
      formData.append("audio", blob, "audio.webm");

      try {
        const response = await axios.post("http://192.168.15.19:5000/transcribe", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        setTranscription((prev) => response.data.text);
      } catch (error) {
        console.error("Error sending audio chunk:", error);
      }
    }
  };

  const handleStopRecording = async () => {
    recordingState = false;
    const blob = new Blob(audioChunks.current, { type: "audio/ogg; codecs=opus" });
    const audioUrl = URL.createObjectURL(blob);
    setAudioSrc(audioUrl);

    const formData = new FormData();
    formData.append("audio", blob, "final_audio.wav");

    try {
      const response = await axios.post("http://192.168.15.19:5000/finish", formData, {
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
