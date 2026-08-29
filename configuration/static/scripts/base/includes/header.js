function getCookie(name) {
    const cookies = document.cookie.split(";");

    for (const cookie of cookies) {
        const separator = cookie.indexOf("=");

        if (separator === -1) {
            continue;
        }

        const key = cookie.slice(0, separator).trim();

        if (key !== name) {
            continue;
        }

        return decodeURIComponent(cookie.slice(separator + 1));
    }

    return null;
}

document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme");

    if (savedTheme) {
        document.documentElement.setAttribute("data-theme", savedTheme);
    }

    const currentPath = window.location.pathname;

    document.querySelectorAll(".navbar .menu a").forEach((link) => {
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

    const navbar = document.querySelector(".navbar");

    function updateNavbar() {
        if (!navbar) {
            return;
        }

        if (window.scrollY > 15) {
            navbar.classList.add("shadow-xl");

            navbar.classList.remove("shadow-md");
        } else {
            navbar.classList.remove("shadow-xl");

            navbar.classList.add("shadow-md");
        }
    }

    updateNavbar();

    window.addEventListener("scroll", updateNavbar, {
        passive: true,
    });
});

function signOut() {
    const csrfToken = getCookie("csrftoken");

    fetch(
        `/accounts/sign-out/?next=${encodeURIComponent(
            window.location.pathname,
        )}`,
        {
            method: "POST",

            headers: {
                "X-CSRFToken": csrfToken || "",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
            },
        },
    )
        .then(() => {
            window.location.reload();
        })
        .catch((error) => {
            console.error("Sign out failed:", error);
        });
}

document.querySelectorAll(".sign-out").forEach((element) => {
    element.addEventListener("click", signOut);
});
