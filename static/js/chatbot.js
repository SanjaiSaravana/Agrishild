let currentState = "India";

// Detect location immediately on load
window.onload = async () => {
    navigator.geolocation.getCurrentPosition(async (pos) => {
        const geo = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${pos.coords.latitude}&lon=${pos.coords.longitude}`);
        const data = await geo.json();
        currentState = data.address.state;
        // Automatically fetch market data for this state too!
        fetchMarketData(null, null, currentState, data.address.city);
    });
};

async function startVoiceChat() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-IN'; // Listen to the user
    
    recognition.onresult = async (event) => {
        const text = event.results[0][0].transcript;
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message: text, state: currentState })
        });
        const result = await response.json();
        speak(result.reply); // Respond in native language
    };
    recognition.start();
}

function speak(text) {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    synth.speak(utterance);
}