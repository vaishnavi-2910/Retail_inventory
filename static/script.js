let myChart;

async function getForecast() {
    const stock = document.getElementById('stockInput').value;
    
    const response = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stock: stock })
    });

    const data = await response.json();

    // Update UI
    document.getElementById('resultArea').classList.remove('hidden');
    document.getElementById('predVal').innerText = data.prediction;
    document.getElementById('growthVal').innerText = data.growth;
    
    const statusBox = document.getElementById('statusBox');
    statusBox.innerText = `Status: ${data.status}`;
    statusBox.style.backgroundColor = data.color;

    // Render Chart
    const ctx = document.getElementById('salesChart').getContext('2d');
    if (myChart) myChart.destroy();
    
    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Sales Trend (Historical + Predicted)',
                data: data.values,
                borderColor: '#00d4ff',
                tension: 0.3,
                fill: true,
                backgroundColor: 'rgba(0, 212, 255, 0.1)'
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true, grid: { color: '#333' } },
                x: { grid: { color: '#333' } }
            }
        }
    });
}