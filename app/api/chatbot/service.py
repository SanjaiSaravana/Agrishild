import httpx
import os


# --- Advanced Mock Engine ---
class MockEngine:
    def __init__(self):
        self.data = {
            "Tamil Nadu": {
                "greetings": ["வணக்கம்! உங்கள் பயிர் எப்படி உள்ளது?", "வணக்கம் விவசாயி அவர்களே!"],
                "market": "தக்காளி மற்றும் வெங்காயம் விலை சீராக உள்ளது. சந்தை நிலவரத்தை அறிய 'சந்தை' என்று டைப் செய்யவும்.",
                "weather": "வானிலை அறிக்கையின்படி, இன்று மழை பெய்ய வாய்ப்புள்ளது.",
                "pest": "பூச்சி தொல்லையை கட்டுப்படுத்த, நீங்கள் வேப்பெண்ணெய் (Neem Oil) பயன்படுத்தலாம்.",
                "fertilizer": "இயற்கை உரம் (தொழு உரம்) பயன்படுத்துவது மண்வளத்தை காக்கும். யூரியா பயன்பாட்டை குறைக்கவும்.",
                "farming": "பயிர் வளர்ப்பு முறை பற்றி அறிய, மண் பரிசோதனை செய்வது அவசியம்.",
                "rice": "நெல் பயிருக்கு தழைச்சத்து (N), மணிச்சத்து (P), சாம்பல் சத்து (K) அவசியம். யூரியா, டி.ஏ.பி (DAP), பொட்டாஷ் உரங்களை பரிந்துரைக்கப்பட்ட அளவில் இடவும். வேப்பம் புண்ணாக்கு கலந்த யூரியா சிறந்தது.",
                "banana": "வாழை தோட்டத்திற்கு சொட்டு நீர் பாசனம் சிறந்தது. 20 நாட்களுக்கு ஒருமுறை உரம் வைக்கவும்.",
                "default": "மன்னிக்கவும், எனக்கு புரியவில்லை. நெல், கரும்பு அல்லது சந்தை விலை பற்றி கேட்கவும்."
            },
            "Punjab": {
                "greetings": ["ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਕੀ ਹਾਲ ਚਾਲ ਹੈ?", "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਖੇਤੀ ਕਿਵੇਂ ਚੱਲ ਰਹੀ ਹੈ?"],
                "market": "ਕਣਕ ਦਾ ਰੇਟ 2200 ਰੁਪਏ ਪ੍ਰਤੀ ਕੁਇੰਟਲ ਚੱਲ ਰਿਹਾ ਹੈ।",
                "weather": "ਮੌਸਮ ਸਾਫ ਰਹਿਣ ਦੀ ਉਮੀਦ ਹੈ।",
                "pest": "ਸੁੰਢੀ ਤੋਂ ਬਚਣ ਲਈ ਸਪਰੇਅ ਦਾ ਛਿੜਕਾਅ ਕਰੋ।",
                "fertilizer": "ਯੂਰੀਆ ਦੀ ਵਰਤੋਂ ਘੱਟ ਕਰੋ। ਜੈਵਿਕ ਖਾਦ ਵਰਤੋ।",
                "farming": "ਫਸਲ ਦੀ ਬਿਜਾਈ ਲਈ ਸਹੀ ਸਮਾਂ ਚੁਣੋ।",
                "rice": "ਝੋਨੇ ਦੀ ਫਸਲ ਲਈ ਨਾਈਟ੍ਰੋਜਨ, ਫਾਸਫੋਰਸ ਅਤੇ ਪੋਟਾਸ਼ ਦੀ ਲੋੜ ਹੁੰਦੀ ਹੈ। ਯੂਰੀਆ ਅਤੇ ਡੀ.ਏ.ਪੀ. ਦੀ ਵਰਤੋਂ ਸਿਫਾਰਸ਼ ਅਨੁਸਾਰ ਕਰੋ।",
                "banana": "ਕੇਲੇ ਦੀ ਖੇਤੀ ਲਈ ਪਾਣੀ ਦੀ ਸਮਰੱਥ ਵਰਤੋਂ ਜ਼ਰੂਰੀ ਹੈ।",
                "default": "ਮਾਫ ਕਰਨਾ, ਸਮਝ ਨਹੀਂ ਆਇਆ। ਕਣਕ, ਝੋਨਾ ਜਾਂ ਮੰਡੀ ਦੇ ਭਾਅ ਬਾਰੇ ਪੁੱਛੋ।"
            },
            "Hindi": { # Default for North India states
                "greetings": ["नमस्ते! कैसे हैं आप?", "नमस्ते! खेती कैसी चल रही है?"],
                "market": "मंडी में आलू और प्याज के दाम बढ़ रहे हैं।",
                "weather": "आज मौसम साफ रहेगा।",
                "pest": "कीड़ा लगने पर नीम का तेल प्रयोग करें।",
                "fertilizer": "जैविक खाद का प्रयोग करें।",
                "farming": "खेती के लिए मिट्टी की जांच ज़रूरी है।",
                "rice": "धान की फसल के लिए यूरिया, डीएपी और पोटाश का उचित मात्रा में प्रयोग करें। जिंक सल्फेट भी लाभदायक है।",
                "banana": "केले की खेती के लिए नियमित पानी और खाद ज़रूरी है।",
                "default": "माफ़ कीजिये, मैं समझा नहीं। कृपया फसल या मंडी भाव के बारे में पूछें।"
            }
        }
        self.default_lang = "Hindi"

    def get_response(self, state: str, message: str, history: list) -> str:
        # Determine language bucket
        lang_key = state if state in ["Tamil Nadu", "Punjab"] else self.default_lang
        responses = self.data.get(lang_key, self.data[self.default_lang])
        
        msg_lower = message.lower()
        print(f"DEBUG: Processing message '{msg_lower}' for state '{state}'") # Debug log
        
        # 1. Check for specific keywords (Expanded with Native Scripts)
        greeting_keywords = ["hi", "hello", "vanakkam", "namaste", "ssup", "வணக்கம்", "नमस्ते", "sat sri akal"]
        if any(w in msg_lower for w in greeting_keywords):
            import random
            return random.choice(responses["greetings"])
        
        market_keywords = ["market", "price", "rate", "cost", "bhav", "vilai", "விலை", "daam"]
        if any(w in msg_lower for w in market_keywords):
            return responses["market"]
            
        weather_keywords = ["weather", "rain", "sun", "humid", "mazhai", "mausam", "மழை", "vaanilai"]
        if any(w in msg_lower for w in weather_keywords):
            return responses["weather"]

        pest_keywords = ["pest", "insect", "worm", "poochi", "keeda", "பூச்சி", "sundhi"]
        if any(w in msg_lower for w in pest_keywords):
            return responses["pest"]

        # Check crop specific keywords BEFORE generic fertilizer/farming keywords
        rice_keywords = ["rice", "paddy", "nellu", "nel", "நெல்", "adhan", "jhona"]
        if any(w in msg_lower for w in rice_keywords):
             return responses["rice"]
             
        banana_keywords = ["banana", "kela", "vaazhai", "வாழை"]
        if any(w in msg_lower for w in banana_keywords):
            return responses["banana"]

        fertilizer_keywords = ["fertilizer", "urea", "uram", "khaad", "உரம்"]
        if any(w in msg_lower for w in fertilizer_keywords):
            return responses["fertilizer"]
            
        farming_keywords = ["grow", "cultivation", "plant", "valarpu", "kheti", "விளைய", "saag", "thottam", "தோற்றம்", "தோட்டம்"]
        if any(w in msg_lower for w in farming_keywords):
            return responses["farming"]

        # 2. Context Awareness (Simple)
        if history and len(history) > 0:
            last_msg = history[-1].get("content", "").lower()
            if "market" in last_msg or "price" in last_msg:
                 if "market" not in msg_lower: 
                    return responses["market"]

        # 3. Default Fallback
        return responses["default"]

