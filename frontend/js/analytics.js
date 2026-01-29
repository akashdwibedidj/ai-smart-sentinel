/**
 * AI Smart Sentinel - Analytics Dashboard
 * Chart.js configurations and interactive elements
 */

document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    initFilters();
});

// ==================== CHARTS INITIALIZATION ====================
function initCharts() {
    // Common Chart Options
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: '#94a3b8',
                    font: { family: 'Inter', size: 11 }
                }
            }
        },
        scales: {
            y: {
                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                ticks: { color: '#64748b' }
            },
            x: {
                grid: { display: false },
                ticks: { color: '#64748b' }
            }
        }
    };

    // 1. Activity Line Chart
    const ctxActivity = document.getElementById('activityChart').getContext('2d');

    // Create gradient
    const gradient = ctxActivity.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(0, 212, 255, 0.2)');
    gradient.addColorStop(1, 'rgba(0, 212, 255, 0)');

    new Chart(ctxActivity, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Access Attempts',
                data: [150, 230, 180, 320, 290, 140, 190],
                borderColor: '#00d4ff',
                backgroundColor: gradient,
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#0B0F14',
                pointBorderColor: '#00d4ff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            ...commonOptions,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(11, 15, 20, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#94a3b8',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false
                }
            }
        }
    });

    // 2. Threat Breakdown Pie Chart
    const ctxPie = document.getElementById('threatPieChart').getContext('2d');
    new Chart(ctxPie, {
        type: 'doughnut',
        data: {
            labels: ['Injection', 'Deepfake', 'Liveness', 'Unknown'],
            datasets: [{
                data: [15, 45, 25, 15],
                backgroundColor: [
                    '#ffb300', // Amber (Injection)
                    '#ff5252', // Red (Deepfake)
                    '#00d4ff', // Cyan (Liveness)
                    '#64748b'  // Grey (Unknown)
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#94a3b8',
                        font: { family: 'Inter', size: 11 },
                        usePointStyle: true,
                        padding: 15
                    }
                }
            }
        }
    });

    // 3. Location Bar Chart
    const ctxBar = document.getElementById('locationBarChart').getContext('2d');
    new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: ['Entrance', 'Lobby', 'Server Rm', 'Parking'],
            datasets: [{
                label: 'Threats',
                data: [12, 8, 3, 5],
                backgroundColor: '#ff5252',
                borderRadius: 4,
                barThickness: 20
            }, {
                label: 'Verified',
                data: [150, 120, 45, 30],
                backgroundColor: '#00e676',
                borderRadius: 4,
                barThickness: 20
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                x: {
                    stacked: true,
                    grid: { display: false },
                    ticks: { color: '#64748b' }
                },
                y: {
                    stacked: true,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748b' }
                }
            }
        }
    });
}

// ==================== INTERACTIVITY ====================
function initFilters() {
    // Toggle buttons
    const toggles = document.querySelectorAll('.toggle-btn');
    toggles.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from siblings
            btn.parentElement.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
            // Add active class to clicked
            btn.classList.add('active');

            // Simulation: Filter table rows
            if (btn.classList.contains('success')) {
                filterTable('success');
            } else if (btn.classList.contains('threat')) {
                filterTable('threat');
            } else {
                filterTable('all');
            }
        });
    });

    // Chart time toggles
    const timeToggles = document.querySelectorAll('.chart-toggle');
    timeToggles.forEach(btn => {
        btn.addEventListener('click', () => {
            btn.parentElement.querySelectorAll('.chart-toggle').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            // In a real app, this would update chart data
        });
    });
}

function filterTable(type) {
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        if (type === 'all') {
            row.style.display = 'table-row';
        } else if (type === 'threat') {
            const isThreat = row.querySelector('.badge.threat');
            row.style.display = isThreat ? 'table-row' : 'none';
        } else if (type === 'success') {
            const isSuccess = row.querySelector('.badge.success');
            row.style.display = isSuccess ? 'table-row' : 'none';
        }
    });
}
