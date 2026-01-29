/**
 * AI Smart Sentinel - Incident Detail Modal
 * Keyboard controls, heatmap toggle, and action handlers
 */

document.addEventListener('DOMContentLoaded', () => {
    initModal();
    initHeatmapToggle();
    initActionButtons();
});

// ==================== MODAL CONTROLS ====================
function initModal() {
    const modal = document.getElementById('incidentModal');
    const closeBtn = document.getElementById('closeModal');

    // Close button
    closeBtn.addEventListener('click', closeModal);

    // ESC key closes modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });

    // Click outside modal closes it
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
}

function closeModal() {
    const modal = document.getElementById('incidentModal');
    modal.classList.remove('active');

    // In production, this would return to the previous page
    setTimeout(() => {
        // Redirect back to analytics or dashboard
        // window.location.href = 'analytics-dashboard.html';
    }, 300);
}

function openModal() {
    const modal = document.getElementById('incidentModal');
    modal.classList.add('active');
}

// ==================== HEATMAP TOGGLE ====================
function initHeatmapToggle() {
    const toggle = document.getElementById('heatmapToggle');
    const preview = document.getElementById('heatmapPreview');

    toggle.addEventListener('change', () => {
        if (toggle.checked) {
            preview.classList.add('overlay-active');
            // Add visual overlay effect
            preview.style.background = 'linear-gradient(135deg, rgba(255, 82, 82, 0.1), rgba(0, 0, 0, 0.5))';
        } else {
            preview.classList.remove('overlay-active');
            preview.style.background = '';
        }
    });
}

// ==================== ACTION BUTTONS ====================
function initActionButtons() {
    const falsePositiveBtn = document.getElementById('falsePositiveBtn');

    // False Positive requires confirmation
    falsePositiveBtn.addEventListener('click', () => {
        const confirmed = confirm(
            '⚠️ Mark as False Positive?\n\n' +
            'This action will be logged with your operator ID.\n\n' +
            'Are you sure this incident is not a threat?'
        );

        if (confirmed) {
            // Update UI
            falsePositiveBtn.innerHTML = '✓ Marked as False Positive';
            falsePositiveBtn.disabled = true;
            falsePositiveBtn.style.background = 'var(--accent-green)';
            falsePositiveBtn.style.borderColor = 'var(--accent-green)';
            falsePositiveBtn.style.color = 'black';

            // Update resolution status
            const resolution = document.getElementById('resolution');
            resolution.value = 'resolved';

            // Show confirmation
            console.log('📋 Incident marked as false positive. Logged to audit trail.');
        }
    });

    // Download Evidence
    const buttons = document.querySelectorAll('.modal-footer .btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Skip false positive button (handled separately)
            if (btn.id === 'falsePositiveBtn') return;

            const text = btn.textContent.trim();

            // Simulate action feedback
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<span class="loading"></span> Processing...';
            btn.disabled = true;

            setTimeout(() => {
                btn.innerHTML = '✓ ' + text.split('\n').pop().trim();

                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                    btn.disabled = false;
                }, 1500);
            }, 1000);
        });
    });
}

// ==================== AUTOSAVE NOTES ====================
const notesInput = document.querySelector('.notes-input');
let saveTimeout;

if (notesInput) {
    notesInput.addEventListener('input', () => {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            console.log('📝 Notes autosaved:', notesInput.value.substring(0, 50) + '...');
        }, 1000);
    });
}
