document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".account-card");

    if (!cards.length) {
        return;
    }

    document.querySelectorAll(".quick-action").forEach((link) => {
        link.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();

                link.click();
            }
        });
    });

    document.querySelectorAll('a[href*="/profile/"]').forEach((link) => {
        link.addEventListener("click", () => {
            link.classList.add("loading");
        });
    });

    const username = document.querySelector("[data-copy-username]");

    if (username) {
        username.style.cursor = "copy";

        username.title = "Click to copy username";

        username.addEventListener("click", async () => {
            const value = username.dataset.copyUsername;

            if (!value) {
                return;
            }

            try {
                await navigator.clipboard.writeText(value);

                const original = username.textContent;

                username.textContent = "Copied!";

                setTimeout(() => {
                    username.textContent = original;
                }, 1200);
            } catch {}
        });
    }
});
