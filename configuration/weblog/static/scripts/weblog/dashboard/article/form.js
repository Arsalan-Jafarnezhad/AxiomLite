document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("[data-article-form]");

    if (!form) {
        return;
    }

    const markdownInput = form.querySelector("[data-markdown-input]");
    const markdownEditor = form.querySelector("[data-markdown-editor]");
    const markdownPreview = form.querySelector("[data-markdown-preview]");
    const markdownPreviewDivider = form.querySelector(
        "[data-markdown-preview-divider]",
    );
    const submitButton = form.querySelector('button[type="submit"]');

    if (!submitButton) {
        return;
    }

    function getErrorContainer(element) {
        if (element === markdownInput) {
            return (
                markdownEditor?.closest(".editor-panel") ||
                markdownEditor?.parentElement ||
                element.parentElement
            );
        }

        return (
            element.closest(".article-field-control") ||
            element.closest(".article-field") ||
            element.parentElement
        );
    }

    function getExistingError(container) {
        return container?.querySelector(":scope > .article-validation-error");
    }

    function removeError(element) {
        element.classList.remove("field-invalid");

        const container = getErrorContainer(element);

        const error = getExistingError(container);

        if (error) {
            error.remove();
        }
    }

    function showError(element, message) {
        removeError(element);

        element.classList.add("field-invalid");

        const container = getErrorContainer(element);

        if (!container) {
            return;
        }

        const error = document.createElement("div");

        error.className = "article-validation-error";

        const icon = document.createElement("span");

        icon.className = "material-symbols-rounded";
        icon.textContent = "error";

        const text = document.createElement("span");

        text.textContent = message;

        error.append(icon, text);

        container.appendChild(error);
    }

    function clearValidation() {
        form.querySelectorAll(".field-invalid").forEach((element) => {
            element.classList.remove("field-invalid");
        });

        form.querySelectorAll(".article-validation-error").forEach(
            (element) => {
                element.remove();
            },
        );

        markdownEditor?.classList.remove("editor-invalid");
    }

    function getFieldLabel(field) {
        const label = form.querySelector(
            `label[for="${CSS.escape(field.id)}"]`,
        );

        if (label) {
            const labelText = label
                .querySelector(".article-field-label")
                ?.textContent.trim();

            if (labelText) {
                return labelText.replace(/\*/g, "").trim();
            }

            return label.textContent.replace(/\*/g, "").trim();
        }

        return field.name
            .replaceAll("_", " ")
            .replace(/\b\w/g, (letter) => letter.toUpperCase());
    }

    function validateRequiredFields() {
        let valid = true;

        const fields = form.querySelectorAll("input, select, textarea");

        fields.forEach((field) => {
            if (
                field.disabled ||
                field.type === "hidden" ||
                field.type === "submit" ||
                field.type === "button" ||
                field.type === "file"
            ) {
                return;
            }

            removeError(field);

            if (!field.required) {
                return;
            }

            if (field.type === "checkbox") {
                if (!field.checked) {
                    showError(field, `${getFieldLabel(field)} is required.`);

                    valid = false;
                }

                return;
            }

            const value = field.value.trim();

            if (!value) {
                showError(field, `${getFieldLabel(field)} is required.`);

                valid = false;

                return;
            }

            if (!field.checkValidity()) {
                showError(
                    field,
                    field.validationMessage ||
                        `${getFieldLabel(field)} is invalid.`,
                );

                valid = false;
            }
        });

        return valid;
    }

    function getReadableMarkdownText(markdown) {
        return (
            markdown
                /*
                 * Remove images completely.
                 */
                .replace(/!\[[^\]]*\]\([^)]*\)/g, "")

                /*
                 * Convert links to their visible labels.
                 */
                .replace(/\[([^\]]+)\]\(([^)]+)\)/g, "$1")

                /*
                 * Keep code content but remove fences.
                 */
                .replace(/```[a-zA-Z0-9_+.#-]*\n?/g, "")
                .replace(/```/g, "")

                /*
                 * Remove Markdown heading markers.
                 */
                .replace(/^#{1,6}\s+/gm, "")

                /*
                 * Remove quote markers.
                 */
                .replace(/^>\s?/gm, "")

                /*
                 * Remove unordered list markers.
                 */
                .replace(/^\s*[-*+]\s+/gm, "")

                /*
                 * Remove ordered list markers.
                 */
                .replace(/^\s*\d+\.\s+/gm, "")

                /*
                 * Remove Markdown emphasis / code syntax.
                 */
                .replace(/[*_~`]/g, "")

                /*
                 * Remove horizontal rules.
                 */
                .replace(/^\s*-{3,}\s*$/gm, "")

                .trim()
        );
    }

    function validateMarkdown() {
        if (!markdownInput) {
            return true;
        }

        const content = markdownInput.value.trim();

        markdownEditor?.classList.remove("editor-invalid");

        if (!content) {
            markdownEditor?.classList.add("editor-invalid");

            showError(markdownInput, "Article content cannot be empty.");

            return false;
        }

        const readableText = getReadableMarkdownText(content);

        if (!readableText) {
            markdownEditor?.classList.add("editor-invalid");

            showError(
                markdownInput,
                "Article content must contain some readable text.",
            );

            return false;
        }

        return true;
    }

    function validateForm() {
        clearValidation();

        const fieldsValid = validateRequiredFields();
        const markdownValid = validateMarkdown();

        return fieldsValid && markdownValid;
    }

    function focusFirstInvalid() {
        const firstInvalid = form.querySelector(".field-invalid");

        if (!firstInvalid) {
            return;
        }

        if (
            firstInvalid === markdownInput &&
            markdownInput?.classList.contains("hidden")
        ) {
            markdownInput.classList.remove("hidden");

            markdownPreview?.classList.add("hidden");
            markdownPreviewDivider?.classList.add("hidden");
        }

        firstInvalid.focus();

        firstInvalid.scrollIntoView({
            behavior: "smooth",
            block: "center",
        });
    }

    form.querySelectorAll("input, select, textarea").forEach((field) => {
        field.addEventListener("input", () => {
            removeError(field);

            if (field === markdownInput) {
                markdownEditor?.classList.remove("editor-invalid");
            }
        });

        field.addEventListener("change", () => {
            removeError(field);

            if (field === markdownInput) {
                markdownEditor?.classList.remove("editor-invalid");
            }
        });

        field.addEventListener("blur", () => {
            if (!field.required) {
                return;
            }

            if (field.type === "checkbox") {
                if (!field.checked) {
                    showError(field, `${getFieldLabel(field)} is required.`);
                }

                return;
            }

            if (!field.value.trim()) {
                showError(field, `${getFieldLabel(field)} is required.`);

                return;
            }

            if (!field.checkValidity()) {
                showError(
                    field,
                    field.validationMessage ||
                        `${getFieldLabel(field)} is invalid.`,
                );
            }
        });
    });

    markdownInput?.addEventListener("focus", () => {
        markdownEditor?.classList.remove("editor-invalid");
        removeError(markdownInput);
    });

    form.addEventListener("submit", (event) => {
        if (!validateForm()) {
            event.preventDefault();

            focusFirstInvalid();

            return;
        }

        submitButton.disabled = true;

        submitButton.setAttribute("aria-busy", "true");

        submitButton.dataset.originalContent = submitButton.innerHTML;

        submitButton.innerHTML = `
            <span class="loading loading-spinner loading-sm"></span>
            <span>Saving...</span>
        `;
    });
});
