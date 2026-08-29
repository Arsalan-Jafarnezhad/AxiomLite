document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("sidebar");
    const sidebarToggle = document.getElementById("sidebar-toggle");

    const SIDEBAR_COOKIE = "sidebar_state";

    function getCookie(name) {
        const cookies = document.cookie.split("; ");

        for (const cookie of cookies) {
            const separator = cookie.indexOf("=");

            if (separator === -1) {
                continue;
            }

            const key = cookie.slice(0, separator);
            const value = cookie.slice(separator + 1);

            if (key === name) {
                return decodeURIComponent(value);
            }
        }

        return null;
    }

    function setCookie(name, value) {
        document.cookie =
            `${name}=${encodeURIComponent(value)}; ` +
            "path=/; " +
            "SameSite=Lax";
    }

    function getSidebarState() {
        const state = getCookie(SIDEBAR_COOKIE);

        if (state !== "open" && state !== "closed") {
            return "closed";
        }

        return state;
    }

    function applySidebarState() {
        if (!sidebar) {
            return;
        }

        const state = getSidebarState();

        sidebar.classList.toggle("sidebar-closed", state === "closed");
    }

    function toggleSidebar() {
        const currentState = getSidebarState();

        const nextState = currentState === "open" ? "closed" : "open";

        setCookie(SIDEBAR_COOKIE, nextState);

        applySidebarState();
    }

    if (sidebar) {
        applySidebarState();
    }

    if (sidebar && sidebarToggle) {
        sidebarToggle.addEventListener("click", toggleSidebar);
    }

    const currentPath = window.location.pathname;

    document.querySelectorAll(".menu a").forEach((link) => {
        try {
            const href = new URL(link.href, window.location.origin).pathname;

            if (
                currentPath === href ||
                (href !== "/" && currentPath.startsWith(href))
            ) {
                link.classList.add("active", "font-bold");
            }
        } catch {}
    });
});
