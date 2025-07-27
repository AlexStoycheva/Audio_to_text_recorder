let mediaRecorder;
let intervalId;
let audioChunks = [];
const transcriptDiv = document.getElementById("transcript");

document.getElementById("startBtn").onclick = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);

  mediaRecorder.ondataavailable = e => {
    audioChunks.push(e.data);
  };

  mediaRecorder.onstop = async () => {
    const blob = new Blob(audioChunks, { type: 'audio/wav' });
    
    audioChunks = [];

    const formData = new FormData();
    formData.append("file", blob, "chunk.wav");

    const response = await fetch("/recognize/chunk", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    if (data.text) {
      transcriptDiv.textContent += data.text + " ";
    }
  };

  mediaRecorder.start();
  intervalId = setInterval(() => {
    mediaRecorder.stop();
    mediaRecorder.start();
  }, 3000);
};

document.getElementById("stopBtn").onclick = () => {
  clearInterval(intervalId);
  mediaRecorder.stop();
};

document.getElementById("uploadForm").onsubmit = async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById("fileInput");
  if (!fileInput.files.length) return;

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const response = await fetch("/recognize/upload", {
    method: "POST",
    body: formData
  });

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "transcription.txt";
  a.click();
};
