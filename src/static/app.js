
let isRecording = false;
let token = '';
let audioSrc = null;
let mediaRecorder = null;
let audioChunks = [];
const audioPlayer = document.getElementById('audioPlayer');
const transcriptionTextarea = document.getElementById('transcription');
const answerTextarea = document.getElementById('answer');
const stopButton = document.getElementById('stopRecording');
const startButtonWrap = document.getElementById('startButtonWrap');
const recordButtonWrap = document.getElementById('recordButtonWrap');
const startButton = document.getElementById('startButton');
const recordButton = document.getElementById('recordButton');
const audioContainer = document.getElementById('audioContainer')

async function initRecorder() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = handleDataAvailable;
        mediaRecorder.onstop = handleStopRecording;

        transcriptionTextarea.value = '';
        answerTextarea.value = '';
        
        const response = await fetch(`/start`);
        const data = await response.json();
        token = data.token;

        startButtonWrap.style.display = 'none';
        recordButtonWrap.style.display = 'block';

    } catch (error) {
        console.error('Error during initialization:', error);
    }
}

async function startRecording() {
    transcriptionTextarea.value = '';
    mediaRecorder.start(1500);
    isRecording = true;  
    audioContainer.style.visibility = 'none';
    recordButton.style.backgroundColor = 'red';
}

function stopRecording() {
    mediaRecorder.stop();
    isRecording = false;
    answerTextarea.value = '';
    audioContainer.style.visibility = 'block';
    recordButton.style.backgroundColor = '';
}

async function handleDataAvailable(event) {
    if (event.data.size > 0) {
        audioChunks.push(event.data);
        const blob = new Blob(audioChunks, { type: 'audio/webm; codecs=opus' });
        const formData = new FormData();
        formData.append('audio', blob, 'audio.webm');
        formData.append('token', token);
        formData.append('language', 'it');

        try {
            const response = await fetch(`/transcribe`, {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            transcriptionTextarea.value = data.text;
        } catch (error) {
            console.error('Error sending audio chunk:', error);
        }
    }
}

async function handleStopRecording() {
    const formData = new FormData();
    formData.append('token', token);
    formData.append('language', 'it');

    try {
        const response = await fetch(`/finish`, {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        transcriptionTextarea.value = data.text;
        answerTextarea.value = data.answer;
        audioSrc = `/stream/${token}`;
        audioPlayer.src = audioSrc;
    } catch (error) {
        console.error('Error sending final audio:', error);
    }
}

audioPlayer.addEventListener('ended', () => {
    audioPlayer.src = `/stream/${token}?t=${Date.now()}`;
});