document.addEventListener("DOMContentLoaded", () => {
    const prefersReducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
    ).matches;

    const statValues = document.querySelectorAll(".stat-value[data-count]");

    const animateCount = (el) => {
        const target = parseInt(el.dataset.count, 10);
        if (Number.isNaN(target)) return;

        if (prefersReducedMotion || target === 0) {
            el.textContent = target.toLocaleString();
            return;
        }

        const duration = 900;
        const start = performance.now();

        const step = (now) => {
            const progress = Math.min((now - start) / duration, 1);
            el.textContent = Math.round(target * progress).toLocaleString();
            if (progress < 1) requestAnimationFrame(step);
        };

        requestAnimationFrame(step);
    };

    if (statValues.length) {
        const counterObserver = new IntersectionObserver(
            (entries, obs) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) return;
                    animateCount(entry.target);
                    obs.unobserve(entry.target);
                });
            },
            { threshold: 0.4 },
        );

        statValues.forEach((el) => counterObserver.observe(el));
    }

    if (!prefersReducedMotion) {
        document.querySelectorAll(".badge-pop").forEach((badge, index) => {
            badge.style.animationDelay = `${index * 80}ms`;
        });
    }
});
