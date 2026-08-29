document.addEventListener("DOMContentLoaded", () => {
    const search = document.querySelector("#article-search");
    const filters = document.querySelectorAll(".article-filter");

    const rows = document.querySelectorAll(".article-row");
    const cards = document.querySelectorAll(".mobile-article-card");

    const items = [...rows, ...cards];

    let activeFilter = "all";

    function filterArticles() {
        const query = search?.value.trim().toLowerCase() || "";

        items.forEach((item) => {
            const title = item.dataset.title || "";
            const status = item.dataset.status || "";

            const matchesSearch = !query || title.includes(query);

            const matchesFilter =
                activeFilter === "all" || status === activeFilter;

            item.style.display = matchesSearch && matchesFilter ? "" : "none";
        });
    }

    search?.addEventListener("input", filterArticles);

    filters.forEach((button) => {
        button.addEventListener("click", () => {
            activeFilter = button.dataset.filter || "all";

            filters.forEach((item) => {
                item.classList.remove("btn-primary", "active");

                item.classList.add("btn-ghost");
            });

            button.classList.remove("btn-ghost");

            button.classList.add("btn-primary", "active");

            filterArticles();
        });
    });

    document.addEventListener("keydown", (event) => {
        if (
            event.key === "/" &&
            document.activeElement?.tagName !== "INPUT" &&
            document.activeElement?.tagName !== "TEXTAREA"
        ) {
            event.preventDefault();

            search?.focus();
        }
    });

    filterArticles();
});
