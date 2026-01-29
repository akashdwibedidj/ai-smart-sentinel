/**
 * AI Smart Sentinel - Camera View
 * Interactive JavaScript for individual camera live view
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

// Update every second
setInterval(updateTimestamp, 1000);
updateTimestamp();

// ==================== SIMULATED FACE DETECTION ====================
class FaceDetector {
    constructor(overlayId) {
        this.overlay = document.getElementById(overlayId);
        this.detections = [];
        this.simulateDetections();
    }

    simulateDetections() {
        // Detection boxes will be added dynamically when AI detects faces
        // For now, start with no detections
        this.detections = [];
        this.renderDetections();
    }

    renderDetections() {
        if (!this.overlay) return;

        this.overlay.innerHTML = this.detections.map(det => `
      <div class="detection-box ${det.status === 'threat' ? 'threat' : ''}" 
           style="left: ${det.x}%; top: ${det.y}%; width: ${det.width}%; height: ${det.height}%;">
        <div class="label">Person #${det.id}${det.name ? ' - ' + det.name : ''}</div>
      </div>
    `).join('');
    }

    updateRandomDetection() {
        // Randomly move detection boxes slightly
        this.detections.forEach(det => {
            det.x += (Math.random() - 0.5) * 3;
            det.y += (Math.random() - 0.5) * 2;

            // Keep within bounds
            det.x = Math.max(5, Math.min(80, det.x));
            det.y = Math.max(10, Math.min(70, det.y));
        });

        this.renderDetections();
    }
}

// ==================== AI METRICS SIMULATION ====================
class AIMetrics {
    constructor() {
        this.injectionScore = 0.02;
        this.authenticity = 98.5;
        this.deepfakeProb = 1.2;
        this.confidence = 94;

        this.updateMetrics();
    }

    updateMetrics() {
        setInterval(() => {
            // Simulate small fluctuations
            this.injectionScore = Math.max(0, Math.min(0.1, this.injectionScore + (Math.random() - 0.5) * 0.01));
            this.authenticity = Math.max(95, Math.min(99.9, this.authenticity + (Math.random() - 0.5) * 0.5));
            this.deepfakeProb = Math.max(0.5, Math.min(5, this.deepfakeProb + (Math.random() - 0.5) * 0.3));
            this.confidence = Math.max(85, Math.min(99, this.confidence + (Math.random() - 0.5) * 2));

            this.render();
        }, 3000);
    }

    render() {
        const injectionEl = document.getElementById('injectionScore');
        const authenticityEl = document.getElementById('authenticityValue');
        const deepfakeEl = document.getElementById('deepfakeProb');
        const confidenceEl = document.getElementById('confidenceValue');
        const confidenceFill = document.getElementById('confidenceFill');

        if (injectionEl) {
            injectionEl.textContent = this.injectionScore.toFixed(2);
            injectionEl.classList.toggle('warning', this.injectionScore > 0.05);
        }

        if (authenticityEl) {
            authenticityEl.textContent = this.authenticity.toFixed(1);
        }

        if (deepfakeEl) {
            deepfakeEl.textContent = this.deepfakeProb.toFixed(1) + '%';
            deepfakeEl.classList.toggle('warning', this.deepfakeProb > 3);
        }

        if (confidenceEl) {
            confidenceEl.textContent = Math.round(this.confidence) + '%';
        }

        if (confidenceFill) {
            confidenceFill.style.width = this.confidence + '%';
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

        if (isRecording) {
            recordBtn.title = 'Stop Recording';
            console.log('🔴 Recording started...');
        } else {
            recordBtn.title = 'Record';
            console.log('⏹️ Recording stopped');
        }
    });
}

// ==================== START VERIFICATION ====================
function initVerificationButton() {
    const btn = document.getElementById('startVerification');
    if (!btn) return;

    btn.addEventListener('click', () => {
        btn.disabled = true;
        btn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 6v6l4 2"/>
      </svg>
      Analyzing Feed...
    `;

        // Simulate verification pipeline
        setTimeout(() => {
            btn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 6v6l4 2"/>
        </svg>
        Injection Check...
      `;
        }, 1500);

        setTimeout(() => {
            btn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 6v6l4 2"/>
        </svg>
        Face Verification...
      `;
        }, 3000);

        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
        Verified ✓
      `;
            btn.classList.add('verified');

            // Navigate to verification screen (Screen 5)
            // window.location.href = 'verification-process.html';
            console.log('✅ Verification complete! Would navigate to verification-process.html');

            // Reset after delay
            setTimeout(() => {
                btn.innerHTML = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          Start Verification
        `;
                btn.classList.remove('verified');
            }, 3000);
        }, 4500);
    });
}

// ==================== REPORT THREAT ====================
function initReportThreat() {
    const btn = document.getElementById('reportThreat');
    if (!btn) return;

    btn.addEventListener('click', () => {
        const confirmed = confirm(
            '⚠️ REPORT THREAT\n\n' +
            'This will:\n' +
            '• Immediately flag this camera feed\n' +
            '• Alert security personnel\n' +
            '• Save last 60 seconds of footage\n\n' +
            'Report this threat?'
        );

        if (confirmed) {
            btn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
        Threat Reported
      `;
            btn.disabled = true;
            console.log('🚨 Threat reported to security team');
        }
    });
}

// ==================== INITIALIZE ====================
document.addEventListener('DOMContentLoaded', () => {
    // Initialize face detector
    new FaceDetector('detectionOverlay');

    // Initialize AI metrics
    new AIMetrics();

    // Initialize buttons
    initRecordButton();
    initVerificationButton();
    initReportThreat();

    console.log('📹 Camera View initialized');
});

// Add spinning animation
const style = document.createElement('style');
style.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  .spin {
    animation: spin 1s linear infinite;
  }
  .btn.verified {
    background: var(--accent-green) !important;
    box-shadow: 0 4px 20px rgba(0, 230, 118, 0.35) !important;
  }
`;
document.head.appendChild(style);