engine = MockEngine()

async def get_ai_response(message: str, state: str, history: list = []):
    api_key = os.getenv('GROQ_API_KEY')
    
    # --- REAL AI ---
    if api_key:
        async with httpx.AsyncClient() as client:
            try:
                # Construct the messages list
                messages_payload = [
                    {"role": "system", "content": f"""
                    You are a precise and helpful agricultural expert (Kisan Mitra) assisting a farmer in {state}.
                    
                    STRICT GUIDELINES:
                    1. LANGUAGE: Respond ONLY in the native regional language of {state} (e.g., Use Tamil script for Tamil Nadu, Punjabi for Punjab). 
                    2. NO ENGLISH: Do NOT provide English translations or explanations. The response must be 100% in the regional script.
                    3. ACCURACY: Provide specific, scientific, and practical advice. For fertilizers, mention specific names (Urea, DAP, Potash) if applicable.
                    4. TONE: Professional, respectful, and authoritative yet accessible.
                    5. FORMAT: Keep it clear. Use bullet points if listing items.
                    6. CONTEXT: Use the chat history to understand follow-up questions.
                    
                    Example for Tamil Nadu (Rice Fertilizer):
                    "நெல் பயிருக்கு தழைச்சத்து (Nitrogen), மணிச்சத்து (Phosphorus) அவசியம். ஏக்கருக்கு 50 கிலோ யூரியா மற்றும் 25 கிலோ டி.ஏ.பி இட வேண்டும்."
                    """}
                ]
                
                # Append History 
                for msg in history[-6:]:
                    messages_payload.append({"role": msg.get("role"), "content": msg.get("content")})
                
                # Append Current
                if not history or history[-1].get("content") != message:
                     messages_payload.append({"role": "user", "content": message})

                res = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": messages_payload
                    },
                    timeout=15.0
                )
                return res.json()['choices'][0]['message']['content']
            except Exception as e:
                print(f"LLM Error: {e}")
                # Fallthrough to mock
    
    # --- MOCK ENGINE FALLBACK ---
    print(f"Using Mock Engine for {state}")
    return engine.get_response(state, message, history)