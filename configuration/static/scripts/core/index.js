(() => {
    "use strict";

    const twEl = document.getElementById("hm-tw");

    if (twEl) {
        const phrases = [
            "Turn your idea into a Django app.",
            "Ship a REST API your team will love.",
            "Scale from 10 users to 10,000.",
            "Secure, tested, documented — on time.",
            "Production-ready software. No shortcuts.",
        ];

        let phraseIdx = 0;
        let charIdx = 0;
        let deleting = false;
        let pauseTick = 0;
        const PAUSE_AFTER_TYPE = 42;
        const PAUSE_AFTER_DELETE = 8;
        const TYPE_SPEED = 38;
        const DELETE_SPEED = 18;

        function tick() {
            const phrase = phrases[phraseIdx];

            if (!deleting) {
                if (charIdx < phrase.length) {
                    twEl.textContent = phrase.slice(0, ++charIdx);
                    setTimeout(tick, TYPE_SPEED);
                } else {
                    if (++pauseTick < PAUSE_AFTER_TYPE) {
                        setTimeout(tick, TYPE_SPEED);
                    } else {
                        pauseTick = 0;
                        deleting = true;
                        setTimeout(tick, DELETE_SPEED);
                    }
                }
            } else {
                if (charIdx > 0) {
                    twEl.textContent = phrase.slice(0, --charIdx);
                    setTimeout(tick, DELETE_SPEED);
                } else {
                    if (++pauseTick < PAUSE_AFTER_DELETE) {
                        setTimeout(tick, DELETE_SPEED);
                    } else {
                        pauseTick = 0;
                        deleting = false;
                        phraseIdx = (phraseIdx + 1) % phrases.length;
                        setTimeout(tick, TYPE_SPEED);
                    }
                }
            }
        }

        if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
            twEl.textContent = phrases[0];
        } else {
            setTimeout(tick, 800);
        }
    }

    const revealEls = document.querySelectorAll(".hm-reveal");

    if (revealEls.length) {
        const revealObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("hm-visible");
                        revealObserver.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.15 },
        );
        revealEls.forEach((el) => revealObserver.observe(el));
    }

    const skillFills = document.querySelectorAll(".hm-skill-fill");

    if (skillFills.length) {
        const skillObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("hm-animated");
                        skillObserver.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.3 },
        );
        skillFills.forEach((el) => skillObserver.observe(el));
    }

    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener("click", (e) => {
            const id = anchor.getAttribute("href").slice(1);
            const target = document.getElementById(id);
            if (!target) return;
            e.preventDefault();
            target.scrollIntoView({ behavior: "smooth", block: "start" });

            history.pushState(null, "", `#${id}`);
        });
    });

    const countEls = document.querySelectorAll("[data-count]");

    if (countEls.length) {
        const countObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) return;
                    const el = entry.target;
                    const target = parseInt(el.dataset.count, 10);
                    if (isNaN(target)) return;

                    const suffixNode = el.querySelector("span");
                    const suffix = suffixNode ? suffixNode.outerHTML : "";

                    const duration = 1400;
                    const start = performance.now();

                    function update(now) {
                        const elapsed = now - start;
                        const progress = Math.min(elapsed / duration, 1);

                        const eased = 1 - Math.pow(1 - progress, 3);
                        const value = Math.round(eased * target);
                        el.innerHTML = value + suffix;
                        if (progress < 1) requestAnimationFrame(update);
                    }

                    requestAnimationFrame(update);
                    countObserver.unobserve(el);
                });
            },
            { threshold: 0.5 },
        );

        countEls.forEach((el) => countObserver.observe(el));
    }

    const navLinks = document.querySelectorAll("[data-nav-link]");

    if (navLinks.length) {
        const sections = Array.from(navLinks)
            .map((link) => document.getElementById(link.dataset.navLink))
            .filter(Boolean);

        const navObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) return;
                    const id = entry.target.id;
                    navLinks.forEach((link) => {
                        const active = link.dataset.navLink === id;
                        link.classList.toggle("nav-active", active);
                        link.setAttribute(
                            "aria-current",
                            active ? "page" : "false",
                        );
                    });
                });
            },
            { rootMargin: "-40% 0px -55% 0px" },
        );

        sections.forEach((s) => navObserver.observe(s));
    }

    const autoRevealSelectors = [
        "#services .hm-service-card",
        "#projects .hm-project-card",
        "#about .hm-skill-row",
        "#writing .hm-post-card",
        ".hm-process-step",
        ".hm-testimonial-card",
        ".hm-stat-card",
    ];

    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        autoRevealSelectors.forEach((sel, groupIdx) => {
            document.querySelectorAll(sel).forEach((el, i) => {
                el.classList.add("hm-reveal");

                if (i % 4 === 1) el.classList.add("hm-reveal-delay-1");
                if (i % 4 === 2) el.classList.add("hm-reveal-delay-2");
                if (i % 4 === 3) el.classList.add("hm-reveal-delay-3");
            });
        });

        document
            .querySelectorAll(".hm-reveal:not(.hm-visible)")
            .forEach((el) => {
                const obs = new IntersectionObserver(
                    ([entry]) => {
                        if (entry.isIntersecting) {
                            el.classList.add("hm-visible");
                            obs.disconnect();
                        }
                    },
                    { threshold: 0.12 },
                );
                obs.observe(el);
            });
    } else {
        autoRevealSelectors.forEach((sel) => {
            document.querySelectorAll(sel).forEach((el) => {
                el.classList.add("hm-reveal", "hm-visible");
            });
        });
    }
})();
