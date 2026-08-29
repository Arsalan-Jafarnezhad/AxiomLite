document.addEventListener("DOMContentLoaded", () => {
    const editor = document.querySelector("[data-code-editor]");

    if (!editor) {
        return;
    }

    const textarea = editor.querySelector("[data-code-input]");
    const lineNumbers = editor.querySelector("[data-line-numbers]");
    const lineCount = editor.querySelector("[data-line-count]");
    const charCount = editor.querySelector("[data-char-count]");
    if (!textarea || !lineNumbers) {
        return;
    }

    const MIN_HEIGHT = 360;

    function getLineCount() {
        return Math.max(1, textarea.value.split("\n").length);
    }

    function updateLineNumbers() {
        const count = getLineCount();

        lineNumbers.replaceChildren();

        for (let i = 1; i <= count; i++) {
            const line = document.createElement("div");

            line.className = "question-line-number";
            line.textContent = i;

            lineNumbers.appendChild(line);
        }

        if (lineCount) {
            lineCount.textContent = `${count} ${count === 1 ? "line" : "lines"}`;
        }
        if (charCount) {
            charCount.textContent = `${textarea.value.length} characters`;
        }
    }

    function syncEditorHeight() {
        textarea.style.height = "0px";

        const contentHeight = textarea.scrollHeight;

        const height = Math.max(MIN_HEIGHT, contentHeight);

        textarea.style.height = `${height}px`;
        lineNumbers.style.height = `${height}px`;
    }

    function syncScroll() {
        lineNumbers.scrollTop = textarea.scrollTop;
    }

    function updateEditor() {
        updateLineNumbers();

        requestAnimationFrame(() => {
            syncEditorHeight();
            syncScroll();
        });
    }

    textarea.addEventListener("input", updateEditor);

    textarea.addEventListener("scroll", syncScroll);

    textarea.addEventListener("keydown", (event) => {
        if (event.key !== "Tab") {
            return;
        }

        event.preventDefault();

        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;

        textarea.setRangeText("    ", start, end, "end");

        updateEditor();
    });

    textarea.addEventListener("paste", () => {
        requestAnimationFrame(updateEditor);
    });

    updateEditor();

    window.addEventListener("load", updateEditor);

    window.addEventListener("resize", () => {
        requestAnimationFrame(() => {
            syncEditorHeight();
            syncScroll();
        });
    });
});
