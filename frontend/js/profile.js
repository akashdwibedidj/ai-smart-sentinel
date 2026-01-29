/**
 * AI Smart Sentinel - User Profile
 * Modal control, form interactions, and logout logic
 */

document.addEventListener('DOMContentLoaded', () => {
    initPasswordModal();
    initFormActions();
});

// ==================== PASSWORD MODAL ====================
function initPasswordModal() {
    const modal = document.getElementById('passwordModal');
    const openBtn = document.getElementById('changePasswordBtn');
    const closeBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelPasswordBtn');
    const newPasswordInput = document.getElementById('newPassword');

    // Open modal
    openBtn.addEventListener('click', () => {
        modal.classList.add('active');
    });

    // Close modal
    const closeModal = () => {
        modal.classList.remove('active');
    };

    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);

    // Close on overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Password strength indicator
    if (newPasswordInput) {
        newPasswordInput.addEventListener('input', (e) => {
            updatePasswordStrength(e.target.value);
        });
    }
}

function updatePasswordStrength(password) {
    const strengthBar = document.querySelector('.strength-bar');
    const strengthText = document.querySelector('.strength-text');

    let strength = 0;
    if (password.length >= 8) strength += 25;
    if (/[A-Z]/.test(password)) strength += 25;
    if (/[0-9]/.test(password)) strength += 25;
    if (/[^A-Za-z0-9]/.test(password)) strength += 25;

    // Update bar width
    strengthBar.style.setProperty('--strength', strength + '%');
    strengthBar.style.cssText = `
        --strength: ${strength}%;
    `;

    // Update color and text
    if (strength <= 25) {
        strengthBar.style.background = 'var(--accent-red)';
        strengthText.textContent = 'Weak';
        strengthText.style.color = 'var(--accent-red)';
    } else if (strength <= 50) {
        strengthBar.style.background = 'var(--accent-amber)';
        strengthText.textContent = 'Fair';
        strengthText.style.color = 'var(--accent-amber)';
    } else if (strength <= 75) {
        strengthBar.style.background = 'var(--accent-cyan)';
        strengthText.textContent = 'Good';
        strengthText.style.color = 'var(--accent-cyan)';
    } else {
        strengthBar.style.background = 'var(--accent-green)';
        strengthText.textContent = 'Strong';
        strengthText.style.color = 'var(--accent-green)';
    }

    // Update bar fill
    const bar = document.querySelector('.strength-bar::after');
    strengthBar.innerHTML = `<div style="width: ${strength}%; height: 100%; background: inherit; border-radius: 2px;"></div>`;
}

// ==================== FORM ACTIONS ====================
function initFormActions() {
    const updateBtn = document.getElementById('updateBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    // Update Profile
    updateBtn.addEventListener('click', () => {
        // Simulate save
        updateBtn.disabled = true;
        updateBtn.innerHTML = '<span class="loading"></span> Saving...';

        setTimeout(() => {
            updateBtn.disabled = false;
            updateBtn.innerHTML = '✓ Saved!';
            updateBtn.style.background = 'var(--accent-green)';

            setTimeout(() => {
                updateBtn.innerHTML = 'Update Profile';
                updateBtn.style.background = '';
            }, 2000);
        }, 1000);
    });

    // Cancel
    cancelBtn.addEventListener('click', () => {
        // Reset form to original values
        document.getElementById('fullName').value = 'John Doe';
        document.getElementById('email').value = 'john.doe@company.com';
        document.getElementById('department').value = 'engineering';
    });

    // Logout
    logoutBtn.addEventListener('click', () => {
        const confirmed = confirm('Are you sure you want to logout?');
        if (confirmed) {
            // Redirect to login page
            window.location.href = 'index.html';
        }
    });
}
