/**
 * FarmGuard Weather & Satellite Integration
 * Handles: Geolocation, Rainfall Progress, and NDVI Status
 */

async function initDashboard() {
    console.log("Initializing FarmGuard Oracles...");
    
    const options = {
        enableHighAccuracy: true,
        timeout: 7000, // 7 seconds before fallback
        maximumAge: 0
    };

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                console.log("Location detected:", pos.coords.latitude, pos.coords.longitude);
                loadFarmData(pos.coords.latitude, pos.coords.longitude);
            },
            (err) => {
                console.warn("Location access denied or timeout. Using default coordinates.");
                loadFarmData(19.0760, 72.8777); // Default to Mumbai/Maharashtra region
            },
            options
        );
    } else {
        console.error("Geolocation not supported. Using fallback.");
        loadFarmData(19.0760, 72.8777);
    }
}

async function loadFarmData(lat, lon) {
    try {
        // Fetch from our Flask API
        const response = await fetch(`/api/weather/current?lat=${lat}&lon=${lon}`);
        const data = await response.json();

        if (data.error) throw new Error(data.error);

        // 1. Update Hero Section
        document.getElementById('location-display').innerText = `📍 ${data.location_name}`;
        document.getElementById('hero-temp').innerText = `${data.temperature.current}°C`;

        // 2. Update Rainfall Card
        const rainValEl = document.getElementById('rain-value');
        const rainProgEl = document.getElementById('rain-progress');
        const rainBadge = document.getElementById('rain-badge');

        const currentRain = data.rainfall.total_30days;
        const threshold = data.rainfall.threshold;
        const rainPercent = Math.min((currentRain / threshold) * 100, 100);

        rainValEl.innerText = `${currentRain} mm`;
        rainProgEl.style.width = `${rainPercent}%`;

        // Update Badge Color based on risk
        if (rainPercent >= 100) {
            rainBadge.innerText = "TRIGGERED";
            rainBadge.style.background = "#fee2e2";
            rainBadge.style.color = "#ef4444";
            rainProgEl.style.background = "#ef4444";
        } else if (rainPercent > 75) {
            rainBadge.innerText = "WARNING";
            rainBadge.style.background = "#fffbeb";
            rainBadge.style.color = "#d97706";
        }

        // 3. Update Satellite (NDVI) Card
        const ndviGauge = document.getElementById('ndvi-gauge');
        const ndviStatus = document.getElementById('ndvi-status');
        const polyIdEl = document.getElementById('poly-id');

        ndviGauge.innerText = data.ndvi;
        polyIdEl.innerText = data.polygon_id || "poly_88x2_active";
        
        if (data.ndvi > 0.7) {
            ndviStatus.innerText = "Healthy Vegetation";
            ndviStatus.style.color = "#059669";
        } else {
            ndviStatus.innerText = "Distress Detected";
            ndviStatus.style.color = "#ef4444";
        }

    } catch (err) {
        console.error("Dashboard Load Error:", err);
        // Set UI to 'Offline' mode if API fails
        document.getElementById('location-display').innerText = "📍 Connection Error";
    }
}

// Run on page load
document.addEventListener('DOMContentLoaded', initDashboard);