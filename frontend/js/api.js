/**
 * AI Smart Sentinel - API Service
 * Centralized API communication with the Flask backend
 */

const API_BASE = 'http://localhost:5000/api';

// ==================== API SERVICE ====================
const ApiService = {

    /**
     * Health check - test backend connectivity
     * @returns {Promise<{status: string, components: object}>}
     */
    async healthCheck() {
        try {
            const response = await fetch(`${API_BASE}/health`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            if (!response.ok) throw new Error('Backend offline');
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            return { status: 'offline', error: error.message };
        }
    },

    /**
     * Verify access - send image for full verification pipeline
     * @param {string} imageBase64 - Base64 encoded image (with data:image prefix)
     * @param {string|null} personId - Optional person ID for targeted verification
     * @returns {Promise<object>} - Verification decision
     */
    async verifyAccess(imageBase64, personId = null) {
        try {
            const response = await fetch(`${API_BASE}/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: imageBase64,
                    person_id: personId
                })
            });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Verification failed');
            }
            return await response.json();
        } catch (error) {
            console.error('Verification error:', error);
            throw error;
        }
    },

    /**
     * Register a new face
     * @param {string} imageBase64 - Base64 encoded image
     * @param {string} personId - Person's name/ID
     * @returns {Promise<{success: boolean, message: string}>}
     */
    async registerFace(imageBase64, personId) {
        try {
            const response = await fetch(`${API_BASE}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: imageBase64,
                    person_id: personId
                })
            });
            return await response.json();
        } catch (error) {
            console.error('Registration error:', error);
            return { success: false, message: error.message };
        }
    },

    /**
     * Get list of registered faces
     * @returns {Promise<{registered_faces: string[], count: number}>}
     */
    async getRegisteredFaces() {
        try {
            const response = await fetch(`${API_BASE}/registered-faces`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            if (!response.ok) throw new Error('Failed to fetch faces');
            return await response.json();
        } catch (error) {
            console.error('Get faces error:', error);
            return { registered_faces: [], count: 0 };
        }
    },

    /**
     * Get access logs
     * @param {number} count - Number of logs to retrieve (default 10)
     * @returns {Promise<{logs: array, count: number}>}
     */
    async getLogs(count = 10) {
        try {
            const response = await fetch(`${API_BASE}/logs?count=${count}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            if (!response.ok) throw new Error('Failed to fetch logs');
            return await response.json();
        } catch (error) {
            console.error('Get logs error:', error);
            return { logs: [], count: 0 };
        }
    },

    /**
     * Get access statistics
     * @returns {Promise<object>} - Statistics object
     */
    async getStatistics() {
        try {
            const response = await fetch(`${API_BASE}/statistics`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            if (!response.ok) throw new Error('Failed to fetch statistics');
            return await response.json();
        } catch (error) {
            console.error('Get statistics error:', error);
            return {
                total_attempts: 0,
                granted: 0,
                denied: 0,
                blocked_threats: 0
            };
        }
    },

    /**
     * Reset all logs
     * @returns {Promise<{success: boolean, message: string}>}
     */
    async resetLogs() {
        try {
            const response = await fetch(`${API_BASE}/reset`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            return await response.json();
        } catch (error) {
            console.error('Reset error:', error);
            return { success: false, message: error.message };
        }
    },

    /**
     * Capture frame from video element as base64
     * @param {HTMLVideoElement} videoElement 
     * @returns {string} Base64 encoded image
     */
    captureFrame(videoElement) {
        const canvas = document.createElement('canvas');
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoElement, 0, 0);
        return canvas.toDataURL('image/jpeg', 0.8);
    }
};

// ==================== CONNECTION STATUS ====================
const ConnectionStatus = {
    isOnline: false,
    lastCheck: null,

    async check() {
        const result = await ApiService.healthCheck();
        this.isOnline = result.status === 'online';
        this.lastCheck = new Date();
        return this.isOnline;
    },

    updateUI() {
        const indicator = document.getElementById('connectionStatus');
        if (indicator) {
            indicator.className = `connection-status ${this.isOnline ? 'online' : 'offline'}`;
            indicator.textContent = this.isOnline ? 'Backend Online' : 'Backend Offline';
        }
    }
};

// Export for use in other scripts
window.ApiService = ApiService;
window.ConnectionStatus = ConnectionStatus;

console.log('🔌 API Service loaded');
