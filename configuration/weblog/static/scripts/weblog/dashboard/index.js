document.addEventListener("DOMContentLoaded", () => {
    const dashboard = document.querySelector("#weblog-dashboard");

    if (!dashboard) {
        return;
    }

    const counters = dashboard.querySelectorAll(".dashboard-stat-value");

    counters.forEach((counter) => {
        const target = Number(counter.textContent.trim());

        if (!Number.isFinite(target) || target <= 0) {
            return;
        }

        const duration = 650;

        const start = performance.now();

        function animate(currentTime) {
            const progress = Math.min((currentTime - start) / duration, 1);

            const eased = 1 - Math.pow(1 - progress, 3);

            const value = Math.floor(target * eased);

            counter.textContent = value.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                counter.textContent = target.toLocaleString();
            }
        }

        counter.textContent = "0";

        requestAnimationFrame(animate);
    });

    dashboard.querySelectorAll("a").forEach((link) => {
        link.addEventListener("focus", () => {
            link.classList.add("dashboard-link-focused");
        });

        link.addEventListener("blur", () => {
            link.classList.remove("dashboard-link-focused");
        });
    });
});
