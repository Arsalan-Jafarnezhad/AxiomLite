document.addEventListener("DOMContentLoaded", () => {
    const articleCards = document.querySelectorAll(".weblog-article-reveal");

    if (articleCards.length) {
        const observer = new IntersectionObserver(
            (entries, observer) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) {
                        return;
                    }

                    entry.target.classList.add("is-visible");

                    observer.unobserve(entry.target);
                });
            },
            {
                threshold: 0.08,
                rootMargin: "0px 0px -40px 0px",
            },
        );

        articleCards.forEach((card) => {
            observer.observe(card);
        });
    }
    document.querySelectorAll('#weblog-home a[href^="#"]').forEach((link) => {
        link.addEventListener("click", (event) => {
            const targetId = link.getAttribute("href");

            if (!targetId || targetId === "#") {
                return;
            }

            const target = document.querySelector(targetId);

            if (!target) {
                return;
            }

            event.preventDefault();

            target.scrollIntoView({
                behavior: "smooth",
                block: "start",
            });
        });
    });

    const hero = document.querySelector(".weblog-hero");

    const heroIcon = document.querySelector(".weblog-hero-icon");

    if (
        hero &&
        heroIcon &&
        !window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
        hero.addEventListener("pointermove", (event) => {
            const rect = hero.getBoundingClientRect();

            const x = (event.clientX - rect.left) / rect.width - 0.5;

            const y = (event.clientY - rect.top) / rect.height - 0.5;

            heroIcon.style.transform = `translate(${x * 8}px, ${y * 8}px)`;
        });

        hero.addEventListener("pointerleave", () => {
            heroIcon.style.transform = "";
        });
    }
});
