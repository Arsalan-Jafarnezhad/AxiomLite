

document.addEventListener("DOMContentLoaded", () => {
    const statusEl = document.querySelector("[data-copy-status]");

    const announce = (message) => {
        if (!statusEl) return;
        statusEl.textContent = message;
    };

    const copyToClipboard = async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (error) {
            return false;
        }
    };





    const copyBtn = document.querySelector("[data-copy-btn]");

    copyBtn?.addEventListener("click", async () => {
        const value = copyBtn.dataset.copy;
        if (!value) return;

        const ok = await copyToClipboard(value);
        announce(
            ok
                ? `Copied "${value}" to clipboard`
                : "Couldn't copy to clipboard",
        );
    });





    const shareBtn = document.querySelector("[data-share-btn]");

    shareBtn?.addEventListener("click", async () => {
        const shareData = {
            title: document.title,
            url: window.location.href,
        };

        if (navigator.share) {
            try {
                await navigator.share(shareData);
            } catch (error) {
            
            }
            return;
        }

        const ok = await copyToClipboard(shareData.url);
        announce(
            ok ? "Profile link copied to clipboard" : "Couldn't copy the link",
        );
    });
});
