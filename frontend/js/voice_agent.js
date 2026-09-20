class VoiceAgent {
    constructor(onResultCallback, onStateChangeCallback) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.supported = !!SpeechRecognition;
        
        if (!this.supported) {
            console.warn("[VoiceAgent] SpeechRecognition API is not supported in this browser.");
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';

        this.onResult = onResultCallback;
        this.onStateChange = onStateChangeCallback;
        this.isListening = false;

        this.initListeners();
    }

    initListeners() {
        this.recognition.onstart = () => {
            this.isListening = true;
            if (this.onStateChange) this.onStateChange('listening', 'Listening to your command...');
        };

        this.recognition.onresult = (event) => {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            const isFinal = event.results[0].isFinal;
            if (this.onResult) this.onResult(transcript, isFinal);
        };

        this.recognition.onerror = (event) => {
            console.error("[VoiceAgent] Speech recognition error:", event.error);
            this.isListening = false;
            if (this.onStateChange) this.onStateChange('error', `Voice Error: ${event.error}`);
        };

        this.recognition.onend = () => {
            this.isListening = false;
            if (this.onStateChange) this.onStateChange('idle', 'Click Orb or Mic to Speak');
        };
    }

    toggle() {
        if (!this.supported) {
            alert("Speech recognition is not supported in your browser. Please use Google Chrome or Microsoft Edge.");
            return;
        }
        if (this.isListening) {
            this.stop();
        } else {
            this.start();
        }
    }

    start() {
        if (this.supported && !this.isListening) {
            try {
                this.recognition.start();
            } catch (err) {
                console.error("[VoiceAgent] Could not start recognition:", err);
            }
        }
    }

    stop() {
        if (this.supported && this.isListening) {
            this.recognition.stop();
        }
    }

    speak(text, onComplete) {
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        if (onComplete) utterance.onend = onComplete;
        window.speechSynthesis.speak(utterance);
    }
}
