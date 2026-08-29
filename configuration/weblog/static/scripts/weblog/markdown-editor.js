class MarkdownEditor {
    constructor(element) {
        this.editor = element;

        this.textarea = element.querySelector("[data-markdown-input]");

        this.preview = element.querySelector("[data-markdown-preview]");

        this.imageInput = element.querySelector("[data-markdown-image-input]");

        this.status = element.querySelector("[data-markdown-status]");

        this.csrfInput = element.querySelector("[data-markdown-csrf]");

        this.uploadUrl = element.dataset.uploadUrl;

        this.bindEvents();

        this.updateStatus();
    }

    bindEvents() {
        this.editor.querySelectorAll("[data-action]").forEach((button) => {
            button.addEventListener("click", () => {
                this.handleAction(button.dataset.action);
            });
        });

        if (this.textarea) {
            this.textarea.addEventListener("input", () => {
                this.updateStatus();
            });

            this.textarea.addEventListener("keydown", (event) => {
                if (event.ctrlKey && event.key.toLowerCase() === "b") {
                    event.preventDefault();

                    this.wrapSelection("**", "**");
                }

                if (event.ctrlKey && event.key.toLowerCase() === "i") {
                    event.preventDefault();

                    this.wrapSelection("*", "*");
                }
            });
        }

        if (this.imageInput) {
            this.imageInput.addEventListener("change", () => {
                this.uploadImage();
            });
        }
    }

    handleAction(action) {
        switch (action) {
            case "bold":
                this.wrapSelection("**", "**");
                break;

            case "italic":
                this.wrapSelection("*", "*");
                break;

            case "strikethrough":
                this.wrapSelection("~~", "~~");
                break;

            case "h1":
                this.insertPrefix("# ");
                break;

            case "h2":
                this.insertPrefix("## ");
                break;

            case "h3":
                this.insertPrefix("### ");
                break;

            case "bullet-list":
                this.insertPrefix("- ");
                break;

            case "numbered-list":
                this.insertPrefix("1. ");
                break;

            case "quote":
                this.insertPrefix("> ");
                break;

            case "link":
                this.insertLink();
                break;

            case "image":
                this.openImagePicker();
                break;

            case "code":
                this.wrapSelection("`", "`");
                break;

            case "code-block":
                this.insertCodeBlock();
                break;

            case "horizontal-rule":
                this.insertText("\n\n---\n\n");
                break;

            case "table":
                this.insertTable();
                break;

            case "preview":
                this.togglePreview();
                break;
        }
    }

    openImagePicker() {
        if (!this.imageInput) {
            this.setStatus("Image upload is unavailable.", true);

            return;
        }

        this.imageInput.click();
    }

    async uploadImage() {
        const file = this.imageInput?.files?.[0];

        if (!file) {
            return;
        }

        if (!this.uploadUrl) {
            this.setStatus("Image upload URL is missing.", true);

            return;
        }

        const csrfToken = this.getCsrfToken();

        if (!csrfToken) {
            this.setStatus("CSRF token is missing.", true);

            console.error("MarkdownEditor: CSRF token was not found.");

            return;
        }

        const formData = new FormData();

        formData.append("image", file);

        this.setStatus("Uploading image...");

        try {
            const response = await fetch(this.uploadUrl, {
                method: "POST",

                body: formData,

                credentials: "same-origin",

                headers: {
                    "X-CSRFToken": csrfToken,
                },
            });

            let data = {};

            try {
                data = await response.json();
            } catch {
                data = {};
            }

            if (!response.ok) {
                throw new Error(
                    data.error ||
                        data.detail ||
                        `Image upload failed (${response.status}).`,
                );
            }

            if (!data.url) {
                throw new Error("Server did not return an image URL.");
            }

            const alt = file.name
                .replace(/\.[^/.]+$/, "")
                .replace(/[-_]+/g, " ");

            this.insertText(`![${alt}](${data.url})`);

            this.setStatus("Image uploaded.");
        } catch (error) {
            console.error("Markdown image upload failed:", error);

            this.setStatus(error.message || "Image upload failed.", true);
        } finally {
            this.imageInput.value = "";
        }
    }

    getCsrfToken() {
        const input = document.querySelector(
            'input[name="csrfmiddlewaretoken"]',
        );

        if (input?.value) {
            return input.value;
        }

        return this.getCookie("csrftoken");
    }

    wrapSelection(before, after) {
        if (!this.textarea) {
            return;
        }

        const start = this.textarea.selectionStart;

        const end = this.textarea.selectionEnd;

        const value = this.textarea.value;

        const selected = value.slice(start, end);

        const text = selected || "text";

        const replacement = before + text + after;

        this.textarea.setRangeText(replacement, start, end, "select");

        this.focus();

        this.updateStatus();
    }

    insertText(text) {
        if (!this.textarea) {
            return;
        }

        const start = this.textarea.selectionStart;

        const end = this.textarea.selectionEnd;

        this.textarea.setRangeText(text, start, end, "end");

        this.focus();

        this.updateStatus();
    }

    insertPrefix(prefix) {
        if (!this.textarea) {
            return;
        }

        const start = this.textarea.selectionStart;

        const end = this.textarea.selectionEnd;

        const value = this.textarea.value;

        const selected = value.slice(start, end);

        if (!selected) {
            const lineStart = value.lastIndexOf("\n", start - 1) + 1;

            this.textarea.setRangeText(prefix, lineStart, lineStart, "end");

            this.focus();

            this.updateStatus();

            return;
        }

        const replacement = selected
            .split("\n")
            .map((line) => {
                if (!line.trim()) {
                    return prefix.trimEnd();
                }

                return prefix + line;
            })
            .join("\n");

        this.textarea.setRangeText(replacement, start, end, "select");

        this.focus();

        this.updateStatus();
    }

    insertLink() {
        if (!this.textarea) {
            return;
        }

        const start = this.textarea.selectionStart;

        const end = this.textarea.selectionEnd;

        const selected = this.textarea.value.slice(start, end);

        const url = window.prompt("Enter URL:", "https://");

        if (!url) {
            return;
        }

        const label = selected || "link";

        this.textarea.setRangeText(`[${label}](${url})`, start, end, "end");

        this.focus();

        this.updateStatus();
    }

    insertCodeBlock() {
        if (!this.textarea) {
            return;
        }

        const start = this.textarea.selectionStart;

        const end = this.textarea.selectionEnd;

        const selected = this.textarea.value.slice(start, end);

        const language = window.prompt("Programming language:", "python");

        if (language === null) {
            return;
        }

        const lang = language.trim();

        const content = selected || 'print("Hello, world!")';

        const replacement = "```" + lang + "\n" + content + "\n```";

        this.textarea.setRangeText(replacement, start, end, "select");

        this.focus();

        this.updateStatus();
    }

    insertTable() {
        const table = [
            "",
            "| Column 1 | Column 2 | Column 3 |",
            "| --- | --- | --- |",
            "| Value | Value | Value |",
            "| Value | Value | Value |",
            "",
        ].join("\n");

        this.insertText(table);
    }

    togglePreview() {
        if (!this.preview || !this.textarea) {
            return;
        }

        const hidden = this.preview.classList.contains("hidden");

        if (hidden) {
            this.preview.innerHTML = this.simplePreview(this.textarea.value);

            this.preview.classList.remove("hidden");

            this.textarea.classList.add("hidden");
        } else {
            this.preview.classList.add("hidden");

            this.textarea.classList.remove("hidden");
        }
    }

    simplePreview(markdown) {
        let html = this.escapeHtml(markdown);

        html = html.replace(
            /```([a-zA-Z0-9_+.#-]*)\n([\s\S]*?)```/g,
            (_, language, code) => {
                const cleanLanguage = language.trim();

                const languageTitle = cleanLanguage
                    ? this.escapeHtml(cleanLanguage)
                    : "Code";

                const languageClass = cleanLanguage
                    ? ` language-${cleanLanguage}`
                    : "";

                return (
                    `<div class="markdown-code-block">` +
                    `<div class="markdown-code-language">` +
                    `<span class="material-symbols-rounded">` +
                    `code` +
                    `</span>` +
                    `<span>${languageTitle}</span>` +
                    `</div>` +
                    `<pre><code${languageClass}>` +
                    code.trimEnd() +
                    `</code></pre>` +
                    `</div>`
                );
            },
        );

        html = html.replace(/^### (.*)$/gm, "<h3>$1</h3>");

        html = html.replace(/^## (.*)$/gm, "<h2>$1</h2>");

        html = html.replace(/^# (.*)$/gm, "<h1>$1</h1>");

        html = html.replace(/^---$/gm, "<hr>");

        html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

        html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

        html = html.replace(/~~(.+?)~~/g, "<del>$1</del>");

        html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

        html = html.replace(
            /\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g,
            '<a href="$2">$1</a>',
        );

        html = html.replace(
            /!\[([^\]]*)\]\(([^)]+)\)/g,
            '<img src="$2" alt="$1">',
        );

        html = html.replace(/^> (.*)$/gm, "<blockquote>$1</blockquote>");

        html = html.replace(/\n/g, "<br>");

        html = html.replace(
            /(<div class="markdown-code-block">[\s\S]*?<\/div>)<br>/g,
            "$1",
        );

        return html;
    }

    escapeHtml(value) {
        const element = document.createElement("div");

        element.textContent = value;

        return element.innerHTML;
    }

    updateStatus() {
        if (!this.status || !this.textarea) {
            return;
        }

        const text = this.textarea.value;

        const characters = text.length;

        const words = text.trim().split(/\s+/).filter(Boolean).length;

        this.status.textContent = `${words} words · ${characters} characters`;
    }

    setStatus(message, error = false) {
        if (!this.status) {
            return;
        }

        this.status.textContent = message;

        this.status.dataset.error = error ? "true" : "false";
    }

    focus() {
        if (this.textarea) {
            this.textarea.focus();
        }
    }

    getCookie(name) {
        const cookies = document.cookie.split(";");

        for (const cookie of cookies) {
            const trimmed = cookie.trim();

            if (trimmed.startsWith(`${name}=`)) {
                return decodeURIComponent(trimmed.slice(name.length + 1));
            }
        }

        return null;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-markdown-editor]").forEach((element) => {
        new MarkdownEditor(element);
    });
});
