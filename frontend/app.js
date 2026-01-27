// AI Smart Sentinel - Frontend JavaScript
const API_BASE = 'http://localhost:5000/api';

let videoStream = null;
let videoElement = document.getElementById('videoElement');
let canvas = document.getElementById('canvas');
let ctx = canvas.getContext('2d');

// Start Camera
document.getElementById('startCamera').addEventListener('click', async () => {
    try {
        videoStream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 } 
        });
        videoElement.srcObject = videoStream;
        
        document.getElementById('startCamera').disabled = true;
        document.getElementById('stopCamera').disabled = false;
        
        updateStatus('🟢 Camera started successfully', 'success');
    } catch (error) {
        updateStatus('❌ Error accessing camera: ' + error.message, 'error');
    }
});

// Stop Camera
document.getElementById('stopCamera').addEventListener('click', () => {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoElement.srcObject = null;
        
        document.getElementById('startCamera').disabled = false;
        document.getElementById('stopCamera').disabled = true;
        
        updateStatus('⏹️ Camera stopped', 'info');
    }
});

// Capture frame from video
function captureFrame() {
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    ctx.drawImage(videoElement, 0, 0);
    return canvas.toDataURL('image/jpeg');
}

// Register Face
document.getElementById('registerBtn').addEventListener('click', async () => {
    const personId = document.getElementById('personId').value.trim();
    
    if (!personId) {
        updateStatus('⚠️ Please enter a Person ID', 'warning');
        return;
    }
    
    if (!videoStream) {
        updateStatus('⚠️ Please start the camera first', 'warning');
        return;
    }
    
    try {
        updateStatus('⏳ Registering face...', 'info');
        
        const imageData = captureFrame();
        
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: imageData,
                person_id: personId
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateStatus(`✅ Face registered successfully for ${personId}`, 'success');
            document.getElementById('personId').value = '';
            loadRegisteredFaces();
        } else {
            updateStatus(`❌ Registration failed: ${result.message}`, 'error');
        }
    } catch (error) {
        updateStatus(`❌ Error: ${error.message}`, 'error');
    }
});

// Verify Face
document.getElementById('verifyBtn').addEventListener('click', async () => {
    if (!videoStream) {
        updateStatus('⚠️ Please start the camera first', 'warning');
        return;
    }
    
    try {
        updateStatus('⏳ Verifying access...', 'info');
        
        const imageData = captureFrame();
        
        const response = await fetch(`${API_BASE}/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: imageData
            })
        });
        
        const result = await response.json();
        displayVerificationResult(result);
        
    } catch (error) {
        updateStatus(`❌ Error: ${error.message}`, 'error');
    }
});

// Display Verification Results
function displayVerificationResult(result) {
    const resultsDiv = document.getElementById('resultsDisplay');
    
    if (result.access_granted) {
        resultsDiv.className = 'results-display success';
        resultsDiv.innerHTML = `
            <h4>✅ ACCESS GRANTED</h4>
            <p><strong>Person:</strong> ${result.person_id}</p>
            <p><strong>Confidence:</strong> ${result.confidence.toFixed(1)}%</p>
            <p><strong>Time:</strong> ${new Date(result.timestamp).toLocaleString()}</p>
            <hr style="margin: 10px 0;">
            <p><strong>Security Checks:</strong></p>
            <ul>
                <li>✓ Injection Check: ${result.checks.injection_check.passed ? 'PASSED' : 'FAILED'}</li>
                <li>✓ Liveness Check: ${result.checks.liveness_check.passed ? 'PASSED' : 'FAILED'}</li>
                <li>✓ Face Verification: ${result.checks.face_verification.passed ? 'PASSED' : 'FAILED'}</li>
            </ul>
        `;
        updateStatus('✅ Access granted', 'success');
    } else {
        resultsDiv.className = 'results-display error';
        resultsDiv.innerHTML = `
            <h4>❌ ACCESS DENIED</h4>
            <p><strong>Decision:</strong> ${result.decision}</p>
            <p><strong>Reason:</strong> ${result.reason.join(', ')}</p>
            <p><strong>Confidence:</strong> ${result.confidence.toFixed(1)}%</p>
            <p><strong>Time:</strong> ${new Date(result.timestamp).toLocaleString()}</p>
            <hr style="margin: 10px 0;">
            <p><strong>Security Checks:</strong></p>
            <ul>
                <li>${result.checks.injection_check.passed ? '✓' : '✗'} Injection Check: ${result.checks.injection_check.passed ? 'PASSED' : 'FAILED'}</li>
                <li>${result.checks.liveness_check.passed ? '✓' : '✗'} Liveness Check: ${result.checks.liveness_check.passed ? 'PASSED' : 'FAILED'}</li>
                <li>${result.checks.face_verification.passed ? '✓' : '✗'} Face Verification: ${result.checks.face_verification.passed ? 'PASSED' : 'FAILED'}</li>
            </ul>
        `;
        updateStatus('❌ Access denied', 'error');
    }
}

// Load Registered Faces
document.getElementById('listFacesBtn').addEventListener('click', loadRegisteredFaces);

async function loadRegisteredFaces() {
    try {
        const response = await fetch(`${API_BASE}/registered-faces`);
        const result = await response.json();
        
        const facesList = document.getElementById('facesList');
        
        if (result.registered_faces.length === 0) {
            facesList.innerHTML = '<p class="placeholder">No registered faces yet</p>';
        } else {
            facesList.innerHTML = result.registered_faces
                .map(face => `<div class="face-item">👤 ${face}</div>`)
                .join('');
        }
    } catch (error) {
        console.error('Error loading faces:', error);
    }
}

// Update Status Display
function updateStatus(message, type = 'info') {
    const statusDiv = document.getElementById('statusDisplay');
    statusDiv.innerHTML = `<p>${message}</p>`;
    
    // Optional: Add color coding
    statusDiv.className = 'status-display';
    if (type === 'success') statusDiv.style.borderLeft = '5px solid #28a745';
    else if (type === 'error') statusDiv.style.borderLeft = '5px solid #dc3545';
    else if (type === 'warning') statusDiv.style.borderLeft = '5px solid #ffc107';
    else statusDiv.style.borderLeft = '5px solid #17a2b8';
}

// Check backend health on load
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const result = await response.json();
        
        if (result.status === 'online') {
            updateStatus('🟢 Backend connected - All systems ready', 'success');
        }
    } catch (error) {
        updateStatus('🔴 Backend offline - Please start the server', 'error');
    }
}

// Initialize
checkHealth();
loadRegisteredFaces();
