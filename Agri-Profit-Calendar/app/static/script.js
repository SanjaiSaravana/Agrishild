function showDetails(day, event, cropsStr) {
    // UI Elements
    const content = document.getElementById('real-content');
    const placeholder = document.getElementById('placeholder-text');
    const cropList = document.getElementById('crop-list');
    
    // Reset and Show Content
    placeholder.classList.add('hidden');
    content.classList.remove('hidden');
    
    // Update Text
    document.getElementById('panel-date').innerText = "February " + day + ", 2026";
    document.getElementById('panel-event').innerText = event;
    
    // Clear and Fill Crops
    cropList.innerHTML = "";
    if (cropsStr) {
        const crops = cropsStr.split(',');
        crops.forEach(crop => {
            let li = document.createElement('li');
            li.innerHTML = `<span class="check-icon">✓</span> ${crop}`;
            cropList.appendChild(li);
        });
    } else {
        cropList.innerHTML = "<li>Standard market goods apply.</li>";
    }
}