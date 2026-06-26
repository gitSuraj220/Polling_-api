// Mobile menu toggle
const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const navLinks = document.getElementById('navLinks');
if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
        navLinks.classList.toggle('open');
    });
}

// Navbar shadow on scroll
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (navbar) {
        navbar.style.boxShadow = window.scrollY > 10
            ? '0 2px 16px rgba(0,0,0,0.1)'
            : '0 1px 8px rgba(0,0,0,0.06)';
    }
});

// FAQ accordion
document.querySelectorAll('.faq-q').forEach(btn => {
    btn.addEventListener('click', () => {
        const item = btn.closest('.faq-item');
        const isOpen = item.classList.contains('open');
        // close all in same category
        btn.closest('.faq-items').querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
        if (!isOpen) item.classList.add('open');
    });
});

// Validity tabs — swap pricing
document.querySelectorAll('.vtab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.vtab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        const val = tab.dataset.val;

        document.querySelectorAll('.pt-plan-price').forEach(el => {
            const price = el.dataset['price' + (val === '1year' ? '1year' : '2year')];
            if (price) el.textContent = price;
        });
        document.querySelectorAll('.pt-plan-original').forEach(el => {
            const orig = el.dataset['orig' + (val === '1year' ? '1year' : '2year')];
            if (orig) el.textContent = orig;
        });

        const validityLabel = document.querySelector('.validity-row');
        if (validityLabel) {
            validityLabel.firstChild.textContent = `🕒 Course Validity : ${val === '1year' ? '1 Year' : '2 Years'}`;
        }
    });
});

// Countdown timer — target: 2 days from page load
function startCountdown() {
    const endTime = new Date();
    endTime.setDate(endTime.getDate() + 2);
    endTime.setHours(endTime.getHours() + 10);
    endTime.setMinutes(endTime.getMinutes() + 53);

    const daysEl    = document.getElementById('cd-days');
    const hoursEl   = document.getElementById('cd-hours');
    const minutesEl = document.getElementById('cd-minutes');
    const secondsEl = document.getElementById('cd-seconds');

    if (!daysEl) return;

    function pad(n) { return String(n).padStart(2, '0'); }

    function tick() {
        const diff = endTime - new Date();
        if (diff <= 0) {
            daysEl.textContent = hoursEl.textContent = minutesEl.textContent = secondsEl.textContent = '00';
            return;
        }
        const days    = Math.floor(diff / 86400000);
        const hours   = Math.floor((diff % 86400000) / 3600000);
        const minutes = Math.floor((diff % 3600000) / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        daysEl.textContent    = pad(days);
        hoursEl.textContent   = pad(hours);
        minutesEl.textContent = pad(minutes);
        secondsEl.textContent = pad(seconds);
        setTimeout(tick, 1000);
    }
    tick();
}
startCountdown();

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
        const target = document.querySelector(link.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            navLinks.classList.remove('open');
        }
    });
});
