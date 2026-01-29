/**
 * AI Smart Sentinel - System Settings
 * Slider updates, save/reset actions, and confirmation dialogs
 */

document.addEventListener('DOMContentLoaded', () => {
    initSliders();
    initActionButtons();
});

// ==================== SLIDER CONTROLS ====================
function initSliders() {
    const sliders = [
        { id: 'injectionSlider', valueId: 'injectionValue' },
        { id: 'deepfakeSlider', valueId: 'deepfakeValue' },
        { id: 'faceMatchSlider', valueId: 'faceMatchValue' }
    ];

    sliders.forEach(({ id, valueId }) => {
        const slider = document.getElementById(id);
        const valueDisplay = document.getElementById(valueId);

        if (slider && valueDisplay) {
            slider.addEventListener('input', () => {
                valueDisplay.textContent = slider.value + '%';
            });
        }
    });
}

// ==================== ACTION BUTTONS ====================
function initActionButtons() {
    const saveBtn = document.getElementById('saveBtn');
    const resetBtn = document.getElementById('resetBtn');
    const testBtn = document.getElementById('testBtn');
    const factoryResetBtn = document.getElementById('factoryResetBtn');

    // Save Changes
    saveBtn.addEventListener('click', () => {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="loading"></span> Saving...';

        setTimeout(() => {
            saveBtn.innerHTML = '✓ Saved!';
            saveBtn.style.background = 'var(--accent-green)';

            setTimeout(() => {
                saveBtn.innerHTML = 'Save Changes';
                saveBtn.style.background = '';
                saveBtn.disabled = false;
            }, 2000);
        }, 1000);
    });

    // Reset to Default
    resetBtn.addEventListener('click', () => {
        const confirmed = confirm('Reset all settings to default values?');
        if (confirmed) {
            // Reset sliders
            document.getElementById('injectionSlider').value = 15;
            document.getElementById('injectionValue').textContent = '15%';

            document.getElementById('deepfakeSlider').value = 70;
            document.getElementById('deepfakeValue').textContent = '70%';

            document.getElementById('faceMatchSlider').value = 85;
            document.getElementById('faceMatchValue').textContent = '85%';

            // Reset timeout
            document.getElementById('timeout').value = 30;

            // Reset model
            document.getElementById('aiModel').value = 'v2.5';

            // Visual feedback
            resetBtn.innerHTML = '✓ Reset Complete';
            setTimeout(() => {
                resetBtn.innerHTML = 'Reset to Default';
            }, 1500);
        }
    });

    // Test Configuration
    testBtn.addEventListener('click', () => {
        testBtn.disabled = true;
        testBtn.innerHTML = '<span class="loading"></span> Testing...';

        setTimeout(() => {
            testBtn.innerHTML = '✓ Test Passed!';
            testBtn.style.background = 'var(--accent-green)';
            testBtn.style.borderColor = 'var(--accent-green)';
            testBtn.style.color = 'black';

            setTimeout(() => {
                testBtn.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="5 3 19 12 5 21 5 3"/>
                    </svg>
                    Test Configuration
                `;
                testBtn.style.background = '';
                testBtn.style.borderColor = '';
                testBtn.style.color = '';
                testBtn.disabled = false;
            }, 2000);
        }, 2000);
    });

    // Factory Reset
    factoryResetBtn.addEventListener('click', () => {
        const firstConfirm = confirm(
            '⚠️ FACTORY RESET\n\n' +
            'This will erase ALL settings and return the system to factory defaults.\n\n' +
            'This action cannot be undone.\n\n' +
            'Are you sure you want to continue?'
        );

        if (firstConfirm) {
            const secondConfirm = confirm(
                '🚨 FINAL WARNING\n\n' +
                'Type "RESET" in the next prompt to confirm factory reset.'
            );

            if (secondConfirm) {
                const typed = prompt('Type RESET to confirm:');
                if (typed === 'RESET') {
                    factoryResetBtn.innerHTML = '🔄 Resetting...';
                    factoryResetBtn.disabled = true;

                    setTimeout(() => {
                        alert('✅ Factory reset complete.\n\nThe system will reload.');
                        window.location.reload();
                    }, 2000);
                } else {
                    alert('Factory reset cancelled.');
                }
            }
        }
    });
}
