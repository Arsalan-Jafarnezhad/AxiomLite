document.addEventListener("DOMContentLoaded", () => {
    const prefersReducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
    ).matches;

    const form = document.querySelector("form");
    const submitButton = document.getElementById("submit-btn");

    const emailInput = document.getElementById("login-email");
    const passwordInput = document.getElementById("login-password");

    emailInput?.focus();

    if (passwordInput) {
        const wrapper = passwordInput.parentElement;

        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.setAttribute("aria-label", "Show password");
        toggle.className =
            "absolute right-4 top-1/2 -translate-y-1/2 text-base-content/50 hover:text-primary transition";
        toggle.innerHTML = '<i class="fa-solid fa-eye"></i>';

        wrapper.appendChild(toggle);

        toggle.addEventListener("click", () => {
            const hidden = passwordInput.type === "password";
            passwordInput.type = hidden ? "text" : "password";
            toggle.setAttribute(
                "aria-label",
                hidden ? "Hide password" : "Show password",
            );
            toggle.innerHTML = hidden
                ? '<i class="fa-solid fa-eye-slash"></i>'
                : '<i class="fa-solid fa-eye"></i>';
        });
    }

    if (passwordInput) {
        const container =
            passwordInput.closest(".space-y-2") || passwordInput.parentElement;

        const warning = document.createElement("div");
        warning.className = "hidden mt-2 text-warning text-sm font-medium";
        warning.innerHTML =
            '<i class="fa-solid fa-triangle-exclamation mr-1"></i> Caps Lock is ON';

        container.appendChild(warning);

        passwordInput.addEventListener("keyup", (event) => {
            warning.classList.toggle(
                "hidden",
                !event.getModifierState("CapsLock"),
            );
        });
    }

    if (form && submitButton) {
        form.addEventListener("submit", () => {
            submitButton.disabled = true;
            submitButton.innerHTML = `
                <span class="loading loading-spinner loading-sm"></span>
                Signing In...
            `;
        });
    }

    document.addEventListener("keydown", (event) => {
        if (
            event.key === "/" &&
            document.activeElement.tagName !== "INPUT" &&
            document.activeElement.tagName !== "TEXTAREA"
        ) {
            event.preventDefault();
            emailInput?.focus();
        }
    });

    window.addEventListener("pageshow", () => {
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.innerHTML = `
                <i class="fa-solid fa-right-to-bracket"></i>
                Sign In
            `;
        }
    });

    const lines = [
        {
            el: document.querySelector('[data-line="1"]'),
            icon: `<i class="text-green-500 fa fa-circle-check"></i>`,
            text: `Credentials verified`,
        },
        {
            el: document.querySelector('[data-line="2"]'),
            icon: `<i class="text-green-500 fa fa-circle-check"></i>`,
            text: `Session created`,
        },
        {
            el: document.querySelector('[data-line="3"]'),
            icon: `<i class="text-blue-500 fa fa-arrow-right"></i>`,
            text: `Redirecting to dashboard . . .`,
        },
    ].filter((line) => line.el);

    if (lines.length) {
        if (prefersReducedMotion) {
            lines.forEach((line) => {
                line.el.innerHTML = line.text;
            });
        } else {
            const typeLine = (line, onDone) => {
                let i = 0;
                const interval = setInterval(() => {
                    line.el.innerHTML = `${line.icon} `;
                    line.el.innerHTML += line.text.slice(0, i + 1);
                    i += 1;
                    if (i >= line.text.length) {
                        clearInterval(interval);
                        onDone();
                    }
                }, 28);
            };

            const runSequence = (index) => {
                if (index >= lines.length) {
                    setTimeout(() => {
                        lines.forEach((line) => {
                            line.el.innerHTML = "";
                        });
                        runSequence(0);
                    }, 2600);
                    return;
                }
                setTimeout(
                    () => typeLine(lines[index], () => runSequence(index + 1)),
                    400,
                );
            };

            runSequence(0);
        }
    }
});
