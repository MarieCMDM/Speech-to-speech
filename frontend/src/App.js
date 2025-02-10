import React, { useState, useRef } from "react";
import axios from "axios";
import "./App.css"

const base_url = ''

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState("");
  const [token, setToken] = useState("")
  const [answer, setAnswer] = useState("");
  const [audioSrc, setAudioSrc] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunks = useRef([]);
  let recordingState = false

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    mediaRecorderRef.current = new MediaRecorder(stream);
    mediaRecorderRef.current.ondataavailable = handleDataAvailable;
    mediaRecorderRef.current.onstop = handleStopRecording;

    try {
      const response = await axios.get(`${base_url}/s2s_bend/start`)
      setToken((prev) => response.data.token);
      console.log(token)
    } catch (error) {
      console.error("Error sending final audio:", error);
    }

    mediaRecorderRef.current.start(1500);
    setIsRecording(true);
    recordingState = true;
  };

  const stopRecording = async() => {
    console.log('Stop')
    recordingState = false;
    mediaRecorderRef.current.stop();
  }

  const handleDataAvailable = async (event) => {
    console.log('dataavaiable', recordingState, event.data)
    if (event.data.size > 0 && recordingState) {
      audioChunks.current.push(event.data);
      const blob = new Blob(audioChunks.current, { type: "audio/webm; codecs=opus" });
      const formData = new FormData();
      formData.append("audio", blob, "audio.webm");
      formData.append("token", token)

      try {
        const response = await axios.post(`${base_url}/s2s_bend/transcribe`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        setTranscription((prev) => response.data.text);
      } catch (error) {
        console.error("Error sending audio chunk:", error);
      }
    }
  };

  const handleStopRecording = async (event) => {
    console.log('Stopped', event.data)
    // const blob = new Blob(audioChunks.current, { type: "audio/webm; codecs=opus" });
    // const audioUrl = URL.createObjectURL(blob);
    // setAudioSrc(audioUrl);

    const formData = new FormData();
    formData.append("token", token)

    try {
      const response = await axios.post(`${base_url}/s2s_bend/finish`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setTranscription((prev) => response.data.text);
      setAnswer((prev) => response.data.answer);
      setAudioSrc(`${base_url}/s2s_bend/stream_audio/${token}`);
    } catch (error) {
      console.error("Error sending final audio:", error);
    }

    setIsRecording(false);
    audioChunks.current = [];
  };

  return (
    <div className="App">
      <h1>Speech to Speech Demo</h1>
      <div class="text_wrap"> Here the real-time text to speeech</div>
      <textarea value={transcription} readOnly rows="10" cols="50" placeholder="Transcribed text"/>
      <div>
        <div class="bts_wrap">
            <button onClick={startRecording} disabled={isRecording}>
              Start Recording
            </button>
          </div>
          <div class="bts_wrap">
            <button onClick={stopRecording} disabled={!isRecording}>
              Stop Recording
          </button>
        </div>
      </div>
      <div class="text_wrap"> Here the text response </div>
      <textarea value={answer} readOnly rows="10" cols="50" placeholder="Answer text"/>
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
