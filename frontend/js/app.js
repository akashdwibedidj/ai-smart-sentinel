const API_BASE = 'http://localhost:5000/api';

// ========================================
// INITIALIZATION & BOOT
// ========================================
window.onload = () => {
    initSplash();
    initBackgroundParticles();
    initDigitalService();
    setupEliteInteractions();
    initAetherInteractions(); // Advanced Mouse & Parallax
};

// ========================================
// DIGITAL SERVICE (Clock & Date)
// ========================================
function initDigitalService() {
    const clockEl = document.getElementById('digitalclock');
    const dateEl = document.getElementById('digitaldate');

    const update = () => {
        const now = new Date();

        // Precise Time with leading zeros
        const h = String(now.getHours()).padStart(2, '0');
        const m = String(now.getMinutes()).padStart(2, '0');
        const s = String(now.getSeconds()).padStart(2, '0');
        if (clockEl) clockEl.textContent = `${h}:${m}:${s}`;

        // Precise Date format consistent with Sketch
        if (dateEl) {
            const days = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'];
            const months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
            const dayName = days[now.getDay()];
            const monthName = months[now.getMonth()];
            const dateStr = `${dayName}, ${monthName} ${now.getDate()}, ${now.getFullYear()}`;
            dateEl.textContent = dateStr;
        }
    };

    update();
    setInterval(update, 1000);
}

