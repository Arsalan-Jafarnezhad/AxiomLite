document.addEventListener("DOMContentLoaded", () => {
    const prefersReducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
    ).matches;

    document.querySelectorAll(".footer-social").forEach((item, index) => {
        item.style.animationDelay = `${index * 70}ms`;

        if (prefersReducedMotion) return;

        item.addEventListener("mouseenter", () => {
            item.animate(
                [
                    { transform: "translateY(0)" },
                    { transform: "translateY(-8px) scale(1.08)" },
                ],
                { duration: 220, easing: "ease-out" },
            );
        });
    });

    const backToTop = document.getElementById("backToTop");
    if (backToTop) {
        const toggleVisibility = () => {
            backToTop.classList.toggle("show", window.scrollY > 400);
        };
        toggleVisibility();
        window.addEventListener("scroll", toggleVisibility, { passive: true });

        backToTop.addEventListener("click", () => {
            window.scrollTo({
                top: 0,
                behavior: prefersReducedMotion ? "auto" : "smooth",
            });
        });
    }

    const newsletterForm = document.querySelector(".newsletter-form");
    const feedback = document.querySelector(".newsletter-feedback");

    if (newsletterForm && feedback) {
        newsletterForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const emailInput = newsletterForm.querySelector(
                "input[name='email']",
            );
            const submitBtn = newsletterForm.querySelector(
                "button[type='submit']",
            );

            if (!emailInput.value || !emailInput.checkValidity()) {
                feedback.textContent = "Please enter a valid email address.";
                feedback.className =
                    "newsletter-feedback text-sm mt-3 text-center lg:text-left error";
                return;
            }

            submitBtn.disabled = true;

            try {
                const response = await fetch(newsletterForm.action, {
                    method: "POST",
                    body: new FormData(newsletterForm),
                    headers: { "X-Requested-With": "XMLHttpRequest" },
                });

                if (response.ok) {
                    feedback.textContent =
                        "Thanks! Check your inbox to confirm your subscription.";
                    feedback.className =
                        "newsletter-feedback text-sm mt-3 text-center lg:text-left success";
                    newsletterForm.reset();
                } else {
                    throw new Error("Request failed");
                }
            } catch (error) {
                feedback.textContent =
                    "Something went wrong. Please try again later.";
                feedback.className =
                    "newsletter-feedback text-sm mt-3 text-center lg:text-left error";
            } finally {
                submitBtn.disabled = false;
            }
        });
    }
});
