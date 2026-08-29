import { initializeCodeBlocks } from "./code-blocks.js";

document.addEventListener("DOMContentLoaded", () => {
    const article = document.getElementById("article-content");
    const progressBar = document.getElementById("article-progress-bar");

    const copyButton = document.getElementById("copy-article-link");
    const shareButton = document.getElementById("share-article");
    const backToTop = document.getElementById("back-to-top");

    async function copyText(text) {
        if (navigator.clipboard) {
            await navigator.clipboard.writeText(text);
            return;
        }

        const textarea = document.createElement("textarea");

        textarea.value = text;

        textarea.style.position = "fixed";
        textarea.style.opacity = "0";

        document.body.appendChild(textarea);

        textarea.select();
        document.execCommand("copy");

        textarea.remove();
    }

    function updateProgress() {
        if (!article || !progressBar) {
            return;
        }

        const start = article.offsetTop;
        const height = article.offsetHeight - window.innerHeight;

        if (height <= 0) {
            progressBar.style.width = "100%";
            return;
        }

        const progress = ((window.scrollY - start) / height) * 100;

        progressBar.style.width = `${Math.min(100, Math.max(0, progress))}%`;
    }

    let ticking = false;

    function requestProgressUpdate() {
        if (ticking) {
            return;
        }

        ticking = true;

        requestAnimationFrame(() => {
            updateProgress();
            ticking = false;
        });
    }

    window.addEventListener("scroll", requestProgressUpdate, { passive: true });

    window.addEventListener("resize", updateProgress);

    updateProgress();

    async function showTemporaryState(button, icon, text, duration = 1600) {
        const original = button.innerHTML;

        button.innerHTML = `
            <span class="material-symbols-rounded text-lg">
                ${icon}
            </span>

            <span class="hidden sm:inline">
                ${text}
            </span>
        `;

        window.setTimeout(() => {
            button.innerHTML = original;
        }, duration);
    }

    copyButton?.addEventListener("click", async () => {
        try {
            await copyText(window.location.href);

            await showTemporaryState(copyButton, "check", "Copied");
        } catch (error) {
            console.error("Unable to copy article URL:", error);
        }
    });

    shareButton?.addEventListener("click", async () => {
        const title =
            document.querySelector(".article-title")?.textContent?.trim() ||
            document.title;

        const shareData = {
            title,
            text: title,
            url: window.location.href,
        };

        if (
            navigator.share &&
            (!navigator.canShare || navigator.canShare(shareData))
        ) {
            try {
                await navigator.share(shareData);
            } catch (error) {
                if (error.name !== "AbortError") {
                    console.error("Share failed:", error);
                }
            }

            return;
        }

        try {
            await copyText(window.location.href);

            await showTemporaryState(shareButton, "check", "Link copied");
        } catch (error) {
            console.error("Unable to copy URL:", error);
        }
    });

    backToTop?.addEventListener("click", () => {
        window.scrollTo({
            top: 0,
            behavior: "smooth",
        });
    });

    if (article) {
        initializeCodeBlocks(article);
    }
});
