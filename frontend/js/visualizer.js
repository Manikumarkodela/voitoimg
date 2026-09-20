class AudioVisualizer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.audioCtx = null;
        this.analyser = null;
        this.microphone = null;
        this.isVisualizing = false;
        this.animationId = null;
    }

    async start() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioCtx.createAnalyser();
            this.analyser.fftSize = 64;
            
            this.microphone = this.audioCtx.createMediaStreamSource(stream);
            this.microphone.connect(this.analyser);
            
            this.isVisualizing = true;
            this.draw();
        } catch (err) {
            console.warn("[AudioVisualizer] Microphone access unavailable for visualizer:", err);
            this.drawIdleWave();
        }
    }

    stop() {
        this.isVisualizing = false;
        if (this.animationId) cancelAnimationFrame(this.animationId);
        if (this.microphone && this.microphone.mediaStream) {
            this.microphone.mediaStream.getTracks().forEach(track => track.stop());
        }
        if (this.audioCtx) {
            this.audioCtx.close();
        }
        this.drawIdleWave();
    }

    draw() {
        if (!this.isVisualizing) return;
        this.animationId = requestAnimationFrame(() => this.draw());

        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        this.analyser.getByteFrequencyData(dataArray);

        const width = this.canvas.width;
        const height = this.canvas.height;
        this.ctx.clearRect(0, 0, width, height);

        const barWidth = (width / bufferLength) * 1.5;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
            const barHeight = (dataArray[i] / 255) * height;
            
            const gradient = this.ctx.createLinearGradient(0, height, 0, 0);
            gradient.addColorStop(0, 'rgba(255, 255, 255, 0.2)');
            gradient.addColorStop(1, 'rgba(255, 255, 255, 0.9)');
            
            this.ctx.fillStyle = gradient;
            this.ctx.fillRect(x, height - barHeight, barWidth - 2, barHeight);

            x += barWidth;
        }
    }

    drawIdleWave() {
        if (!this.canvas) return;
        const width = this.canvas.width;
        const height = this.canvas.height;
        this.ctx.clearRect(0, 0, width, height);
        
        this.ctx.beginPath();
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        this.ctx.lineWidth = 1.5;
        this.ctx.moveTo(0, height / 2);
        this.ctx.lineTo(width, height / 2);
        this.ctx.stroke();
    }
}
