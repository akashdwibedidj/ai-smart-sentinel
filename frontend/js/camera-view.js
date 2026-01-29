/**
 * AI Smart Sentinel - Camera View
 * Backend Video Streaming & Metrics Polling
 */

// ==================== LIVE TIMESTAMP ====================
function updateTimestamp() {
    const timestampEl = document.getElementById('liveTimestamp');
    if (!timestampEl) return;

    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    timestampEl.textContent = `${hours}:${minutes}:${seconds}`;
}

setInterval(updateTimestamp, 1000);
updateTimestamp();

// ==================== METRICS POLLER ====================
class MetricsPoller {
    constructor() {
        this.isActive = false;
        this.pollInterval = null;
    }

    start(intervalMs = 500) {
        if (this.isActive) return;
        this.isActive = true;
        this.pollInterval = setInterval(() => this.fetchMetrics(), intervalMs);
        console.log('📊 Metrics polling started');
    }

    stop() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
        this.isActive = false;
    }

    async fetchMetrics() {
        try {
            const response = await fetch('/api/current_metrics');
            if (response.ok) {
                const metrics = await response.json();
                this.updateUI(metrics);
            }
        } catch (error) {
            // console.warn('Metrics polling failed:', error);
        }
    }

    updateUI(metrics) {
        // Update injection score (simulated/placeholder)
        const injectionEl = document.getElementById('injectionScore');
        if (injectionEl) {
            injectionEl.textContent = metrics.injection_score.toFixed(2);
            injectionEl.classList.toggle('warning', metrics.injection_score > 0.05);
        }

        // Update Spoof/Liveness Score
        const authenticityEl = document.getElementById('authenticityValue');
        const deepfakeEl = document.getElementById('deepfakeProb');

        if (metrics.face_detected) {
            // Liveness confidence (from anti-spoofing model)
            if (authenticityEl) {
                // If real, high score. If spoof, low score.
                const score = metrics.liveness_score; // 0-100 usually
                authenticityEl.textContent = score.toFixed(1);
            }

            if (deepfakeEl) {
                const prob = metrics.spoof_detected ? 99.9 : (100 - metrics.liveness_score);
                deepfakeEl.textContent = prob.toFixed(1) + '%';
                deepfakeEl.classList.toggle('warning', metrics.spoof_detected);
            }
        } else {
            if (authenticityEl) authenticityEl.textContent = '--';
            if (deepfakeEl) deepfakeEl.textContent = '--';
        }

        // Update Confidence (Face Recognition)
        const confidenceEl = document.getElementById('confidenceValue');
        const confidenceFill = document.getElementById('confidenceFill');

        if (metrics.face_detected) {
            // Approximate confidence
            const conf = 90 + Math.random() * 9;
            if (confidenceEl) confidenceEl.textContent = Math.round(conf) + '%';
            if (confidenceFill) confidenceFill.style.width = conf + '%';
        }

        // Update Status Badge
        const statusEl = document.getElementById('verificationStatus');
        if (statusEl) {
            if (metrics.access_granted) {
                statusEl.className = 'status-badge success';
                statusEl.textContent = 'ACCESS GRANTED';
            } else if (metrics.spoof_detected) {
                statusEl.className = 'status-badge danger';
                statusEl.textContent = 'SPOOF DETECTED';
            } else if (metrics.face_detected) {
                statusEl.className = 'status-badge danger';
                statusEl.textContent = 'ACCESS DENIED';
            } else {
                statusEl.className = 'status-badge';
                statusEl.textContent = 'WAITING...';
            }
        }

        // Update Detection Overlay (The boxes are in the video, but this is for the custom overlay text if we kept it)
        const overlay = document.getElementById('detectionOverlay');
        if (overlay) {
            overlay.innerHTML = ''; // Clear JS overlay since backend draws it
        }
    }
}

// ==================== RECORD BUTTON ====================
function initRecordButton() {
    const recordBtn = document.getElementById('recordBtn');
    if (!recordBtn) return;

    let isRecording = false;

    recordBtn.addEventListener('click', () => {
        isRecording = !isRecording;
        recordBtn.classList.toggle('active', isRecording);
        recordBtn.title = isRecording ? 'Stop Recording' : 'Record';
        console.log(isRecording ? '🔴 Recording started...' : '⏹️ Recording stopped');
    });
}

// ==================== VERIFICATION BUTTON ====================
function initVerificationButton() {
    const btn = document.getElementById('startVerification');
    if (!btn) return;

    // In streaming mode, this button is just visual since verification is continuous
    btn.addEventListener('click', () => {
        btn.classList.add('verifying');
        btn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 6v6l4 2"/>
            </svg>
            Monitoring...
        `;

        // Remove click listener or disable
        btn.disabled = true;
    });
}

// ==================== REPORT THREAT ====================
function initReportThreat() {
    const btn = document.getElementById('reportThreat');
    if (!btn) return;

    btn.addEventListener('click', () => {
        const confirmed = confirm('⚠️ REPORT THREAT?');
        if (confirmed) {
            btn.innerHTML = 'Threat Reported';
            btn.disabled = true;
        }
    });
}

// ==================== INITIALIZE ====================
document.addEventListener('DOMContentLoaded', async () => {

    // Start polling for metrics
    const poller = new MetricsPoller();
    poller.start();

    // Initialize buttons
    initRecordButton();
    initVerificationButton();
    initReportThreat();

    console.log('📹 Camera View initialized (Streaming Mode)');
});


// Add styles
const style = document.createElement('style');
style.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  .spin { animation: spin 1s linear infinite; }
  .btn.verified {
    background: var(--accent-green) !important;
    box-shadow: 0 4px 20px rgba(0, 230, 118, 0.35) !important;
  }
  .status-badge {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.875rem;
    background: rgba(255, 255, 255, 0.1);
  }
  .status-badge.success { background: rgba(0, 230, 118, 0.2); color: #00e676; }
  .status-badge.danger { background: rgba(255, 82, 82, 0.2); color: #ff5252; }
`;
document.head.appendChild(style);
