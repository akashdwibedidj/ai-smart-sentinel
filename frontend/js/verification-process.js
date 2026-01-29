/**
 * AI Smart Sentinel - Verification Process
 * Multi-stage AI analysis with automatic progression
 */

// ==================== STATE ====================
const state = {
    startTime: Date.now(),
    isPaused: false,
    currentStage: 2,
    stages: [
        { id: 1, name: 'Injection Attack Detection', progress: 100, status: 'complete' },
        { id: 2, name: 'Liveness Detection', progress: 65, status: 'active' },
        { id: 3, name: 'Deepfake Detection', progress: 0, status: 'pending' },
        { id: 4, name: 'Face Recognition', progress: 0, status: 'pending' }
    ],
    framesAnalyzed: 127
};

// ==================== ELAPSED TIME ====================
function updateElapsedTime() {
    if (state.isPaused) return;

    const elapsed = Math.floor((Date.now() - state.startTime) / 1000);
    const minutes = String(Math.floor(elapsed / 60)).padStart(2, '0');
    const seconds = String(elapsed % 60).padStart(2, '0');

    const el = document.getElementById('elapsedTime');
    if (el) el.textContent = `${minutes}:${seconds}`;
}

setInterval(updateElapsedTime, 1000);

// ==================== OVERALL PROGRESS ====================
function calculateOverallProgress() {
    const total = state.stages.reduce((sum, stage) => sum + stage.progress, 0);
    return Math.round(total / state.stages.length);
}

function updateOverallProgress() {
    const progress = calculateOverallProgress();

    const progressFill = document.getElementById('overallProgress');
    const progressPercent = document.getElementById('progressPercent');

    if (progressFill) progressFill.style.width = progress + '%';
    if (progressPercent) progressPercent.textContent = progress + '%';

    // Update pipeline line
    const pipelineProgress = document.getElementById('pipelineProgress');
    if (pipelineProgress) {
        const completedStages = state.stages.filter(s => s.status === 'complete').length;
        const activeProgress = state.stages.find(s => s.status === 'active')?.progress || 0;
        const pipelinePercent = ((completedStages + (activeProgress / 100)) / state.stages.length) * 100;
        pipelineProgress.style.height = pipelinePercent + '%';
    }
}

// ==================== STAGE TEXT ====================
function updateCurrentStageText() {
    const stageText = document.querySelector('.stage-text');
    const activeStage = state.stages.find(s => s.status === 'active');

    if (stageText && activeStage) {
        const messages = {
            1: 'Checking feed integrity...',
            2: 'Analyzing liveness...',
            3: 'Scanning for deepfakes...',
            4: 'Matching face identity...'
        };
        stageText.textContent = messages[activeStage.id] || 'Processing...';
    }
}

// ==================== STAGE SIMULATION ====================
function simulateProgress() {
    if (state.isPaused) return;

    const activeStage = state.stages.find(s => s.status === 'active');
    if (!activeStage) {
        // All stages complete - navigate to success
        completeVerification(true);
        return;
    }

    // Increment progress
    activeStage.progress = Math.min(100, activeStage.progress + Math.random() * 3);

    // Update UI
    if (activeStage.id === 2) {
        const stage2Fill = document.getElementById('stage2Fill');
        const stage2Progress = document.getElementById('stage2Progress');
        if (stage2Fill) stage2Fill.style.width = activeStage.progress + '%';
        if (stage2Progress) stage2Progress.textContent = Math.round(activeStage.progress) + '%';
    }

    // Increment frames analyzed
    state.framesAnalyzed += Math.floor(Math.random() * 5);
    const framesEl = document.getElementById('framesAnalyzed');
    if (framesEl) framesEl.textContent = state.framesAnalyzed;

    // Check if stage complete
    if (activeStage.progress >= 100) {
        activeStage.status = 'complete';

        // Find next stage
        const nextStage = state.stages.find(s => s.status === 'pending');
        if (nextStage) {
            nextStage.status = 'active';
            state.currentStage = nextStage.id;
            updateStageCards();
        }
    }

    updateOverallProgress();
    updateCurrentStageText();
}

