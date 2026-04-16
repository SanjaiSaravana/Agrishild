let currentUserState = "India";
let currentUserDistrict = "";

// 1. Location & Geocoding
window.onload = () => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async (position) => {
            const { latitude, longitude } = position.coords;
            try {
                const geoRes = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`);
                const geoData = await geoRes.json();
                
                currentUserState = geoData.address.state || "India";
                currentUserDistrict = (geoData.address.state_district || geoData.address.county || "").replace(' District', '');
                
                // Update UI elements
                const locDisplay = document.getElementById('location-display');
                if(locDisplay) locDisplay.innerText = `${currentUserDistrict}, ${currentUserState}`;
                
                const locText = document.getElementById('location-text');
                if(locText) locText.innerText = `📍 Viewing Mandis in ${currentUserDistrict}, ${currentUserState}`;

                // Trigger market data for index page
                if(document.getElementById('market-list')) {
                    fetchMarketData(latitude, longitude, currentUserState, currentUserDistrict);
                }
            } catch (e) { console.error("Location error", e); }
        });
    }
};

// 2. Market Tracker Rendering
async function fetchMarketData(lat, lon, state, district) {
    const marketList = document.getElementById('market-list');
    if(!marketList) return;

    try {
        const response = await fetch('/api/market-tracker', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ state, district })
        });
        const result = await response.json();
        
        if (result.data.length > 0) {
            marketList.innerHTML = result.data.map(record => `
                <div class="mandi-card">
                    <div class="live-tag"><span class="pulse"></span> ${record.market}</div>
                    <h3>${record.commodity}</h3>
                    <p>Variety: ${record.variety}</p>
                    <div class="price">₹${record.modal_price} <small>/ quintal</small></div>
                </div>
            `).join('');
        }
    } catch (e) { console.error("Market fetch failed", e); }
}

// 3. Human-like Chat Bot Logic
async function sendMessage() {
    const input = document.getElementById('user-input');
    const text = input.value.trim();
    if (!text) return;

    appendBubble('user', text);
    input.value = '';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, state: currentUserState })
        });
        const data = await response.json();
        
        appendBubble('bot', data.reply);
        speakResponse(data.reply, data.lang_code); 
    } catch (e) { appendBubble('bot', "Connection error."); }
}

function speakResponse(text, langCode) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = langCode;
    utterance.rate = 0.9; // Natural human speed
    
    const voices = window.speechSynthesis.getVoices();
    utterance.voice = voices.find(v => v.lang === langCode) || voices[0];
    
    window.speechSynthesis.speak(utterance);
}

function appendBubble(sender, text) {
    const chatBox = document.getElementById('chat-box');
    if(!chatBox) return;
    const div = document.createElement('div');
    div.className = `msg-wrapper ${sender}`;
    div.innerHTML = `<div class="msg-bubble">${text}</div>`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 4. Voice Trigger
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'en-IN'; // Can be adjusted based on currentUserState

function startVoiceChat() {
    recognition.start();
    const modal = document.getElementById('voice-modal');
    if(modal) modal.style.display = 'flex';
}

recognition.onresult = (event) => {
    document.getElementById('user-input').value = event.results[0][0].transcript;
    if(document.getElementById('voice-modal')) document.getElementById('voice-modal').style.display = 'none';
    sendMessage();
};

// 2. Human-like Chat Logic
async function sendMessage() {
    const input = document.getElementById('user-input');
    const text = input.value.trim();
    if (!text) return;

    appendBubble('user', text);
    input.value = '';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, state: currentUserState })
        });
        const data = await response.json();
        
        appendBubble('bot', data.reply);
        speak(data.reply, data.lang_code); // Human voice in regional language
    } catch (e) { appendBubble('bot', "Connection error."); }
}

function speak(text, langCode) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = langCode;
    utterance.rate = 0.9; // Slightly slower for natural feel
    
    // Find best regional voice
    const voices = window.speechSynthesis.getVoices();
    utterance.voice = voices.find(v => v.lang === langCode) || voices[0];
    
    window.speechSynthesis.speak(utterance);
}

function appendBubble(sender, text) {
    const chatBox = document.getElementById('chat-box');
    if(!chatBox) return;
    const div = document.createElement('div');
    div.className = `msg-wrapper ${sender}`;
    div.innerHTML = `<div class="msg-bubble">${text}</div>`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

