document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("comment-search");

    const sortSelect = document.getElementById("comment-sort");

    const commentList = document.getElementById("comment-list");

    const noResults = document.getElementById("comment-no-results");

    const filters = [...document.querySelectorAll(".comment-filter")];

    const deleteDialog = document.getElementById("delete-comment-dialog");

    const deleteConfirm = deleteDialog?.querySelector("[data-delete-confirm]");

    const deleteCancel = deleteDialog?.querySelector("[data-delete-cancel]");

    let activeFilter = "all";

    let pendingDeleteForm = null;

    function getCards() {
        return [...document.querySelectorAll(".comment-card")];
    }

    function normalize(value) {
        return value.toLowerCase().trim();
    }

    function matchesFilter(card) {
        if (activeFilter === "all") {
            return true;
        }

        return card.dataset.status === activeFilter;
    }

    function matchesSearch(card) {
        const query = normalize(searchInput?.value || "");

        if (!query) {
            return true;
        }

        return normalize(card.dataset.search || "").includes(query);
    }

    function sortCards() {
        if (!commentList) {
            return;
        }

        const mode = sortSelect?.value || "newest";

        const cards = getCards();

        cards.sort((a, b) => {
            if (mode === "author") {
                return (a.dataset.author || "").localeCompare(
                    b.dataset.author || "",
                );
            }

            const dateA = Number(a.dataset.date || 0);

            const dateB = Number(b.dataset.date || 0);

            if (mode === "oldest") {
                return dateA - dateB;
            }

            return dateB - dateA;
        });

        for (const card of cards) {
            commentList.appendChild(card);
        }
    }

    function render() {
        let visibleCount = 0;

        for (const card of getCards()) {
            const visible = matchesFilter(card) && matchesSearch(card);

            card.classList.toggle("is-hidden", !visible);

            if (visible) {
                visibleCount++;
            }
        }

        if (noResults) {
            noResults.classList.toggle("hidden", visibleCount !== 0);
        }

        sortCards();
    }

    for (const filter of filters) {
        filter.addEventListener("click", () => {
            activeFilter = filter.dataset.filter || "all";

            for (const button of filters) {
                const active = button === filter;

                button.classList.toggle("btn-ghost", !active);

                button.classList.toggle("btn-primary", active);

                button.setAttribute("aria-pressed", String(active));
            }

            render();
        });
    }

    searchInput?.addEventListener("input", render);

    sortSelect?.addEventListener("change", sortCards);

    document.addEventListener("keydown", (event) => {
        if (event.key === "/" && document.activeElement !== searchInput) {
            event.preventDefault();

            searchInput?.focus();
        }

        if (event.key === "Escape" && document.activeElement === searchInput) {
            searchInput.value = "";

            render();

            searchInput.blur();
        }
    });

    function showToast(message, type = "success") {
        document.querySelector(".comment-toast")?.remove();

        const toast = document.createElement("div");

        toast.className = "comment-toast toast toast-end toast-bottom z-[100]";

        const alert = document.createElement("div");

        const alertClass =
            type === "error"
                ? "alert-error"
                : type === "warning"
                  ? "alert-warning"
                  : "alert-success";

        const icon =
            type === "error"
                ? "error"
                : type === "warning"
                  ? "warning"
                  : "check_circle";

        alert.className = `alert ${alertClass} shadow-lg`;

        const iconElement = document.createElement("span");

        iconElement.className = "material-symbols-rounded";

        iconElement.textContent = icon;

        const text = document.createElement("span");

        text.textContent = message;

        alert.append(iconElement, text);

        toast.appendChild(alert);

        document.body.appendChild(toast);

        window.setTimeout(() => {
            toast.classList.add("comment-toast-hide");

            window.setTimeout(() => {
                toast.remove();
            }, 200);
        }, 3000);
    }

    function setLoading(button, loading) {
        if (!button) {
            return;
        }

        if (loading) {
            if (!button.dataset.originalHtml) {
                button.dataset.originalHtml = button.innerHTML;
            }

            button.disabled = true;

            button.classList.add("pointer-events-none");

            button.innerHTML = `
                <span
                    class="
                        loading
                        loading-spinner
                        loading-sm
                    "
                ></span>

                Working...
            `;

            return;
        }

        button.disabled = false;

        button.classList.remove("pointer-events-none");

        if (button.dataset.originalHtml) {
            button.innerHTML = button.dataset.originalHtml;

            delete button.dataset.originalHtml;
        }
    }

    function updateStatus(card, status) {
        card.dataset.status = status;

        const badge = card.querySelector(".comment-status");

        const indicator = card.querySelector(".comment-status-indicator");

        if (!badge) {
            return;
        }

        badge.classList.remove("badge-success", "badge-warning", "badge-error");

        indicator?.classList.remove("bg-success", "bg-warning", "bg-error");

        if (status === "approved") {
            badge.classList.add("badge-success");

            badge.innerHTML = `
                <span
                    class="
                        material-symbols-rounded
                        text-sm
                    "
                >
                    check_circle
                </span>

                Approved
            `;

            indicator?.classList.add("bg-success");

            return;
        }

        if (status === "rejected") {
            badge.classList.add("badge-error");

            badge.innerHTML = `
                <span
                    class="
                        material-symbols-rounded
                        text-sm
                    "
                >
                    cancel
                </span>

                Rejected
            `;

            indicator?.classList.add("bg-error");

            return;
        }

        badge.classList.add("badge-warning");

        badge.innerHTML = `
            <span
                class="
                    material-symbols-rounded
                    text-sm
                "
            >
                schedule
            </span>

            Needs review
        `;

        indicator?.classList.add("bg-warning");
    }

    function getActionForm(card, action) {
        return (
            card.querySelector(`form[data-action="${action}"]`) ||
            card
                .querySelector(`button[data-action="${action}"]`)
                ?.closest("form")
        );
    }

    function updateActions(card, status) {
        const approveForm = getActionForm(card, "approve");

        const rejectForm = getActionForm(card, "reject");

        if (approveForm) {
            approveForm.hidden = status === "approved";
        }

        if (rejectForm) {
            rejectForm.hidden = status === "rejected";
        }
    }

    function removeCard(card) {
        card.classList.add("is-removing");

        window.setTimeout(() => {
            card.remove();

            render();
        }, 250);
    }

    async function submitAjax(form, action) {
        if (!form) {
            return;
        }

        const button = form.querySelector("button[type='submit']");

        if (!button) {
            return;
        }

        if (button.disabled || form.dataset.submitting === "true") {
            return;
        }

        form.dataset.submitting = "true";

        setLoading(button, true);

        try {
            const response = await fetch(form.action, {
                method: "POST",

                headers: {
                    "X-Requested-With": "XMLHttpRequest",

                    Accept: "application/json",
                },

                body: new FormData(form),
            });

            let data;

            try {
                data = await response.json();
            } catch {
                throw new Error("The server returned an invalid response.");
            }

            if (!response.ok || !data.success) {
                throw new Error(
                    data.message || "Unable to complete the action.",
                );
            }

            const card = form.closest(".comment-card");

            if (!card) {
                return;
            }

            if (action === "delete") {
                setLoading(button, false);

                delete form.dataset.submitting;

                removeCard(card);

                showToast(data.message || "Comment deleted successfully.");

                return;
            }

            setLoading(button, false);

            delete form.dataset.submitting;

            updateStatus(card, data.status);

            updateActions(card, data.status);

            render();

            showToast(
                data.status === "approved"
                    ? "Comment approved."
                    : "Comment rejected.",
            );
        } catch (error) {
            console.error("Comment action failed:", error);

            setLoading(button, false);

            delete form.dataset.submitting;

            showToast(error.message || "Something went wrong.", "error");
        }
    }

    document.addEventListener("submit", (event) => {
        const form = event.target.closest(".comment-action-form");

        if (!form) {
            return;
        }

        event.preventDefault();

        const button = form.querySelector("button[type='submit']");

        const action = form.dataset.action || button?.dataset.action;

        if (!action) {
            console.error("Comment action form has no action:", form);

            return;
        }

        if (action === "delete") {
            pendingDeleteForm = form;

            deleteDialog?.showModal();

            return;
        }

        submitAjax(form, action);
    });

    deleteConfirm?.addEventListener("click", () => {
        if (!pendingDeleteForm) {
            return;
        }

        const form = pendingDeleteForm;

        pendingDeleteForm = null;

        deleteDialog?.close();

        submitAjax(form, "delete");
    });

    deleteCancel?.addEventListener("click", () => {
        pendingDeleteForm = null;

        deleteDialog?.close();
    });

    deleteDialog?.addEventListener("click", (event) => {
        if (event.target === deleteDialog) {
            pendingDeleteForm = null;

            deleteDialog.close();
        }
    });

    if (filters[0]) {
        filters[0].classList.remove("btn-ghost");

        filters[0].classList.add("btn-primary");

        filters[0].setAttribute("aria-pressed", "true");
    }

    render();
});