// ==================== UPDATE STAGE CARDS ====================
function updateStageCards() {
    state.stages.forEach(stage => {
        const card = document.querySelector(`.stage-card[data-stage="${stage.id}"]`);
        if (!card) return;

        // Update classes
        card.classList.remove('complete', 'active', 'pending');
        card.classList.add(stage.status);

        // Update status text
        const statusEl = card.querySelector('.stage-status');
        if (statusEl) {
            statusEl.className = 'stage-status ' + stage.status;
            statusEl.textContent = stage.status === 'complete' ? 'Complete' :
                stage.status === 'active' ? 'In Progress' : 'Pending';
        }

        // Update progress ring
        const ringEl = card.querySelector('.stage-progress-ring span');
        if (ringEl) {
            ringEl.textContent = Math.round(stage.progress) + '%';
        }

        // Show/hide number or checkmark
        const numberEl = card.querySelector('.stage-number');
        if (numberEl) {
            if (stage.status === 'complete') {
                numberEl.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        `;
            } else if (stage.status === 'active') {
                numberEl.innerHTML = `<div class="stage-spinner"></div>`;
            } else {
                numberEl.textContent = stage.id;
            }
        }
    });
}

// ==================== VERIFICATION COMPLETE ====================
function completeVerification(success) {
    clearInterval(progressInterval);

    const body = document.body;

    if (success) {
        // Success animation
        body.style.transition = 'background 1s ease';
        body.style.background = 'linear-gradient(135deg, rgba(0, 230, 118, 0.1), var(--bg-primary))';

        setTimeout(() => {
            // Navigate to success screen
            console.log('✅ Verification successful! Navigating to success screen...');
            window.location.href = 'verification-success.html';
        }, 1000);
    } else {
        // Failure animation
        body.style.transition = 'background 1s ease';
        body.style.background = 'linear-gradient(135deg, rgba(255, 82, 82, 0.1), var(--bg-primary))';

        setTimeout(() => {
            // Navigate to threat screen
            console.log('🚨 Threat detected! Navigating to threat screen...');
            window.location.href = 'threat-detected.html';
        }, 1000);
    }
}

// ==================== PAUSE / CANCEL ====================
function initControls() {
    const pauseBtn = document.getElementById('pauseBtn');
    const cancelBtn = document.getElementById('cancelBtn');

    if (pauseBtn) {
        pauseBtn.addEventListener('click', () => {
            state.isPaused = !state.isPaused;

            if (state.isPaused) {
                pauseBtn.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          Resume
        `;
                pauseBtn.classList.add('paused');
            } else {
                pauseBtn.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="6" y="4" width="4" height="16"/>
            <rect x="14" y="4" width="4" height="16"/>
          </svg>
          Pause Analysis
        `;
                pauseBtn.classList.remove('paused');
            }
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            const confirmed = confirm(
                '⚠️ CANCEL VERIFICATION?\n\n' +
                'This will stop the analysis and return to the camera view.\n\n' +
                'Are you sure?'
            );

            if (confirmed) {
                clearInterval(progressInterval);
                window.location.href = 'camera-view.html';
            }
        });
    }
}

// ==================== INITIALIZE ====================
let progressInterval;

document.addEventListener('DOMContentLoaded', () => {
    initControls();
    updateOverallProgress();
    updateCurrentStageText();

    // Start progress simulation
    progressInterval = setInterval(simulateProgress, 200);

    // Simulate random AI confidence updates
    setInterval(() => {
        const confidence = 90 + Math.random() * 9;
        const el = document.getElementById('aiConfidence');
        if (el) el.textContent = Math.round(confidence) + '%';
    }, 2000);

    console.log('🔄 Verification process started');
});