// ========================================
// AETHER ADVANCED INTERACTIONS
// ========================================
function initAetherInteractions() {
    const mouseGlow = document.getElementById('mouse-glow');
    const parallaxCards = document.querySelectorAll('.parallax-card');

    window.addEventListener('mousemove', (e) => {
        // 1. Mouse Glow Position
        if (mouseGlow) {
            mouseGlow.style.left = e.clientX + 'px';
            mouseGlow.style.top = e.clientY + 'px';
        }

        // 2. Parallax Cards Effect
        parallaxCards.forEach(card => {
            const rect = card.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;

            const dx = e.clientX - centerX;
            const dy = e.clientY - centerY;

            // Calculate distance for subtle rotation
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 400) {
                const tiltX = (dy / 25).toFixed(2);
                const tiltY = (-(dx / 25)).toFixed(2);
                card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) translateY(-15px)`;
            } else {
                card.style.transform = `perspective(1000px) rotateX(0) rotateY(0) translateY(0)`;
            }
        });
    });
}

// ========================================
// SPLASH & MATRIX ENGINE
// ========================================
function initSplash() {
    const splash = document.getElementById('splashScreen');
    const mCanvas = document.getElementById('matrixCanvas');
    if (!splash || !mCanvas) return;

    const ctx = mCanvas.getContext('2d');
    const chars = '01ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ';
    const charArray = chars.split('');
    let drops = [];
    let fontSize = 16;

    function resize() {
        mCanvas.width = window.innerWidth;
        mCanvas.height = window.innerHeight;
        let columns = Math.floor(mCanvas.width / fontSize);
        for (let i = 0; i < columns; i++) {
            if (drops[i] === undefined) drops[i] = Math.random() * -150;
        }
    }
    window.addEventListener('resize', resize);
    resize();

    function draw() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.08)';
        ctx.fillRect(0, 0, mCanvas.width, mCanvas.height);
        ctx.fillStyle = '#0066FF';
        ctx.font = fontSize + 'px monospace';
        for (let i = 0; i < drops.length; i++) {
            const text = charArray[Math.floor(Math.random() * charArray.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            if (drops[i] * fontSize > mCanvas.height && Math.random() > 0.975) drops[i] = 0;
            drops[i]++;
        }
    }
    const interval = setInterval(draw, 35);

    setTimeout(() => {
        splash.classList.add('fade-out');
        setTimeout(() => {
            splash.style.display = 'none';
            clearInterval(interval);
        }, 1200);
    }, 3000);
}

// ========================================
// AETHER NATURE PARTICLES (Background)
// ========================================
function initBackgroundParticles() {
    const canvas = document.getElementById('bg-particles');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];
    let pollens = [];
    let birds = [];
    let petals = [];
    const count = 40;
    const birdCount = 3;
    const petalCount = 8;
    let mouse = { x: -1000, y: -1000 };
    window.addEventListener('mousemove', e => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
        // 1. Create Pollen on Move
        if (Math.random() > 0.4) pollens.push(new Pollen(e.clientX, e.clientY));
    });

    class Petal {
        constructor() { this.init(); }
        init() {
            this.x = Math.random() * canvas.width;
            this.y = -20;
            this.size = Math.random() * 5 + 5;
            this.speedX = Math.random() * 1 - 0.5;
            this.speedY = Math.random() * 1 + 0.5;
            this.opacity = Math.random() * 0.4 + 0.2;
            this.angle = Math.random() * 360;
            this.spin = Math.random() * 1 - 0.5;
        }
        update() {
            this.x += this.speedX + Math.sin(this.y / 100);
            this.y += this.speedY;
            this.angle += this.spin;
            if (this.y > canvas.height + 20) this.init();
        }
        draw() {
            ctx.save();
            ctx.translate(this.x, this.y);
            ctx.rotate(this.angle * Math.PI / 180);
            ctx.globalAlpha = this.opacity;
            ctx.fillStyle = '#BC00FF'; // Cyber Purple Energy Fragment
            ctx.beginPath();
            ctx.ellipse(0, 0, this.size, this.size / 2, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }

    class Pollen {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.vx = (Math.random() - 0.5) * 2;
            this.vy = (Math.random() - 0.5) * 2;
            this.age = 0;
            this.maxAge = Math.random() * 50 + 50;
            this.color = '#00F0FF'; // Cyan Energy Dust
        }
        update() {
            this.x += this.vx;
            this.y += this.vy;
            this.age++;
            this.vx *= 0.98;
            this.vy *= 0.98;
        }
        draw() {
            const alpha = 1 - (this.age / this.maxAge);
            ctx.globalAlpha = alpha * 0.4;
            ctx.fillStyle = this.color;
            ctx.beginPath();
            ctx.arc(this.x, this.y, 5, 0, Math.PI * 2); // Increased further from 3 to 5
            ctx.fill();
        }
    }

    class Bird {
        constructor() {
            this.init();
        }
        init() {
            this.x = -100;
            this.y = Math.random() * canvas.height;
            this.vx = Math.random() * 2 + 1;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.flap = 0;
        }
        update() {
            this.x += this.vx;
            this.y += this.vy;
            this.flap += 0.15;

            // Interaction: Avoid mouse
            let dx = mouse.x - this.x;
            let dy = mouse.y - this.y;
            let dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 150) {
                this.vy += dy < 0 ? 0.2 : -0.2;
                this.vx += 0.1;
            }

            if (this.x > canvas.width + 100) this.init();
        }
        draw() {
            ctx.globalAlpha = 0.6;
            ctx.strokeStyle = '#FFFFFF'; // White Cyber Silhouette
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            const wingY = Math.sin(this.flap) * 8;
            // Left wing
            ctx.moveTo(this.x, this.y);
            ctx.lineTo(this.x - 10, this.y - wingY);
            // Right wing
            ctx.moveTo(this.x, this.y);
            ctx.lineTo(this.x + 10, this.y - wingY);
            ctx.stroke();
        }
    }

    class Particle {
        constructor() { this.init(); }
        init() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height + canvas.height; // Start from bottom
            this.size = Math.random() * 6 + 4; // Increased further from 4+2 to 6+4
            this.speedX = Math.random() * 1 - 0.5;
            this.speedY = Math.random() * -0.5 - 0.2; // Move upwards
            this.color = Math.random() > 0.5 ? '#0066FF' : '#BC00FF';
            this.opacity = Math.random() * 0.3 + 0.1;
            this.growth = Math.random() * 0.01;
        }

        draw() {
            ctx.fillStyle = this.color;
            ctx.globalAlpha = this.opacity;
            ctx.beginPath();
            // Create a "Dandelion" soft star shape
            for (let i = 0; i < 5; i++) {
                ctx.moveTo(this.x, this.y);
                ctx.lineTo(this.x + Math.cos(i) * this.size * 2, this.y + Math.sin(i) * this.size * 2);
            }
            ctx.strokeStyle = this.color;
            ctx.lineWidth = 0.5;
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size / 2, 0, Math.PI * 2);
            ctx.fill();
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            // Mouse interaction (repel softly)
            let dx = mouse.x - this.x;
            let dy = mouse.y - this.y;
            let distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < 150) {
                this.x -= dx / 50;
                this.y -= dy / 50;
            }

            // Reset if out of bounds
            if (this.y < -50) {
                this.y = canvas.height + 50;
                this.x = Math.random() * canvas.width;
            }
        }
    }

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    for (let i = 0; i < count; i++) particles.push(new Particle());
    for (let i = 0; i < birdCount; i++) birds.push(new Bird());
    for (let i = 0; i < petalCount; i++) petals.push(new Petal());

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Update & Draw Particles (Dandelions)
        for (let i = 0; i < particles.length; i++) {
            particles[i].draw();
            particles[i].update();
        }

        // Update & Draw Pollen
        pollens = pollens.filter(p => p.age < p.maxAge);
        pollens.forEach(p => {
            p.draw();
            p.update();
        });

        // Update & Draw Birds
        birds.forEach(b => {
            b.draw();
            b.update();
        });

        // Update & Draw Petals
        petals.forEach(p => {
            p.draw();
            p.update();
        });

        requestAnimationFrame(animate);
    }
    animate();
}

// ========================================
// ELITE INTERACTIONS & PORTAL LOGIC
// ========================================
function setupEliteInteractions() {
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const loginCard = document.getElementById('loginCard');
    const errorOverlay = document.getElementById('errorOverlay');
    const retryBtn = document.getElementById('retryBtn');
    const togglePassBtn = document.getElementById('togglePassword');
    const passInput = document.getElementById('password');
    const scanLine = document.querySelector('.scan-line');

    // Password Toggle
    if (togglePassBtn && passInput) {
        togglePassBtn.addEventListener('click', () => {
            const type = passInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passInput.setAttribute('type', type);
            togglePassBtn.classList.toggle('active');
        });
    }

    // Register Button (Placeholder)
    if (registerBtn) {
        registerBtn.addEventListener('click', () => {
            alert('REGISTRATION SERVICE: UNAVAILABLE\nRemote link initialization failed. Please contact your administrator.');
        });
    }

    // Reset Terminal logic (Button)
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
            document.getElementById('rememberMe').checked = false;
        });
    }

    // Main Login Logic
    if (loginBtn) {
        loginBtn.addEventListener('click', async () => {
            const user = document.getElementById('username').value;
            const pass = document.getElementById('password').value;

            if (!user || !pass) {
                loginCard.classList.add('shake-anim');
                setTimeout(() => loginCard.classList.remove('shake-anim'), 500);
                return;
            }

            // Trigger Intensive Security Scan Animation
            if (scanLine) {
                scanLine.style.animation = 'none';
                void scanLine.offsetWidth; // trigger reflow
                scanLine.style.animation = 'scanVertical 1s cubic-bezier(0.19, 1, 0.22, 1)';
                scanLine.style.opacity = '1';
                scanLine.style.height = '15px';
            }

            // Energy Pulse Energy click interaction
            const pulseContainer = loginBtn.querySelector('.energy-pulse-container');
            if (pulseContainer) {
                const pulse = document.createElement('div');
                pulse.className = 'energy-pulse';
                pulseContainer.appendChild(pulse);
                setTimeout(() => pulse.remove(), 600);
            }

            loginBtn.classList.add('verifying');
            loginBtn.querySelector('.btn-text').textContent = 'INITIALIZING PROTOCOL...';

            // Artificial Delay for the Scan Effect
            await new Promise(resolve => setTimeout(resolve, 1200));

            try {
                let data;
                // --- DEMO BYPASS ---
                if (user === 'admin' && pass === 'sentinel2026') {
                    data = { success: true };
                } else {
                    const res = await fetch(`${API_BASE}/login`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username: user, password: pass })
                    });
                    data = await res.json();
                }
                // --- END DEMO BYPASS ---

                if (data.success) {
                    // Successful Authentication
                    loginBtn.style.background = 'var(--nature-green)';
                    loginBtn.querySelector('.btn-text').textContent = 'VERIFICATION GRANTED';
                    setTimeout(() => {
                        window.location.href = 'main-dashboard.html';
                    }, 1200);
                } else {
                    handleLoginError();
                }
            } catch (e) {
                handleLoginError();
            } finally {
                // Reset Scan Line state
                if (scanLine) {
                    setTimeout(() => {
                        scanLine.style.animation = 'scanVertical 8s infinite linear';
                        scanLine.style.opacity = '0.4';
                        scanLine.style.height = '3px';
                    }, 500);
                }
            }
        });
    }

    function handleLoginError() {
        // Shake animation for physical feedback
        if (loginCard) {
            loginCard.classList.add('shake-anim');
            setTimeout(() => loginCard.classList.remove('shake-anim'), 500);
        }

        // Full Page Error Transition (Designer Request)
        if (errorOverlay) {
            errorOverlay.classList.remove('hidden');
        }

        // Reset Primary Button State
        loginBtn.classList.remove('verifying');
        loginBtn.querySelector('.btn-text').textContent = 'LOGIN';
    }

    // Error Screen 'Try Again' Action
    if (retryBtn) {
        retryBtn.addEventListener('click', () => {
            if (errorOverlay) {
                errorOverlay.style.opacity = '0';
                setTimeout(() => {
                    errorOverlay.classList.add('hidden');
                    errorOverlay.style.opacity = '1';
                }, 300);
            }
        });
    }
}
