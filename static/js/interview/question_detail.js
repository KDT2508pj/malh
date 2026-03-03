let timerInterval = null;
let seconds = 0;
let mediaRecorder = null;
let mediaStream = null;
let recordedChunks = [];
let isRecording = false;
let audioContext = null;
let analyserNode = null;
let sourceNode = null;
let animationFrameId = null;
let frequencyData = null;
let smoothedLevels = [];

const interviewContext = window.INTERVIEW_CONTEXT || {};
const sessionId = Number(interviewContext.sessionId || 0);
const selId = Number(interviewContext.selId || 0);

function startTimer() {
    const $timerElement = $("#timer");
    seconds = 0;
    $timerElement.text("00:00");

    timerInterval = setInterval(() => {
        seconds += 1;
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        $timerElement.text(
            `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`,
        );
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function pickSupportedMimeType() {
    const candidates = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4"];
    for (const mimeType of candidates) {
        if (window.MediaRecorder && MediaRecorder.isTypeSupported(mimeType)) {
            return mimeType;
        }
    }
    return "";
}

async function uploadRecordedAudio(blob) {
    const ext = blob.type.includes("mp4") ? "m4a" : "webm";
    const fileName = `answer.${ext}`;
    const file = new File([blob], fileName, { type: blob.type || "audio/webm" });

    const formData = new FormData();
    formData.append("audio_file", file);
    formData.append("duration_sec", String(seconds));

    const response = await fetch(
        `/api/interviews/${sessionId}/questions/${selId}/recordings`,
        {
            method: "POST",
            body: formData,
        },
    );

    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        const message = data.detail || "Recording upload failed.";
        throw new Error(message);
    }

    return response.json();
}

function cleanupStream() {
    if (mediaStream) {
        mediaStream.getTracks().forEach((track) => track.stop());
        mediaStream = null;
    }
}

function stopVisualizer() {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
    }
    if (sourceNode) {
        sourceNode.disconnect();
        sourceNode = null;
    }
    if (analyserNode) {
        analyserNode.disconnect();
        analyserNode = null;
    }
    if (audioContext) {
        audioContext.close().catch(() => {});
        audioContext = null;
    }
    frequencyData = null;
    smoothedLevels = [];

    $(".recording-visual .wave-bar").css({
        height: "16px",
        opacity: "0.45",
    });
}

function startVisualizer(stream) {
    const bars = $(".recording-visual .wave-bar").toArray();
    if (!bars.length) {
        return;
    }

    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) {
        return;
    }

    audioContext = new AudioContextClass();
    analyserNode = audioContext.createAnalyser();
    analyserNode.fftSize = 256;
    analyserNode.smoothingTimeConstant = 0.75;
    sourceNode = audioContext.createMediaStreamSource(stream);
    sourceNode.connect(analyserNode);

    frequencyData = new Uint8Array(analyserNode.frequencyBinCount);
    smoothedLevels = Array.from({ length: bars.length }, () => 0);

    const minHeight = 12;
    const maxHeight = 96;
    const binSize = Math.max(1, Math.floor(frequencyData.length / bars.length));

    const render = () => {
        if (!analyserNode) {
            return;
        }
        analyserNode.getByteFrequencyData(frequencyData);

        for (let i = 0; i < bars.length; i += 1) {
            let sum = 0;
            const start = i * binSize;
            const end = Math.min(frequencyData.length, start + binSize);
            for (let j = start; j < end; j += 1) {
                sum += frequencyData[j];
            }
            const avg = sum / Math.max(1, end - start);
            const normalized = avg / 255;

            smoothedLevels[i] = smoothedLevels[i] * 0.6 + normalized * 0.4;

            const height = minHeight + smoothedLevels[i] * (maxHeight - minHeight);
            bars[i].style.height = `${Math.round(height)}px`;
            bars[i].style.opacity = `${Math.max(0.45, Math.min(1, 0.5 + smoothedLevels[i] * 0.8))}`;
        }

        animationFrameId = requestAnimationFrame(render);
    };

    render();
}

async function startRecordingFlow() {
    if (isRecording) {
        return;
    }
    if (!sessionId || !selId) {
        alert("Interview context is invalid.");
        return;
    }
    if (!window.MediaRecorder) {
        alert("This browser does not support audio recording.");
        return;
    }

    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        recordedChunks = [];

        const mimeType = pickSupportedMimeType();
        mediaRecorder = mimeType
            ? new MediaRecorder(mediaStream, { mimeType })
            : new MediaRecorder(mediaStream);

        mediaRecorder.ondataavailable = (event) => {
            if (event.data && event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };

        startVisualizer(mediaStream);
        mediaRecorder.start();
        isRecording = true;
        $("#mode-standby").removeClass("active");
        $("#mode-recording").addClass("active");
        startTimer();
    } catch (_error) {
        stopVisualizer();
        cleanupStream();
        alert("Microphone permission is required.");
    }
}

function finishRecording() {
    if (!isRecording || !mediaRecorder) {
        return;
    }

    isRecording = false;
    stopTimer();
    stopVisualizer();

    mediaRecorder.onstop = async () => {
        try {
            const type = mediaRecorder.mimeType || "audio/webm";
            const blob = new Blob(recordedChunks, { type });
            await uploadRecordedAudio(blob);
            alert("Recording saved.");
            window.location.href = `/interviews/${sessionId}`;
        } catch (error) {
            alert(error.message || "Failed to save recording.");
            $("#mode-recording").removeClass("active");
            $("#mode-standby").addClass("active");
        } finally {
            cleanupStream();
            mediaRecorder = null;
            recordedChunks = [];
        }
    };

    mediaRecorder.stop();
}

$(function () {
    console.log("question_detail loaded");
});
