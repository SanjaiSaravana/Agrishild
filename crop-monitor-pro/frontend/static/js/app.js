const map = L.map('map-container').setView([20.5937, 78.9629], 5);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

let satelliteLayer;

async function runAnalysis(lat, lon) {
    const response = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat, lon })
    });

    const data = await response.json();

    // Update UI components
    document.querySelector('.score-box').innerText = data.accuracy;
    document.querySelector('h2').innerText = data.ndvi;
    document.querySelector('.bar').style.width = (data.ndvi * 100) + '%';
    
    // Land Type Differentiator
    const landLabel = document.querySelector('.no-issue');
    landLabel.innerText = data.land_type;
    landLabel.style.color = data.land_type === "Farm" ? "#2ea043" : "#f85149";

    // Overlay Satellite Data
    if (satelliteLayer) map.removeLayer(satelliteLayer);
    satelliteLayer = L.tileLayer(data.map_url).addTo(map);
}

// Auto-detect location
map.locate({setView: true, maxZoom: 14});
map.on('locationfound', (e) => {
    runAnalysis(e.latlng.lat, e.latlng.lng);
});