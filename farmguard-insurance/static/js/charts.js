document.addEventListener('DOMContentLoaded', () => {
    // Rainfall Trend Chart
    const rainCtx = document.getElementById('rainfallChart').getContext('2d');
    new Chart(rainCtx, {
        type: 'line',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Today'],
            datasets: [{
                label: 'Rainfall (mm)',
                data: [15, 28, 42, 68, 145],
                borderColor: '#2C5F2D',
                tension: 0.4,
                fill: true,
                backgroundColor: 'rgba(44, 95, 45, 0.1)'
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });

    // Temperature Bar Chart
    const tempCtx = document.getElementById('tempChart').getContext('2d');
    new Chart(tempCtx, {
        type: 'bar',
        data: {
            labels: ['M', 'T', 'W', 'T', 'F', 'S', 'S'],
            datasets: [{
                label: 'Max Temp (°C)',
                data: [35, 37, 38, 38, 36, 34, 33],
                backgroundColor: '#F59E0B',
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } }
        }
    });
});