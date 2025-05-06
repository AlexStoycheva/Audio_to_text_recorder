let mediaRecorder;
let audioChunks = [];
  
document.getElementById("startBtn").onclick = async () => {
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
mediaRecorder = new MediaRecorder(stream);

mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    audioChunks = [];

    const formData = new FormData();
    formData.append("file", audioBlob, "speech.wav");

    const response = await fetch("/recognize", {
    method: "POST",
    body: formData,
    });

    const data = await response.json();
    document.getElementById("result").textContent = data.text || "No speech detected.";
};

mediaRecorder.start();
};

document.getElementById("stopBtn").onclick = () => {
mediaRecorder.stop();
};