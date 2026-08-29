const LANGUAGE_NAMES = {
    html: "HTML",
    xml: "XML",
    markup: "HTML",

    css: "CSS",

    javascript: "JavaScript",
    js: "JavaScript",

    typescript: "TypeScript",
    ts: "TypeScript",

    python: "Python",
    py: "Python",

    java: "Java",

    c: "C",

    cpp: "C++",
    cxx: "C++",

    csharp: "C#",
    cs: "C#",

    go: "Go",
    rust: "Rust",
    ruby: "Ruby",

    php: "PHP",
    swift: "Swift",
    kotlin: "Kotlin",

    sql: "SQL",

    bash: "Bash",
    shell: "Shell",
    sh: "Shell",

    powershell: "PowerShell",
    ps: "PowerShell",

    json: "JSON",

    yaml: "YAML",
    yml: "YAML",

    markdown: "Markdown",
    md: "Markdown",

    plaintext: "Plain Text",
    text: "Plain Text",
    txt: "Plain Text",
};

const PRISM_LANGUAGES = {
    html: "markup",
    xml: "markup",
    markup: "markup",

    css: "css",

    javascript: "javascript",
    js: "javascript",

    typescript: "typescript",
    ts: "typescript",

    python: "python",
    py: "python",

    java: "java",
    c: "c",

    cpp: "cpp",
    cxx: "cpp",

    csharp: "csharp",
    cs: "csharp",

    go: "go",
    rust: "rust",
    ruby: "ruby",

    php: "php",
    swift: "swift",
    kotlin: "kotlin",

    sql: "sql",

    bash: "bash",
    shell: "bash",
    sh: "bash",

    powershell: "powershell",
    ps: "powershell",

    json: "json",

    yaml: "yaml",
    yml: "yaml",

    markdown: "markdown",
    md: "markdown",
};

function getLanguage(code) {
    const className = [...code.classList].find((name) =>
        name.startsWith("language-"),
    );

    return className ? className.slice(9).toLowerCase() : "text";
}

function getLanguageName(language) {
    return (
        LANGUAGE_NAMES[language] ||
        language.charAt(0).toUpperCase() + language.slice(1)
    );
}

function getPrismLanguage(language) {
    return PRISM_LANGUAGES[language] || language;
}

async function copyText(text) {
    if (navigator.clipboard) {
        await navigator.clipboard.writeText(text);
        return;
    }

    const textarea = document.createElement("textarea");

    textarea.value = text;

    textarea.style.position = "fixed";
    textarea.style.opacity = "0";

    document.body.appendChild(textarea);

    textarea.select();
    document.execCommand("copy");

    textarea.remove();
}

function createCopyButton(code, languageName) {
    const button = document.createElement("button");

    button.type = "button";
    button.className = "markdown-code-copy";

    button.setAttribute("aria-label", `Copy ${languageName} code`);

    button.title = "Copy code";

    button.innerHTML = `
        <span
            class="material-symbols-rounded"
            aria-hidden="true"
        >
            content_copy
        </span>
    `;

    button.addEventListener("click", async () => {
        try {
            await copyText(code.textContent || "");

            button.innerHTML = `
                <span
                    class="material-symbols-rounded"
                    aria-hidden="true"
                >
                    check
                </span>
            `;

            button.classList.add("text-success");

            button.setAttribute("aria-label", "Code copied");

            button.title = "Copied";

            window.setTimeout(() => {
                button.innerHTML = `
                    <span
                        class="material-symbols-rounded"
                        aria-hidden="true"
                    >
                        content_copy
                    </span>
                `;

                button.classList.remove("text-success");

                button.setAttribute("aria-label", `Copy ${languageName} code`);

                button.title = "Copy code";
            }, 1500);
        } catch (error) {
            console.error("Unable to copy code:", error);
        }
    });

    return button;
}

function initializeCodeBlocks(root = document) {
    const Prism = window.Prism;

    if (!Prism) {
        console.error("PrismJS is not loaded.");
        return;
    }

    root.querySelectorAll("pre > code").forEach((code) => {
        const pre = code.parentElement;

        if (!pre) {
            return;
        }

        if (pre.parentElement?.classList.contains("markdown-code-block")) {
            return;
        }

        const language = getLanguage(code);
        const languageName = getLanguageName(language);
        const prismLanguage = getPrismLanguage(language);

        const wrapper = document.createElement("div");

        wrapper.className = "markdown-code-block";

        const header = document.createElement("div");

        header.className = "markdown-code-language";

        const label = document.createElement("div");

        label.className = "markdown-code-language-name";

        label.innerHTML = `
            <span
                class="material-symbols-rounded"
                aria-hidden="true"
            >
                code
            </span>

            <span>
                ${languageName}
            </span>
        `;

        header.appendChild(label);
        header.appendChild(createCopyButton(code, languageName));

        pre.parentNode.insertBefore(wrapper, pre);

        wrapper.appendChild(header);
        wrapper.appendChild(pre);

        if (prismLanguage !== "text" && Prism.languages[prismLanguage]) {
            Prism.highlightElement(code);
        }
    });

    root.querySelectorAll("a").forEach((link) => {
        if (link.hostname && link.hostname !== window.location.hostname) {
            link.target = "_blank";
            link.rel = "noopener noreferrer";
        }
    });
}

export { initializeCodeBlocks };
