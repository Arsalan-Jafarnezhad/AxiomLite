document.addEventListener("DOMContentLoaded", () => {
    const commentBody = document.getElementById("comment-body");

    const commentCounter = document.getElementById("comment-counter");

    const commentForm = document.getElementById("comment-form");

    function updateCounter() {
        if (!commentBody || !commentCounter) {
            return;
        }

        const length = commentBody.value.length;

        commentCounter.textContent = `${length} / 2000`;

        commentCounter.classList.remove("text-warning", "text-error");

        if (length >= 1800) {
            commentCounter.classList.add("text-warning");
        }

        if (length >= 1950) {
            commentCounter.classList.remove("text-warning");

            commentCounter.classList.add("text-error");
        }
    }

    commentBody?.addEventListener("input", updateCounter);

    updateCounter();

    document.querySelectorAll(".reply-button").forEach((button) => {
        button.addEventListener("click", () => {
            if (!commentBody) {
                return;
            }

            const username = button.dataset.username;

            const commentId = button.dataset.commentId;

            commentBody.value = `@${username} `;

            commentBody.focus();

            commentBody.dataset.parent = commentId;

            let parentInput = commentForm?.querySelector(
                'input[name="parent"]',
            );

            if (!parentInput && commentForm) {
                parentInput = document.createElement("input");

                parentInput.type = "hidden";
                parentInput.name = "parent";

                commentForm.appendChild(parentInput);
            }

            if (parentInput) {
                parentInput.value = commentId;
            }

            updateCounter();

            commentForm?.scrollIntoView({
                behavior: "smooth",
                block: "center",
            });
        });
    });

    commentForm?.addEventListener("submit", () => {
        const button = commentForm.querySelector('button[type="submit"]');

        if (!button) {
            return;
        }

        button.disabled = true;

        button.innerHTML = `
                <span class="loading loading-spinner loading-sm"></span>
                Submitting...
            `;
    });
});
