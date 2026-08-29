(() => {
    "use strict";

    const scene = document.getElementById("card-scene");
    const inner = document.getElementById("card-inner");
    const form = document.getElementById("payment-form");
    const submitBtn = document.getElementById("submit-btn");
    const overlay = document.getElementById("processing-overlay");
    const globalErr = document.getElementById("global-error");
    const globalErrTx = document.getElementById("global-error-text");

    const dispNumber = document.getElementById("disp-number");
    const dispName = document.getElementById("disp-name");
    const dispExpiry = document.getElementById("disp-expiry");
    const dispNetwork = document.getElementById("disp-network");
    const dispCvv = document.getElementById("disp-cvv");

    const inpNumber = document.getElementById("card_number");
    const inpName = document.getElementById("cardholder_name");
    const inpExpiry = document.getElementById("expiry");
    const inpCvv = document.getElementById("cvv");
    const inpPostcode = document.getElementById("billing_postcode");

    let isFlipped = false;
    let isProcessing = false;

    let manualFlip = false;

    function setFlipped(state) {
        isFlipped = state;
        inner.classList.toggle("is-flipped", state);
    }

    scene.addEventListener("click", () => {
        manualFlip = true;
        setFlipped(!isFlipped);
    });

    scene.addEventListener("keydown", (e) => {
        if (e.key === " " || e.key === "Enter") {
            e.preventDefault();
            manualFlip = true;
            setFlipped(!isFlipped);
        }
    });

    inpCvv.addEventListener("focus", () => {
        manualFlip = false;
        setFlipped(true);
    });

    inpCvv.addEventListener("blur", () => {
        if (!manualFlip) setFlipped(false);
    });

    [inpNumber, inpName, inpExpiry, inpPostcode].forEach((el) => {
        el.addEventListener("focus", () => {
            if (!manualFlip) setFlipped(false);
        });
    });

    inpNumber.addEventListener("input", () => {
        const raw = inpNumber.value.replace(/\D/g, "").substring(0, 16);

        inpNumber.value = raw.replace(/(.{4})/g, "$1 ").trimEnd();

        const padded = raw.padEnd(16, "•");
        dispNumber.textContent = padded.match(/.{1,4}/g).join(" ");

        updateNetwork(raw);
    });

    inpName.addEventListener("input", () => {
        const v = inpName.value.trim().toUpperCase();
        dispName.textContent = v || dispName.dataset.placeholder;
    });

    inpExpiry.addEventListener("input", () => {
        let v = inpExpiry.value.replace(/\D/g, "").substring(0, 4);
        if (v.length >= 3) v = v.slice(0, 2) + "/" + v.slice(2);
        inpExpiry.value = v;
        dispExpiry.textContent = v || "MM/YY";
    });

    inpCvv.addEventListener("input", () => {
        dispCvv.textContent =
            inpCvv.value.replace(/\D/g, "").substring(0, 4) || "•••";
    });

    const websiteTitle = document.documentElement.dataset.websiteTitle;

    const NETWORKS = {
        VISA: {
            label: "VISA",
            grad: "linear-gradient(135deg,#1a237e 0%,#1565c0 100%)",
        },
        MASTERCARD: {
            label: "MASTERCARD",
            grad: "linear-gradient(135deg,#c62828 0%,#1a1a1a 100%)",
        },
        AMEX: {
            label: "AMEX",
            grad: "linear-gradient(135deg,#00695c 0%,#0288d1 100%)",
        },
        DISCOVER: {
            label: "DISCOVER",
            grad: "linear-gradient(135deg,#e65100 0%,#ffd600 100%)",
        },
        DEFAULT: {
            label: `${websiteTitle} Card`,

            grad: "linear-gradient(135deg,#1e40af 0%,#1d4ed8 100%)",
        },
    };

    function detectNetwork(num) {
        if (/^4/.test(num)) return "VISA";
        if (/^5[1-5]/.test(num)) return "MASTERCARD";
        if (/^2(2[2-9]|[3-6]\d|7[01])/.test(num)) return "MASTERCARD";
        if (/^3[47]/.test(num)) return "AMEX";
        if (/^6(?:011|5)/.test(num)) return "DISCOVER";
        return "DEFAULT";
    }

    function updateNetwork(num) {
        const key = detectNetwork(num);
        const net = NETWORKS[key];
        dispNetwork.textContent = net.label;

        document.querySelectorAll(".card-face").forEach((face) => {
            face.style.background = net.grad;
        });
    }

    updateNetwork("");

    function showFieldError(fieldId, message) {
        const errEl = document.getElementById(`err-${fieldId}`);
        const wrap = document.getElementById(`wrap-${fieldId}`);
        if (!errEl) return;
        errEl.textContent = message;
        errEl.classList.add("visible");
        wrap?.querySelector(".pay-input")?.classList.add("input-error");
    }

    function clearFieldError(fieldId) {
        const errEl = document.getElementById(`err-${fieldId}`);
        const wrap = document.getElementById(`wrap-${fieldId}`);
        if (!errEl) return;
        errEl.classList.remove("visible");
        wrap?.querySelector(".pay-input")?.classList.remove("input-error");
    }

    function clearAllErrors() {
        document
            .querySelectorAll(".field-error")
            .forEach((el) => el.classList.remove("visible"));
        document
            .querySelectorAll(".pay-input")
            .forEach((el) => el.classList.remove("input-error"));
        hideGlobalError();
    }

    [
        ["card_number", "card_number"],
        ["cardholder_name", "cardholder_name"],
        ["expiry", "expiry"],
        ["cvv", "cvv"],
    ].forEach(([inputId, fieldId]) => {
        document
            .getElementById(inputId)
            ?.addEventListener("input", () => clearFieldError(fieldId));
    });

    function validate() {
        clearAllErrors();
        let valid = true;

        const num = inpNumber.value.replace(/\s/g, "");
        if (num.length < 13 || num.length > 19) {
            showFieldError(
                "card_number",
                window.PAY_I18N?.invalidCard ||
                    "Please enter a valid card number.",
            );
            valid = false;
        }

        const name = inpName.value.trim();
        if (!name || name.length < 2) {
            showFieldError(
                "cardholder_name",
                window.PAY_I18N?.invalidName ||
                    "Please enter the cardholder name.",
            );
            valid = false;
        }

        const parts = inpExpiry.value.split("/");
        const mm = parseInt(parts[0], 10);
        const yy = parseInt(parts[1] || "", 10);
        const now = new Date();
        const expYear = 2000 + yy;
        if (
            !mm ||
            !yy ||
            mm < 1 ||
            mm > 12 ||
            expYear < now.getFullYear() ||
            (expYear === now.getFullYear() && mm < now.getMonth() + 1)
        ) {
            showFieldError(
                "expiry",
                window.PAY_I18N?.invalidExpiry ||
                    "Please enter a valid expiry date.",
            );
            valid = false;
        }

        const network = detectNetwork(num);
        const cvvLen = network === "AMEX" ? 4 : 3;
        if (inpCvv.value.replace(/\D/g, "").length < cvvLen) {
            showFieldError(
                "cvv",
                (
                    window.PAY_I18N?.invalidCvv ||
                    `CVV must be ${cvvLen} digits.`
                ).replace("{n}", cvvLen),
            );
            valid = false;
        }

        return valid;
    }

    function luhn(num) {
        let sum = 0,
            alt = false;
        for (let i = num.length - 1; i >= 0; i--) {
            let n = parseInt(num[i], 10);
            if (alt) {
                n *= 2;
                if (n > 9) n -= 9;
            }
            sum += n;
            alt = !alt;
        }
        return sum % 10 === 0;
    }

    function showGlobalError(msg) {
        globalErrTx.textContent = msg;
        globalErr.classList.add("visible");

        void globalErr.offsetHeight;
    }
    function hideGlobalError() {
        globalErr.classList.remove("visible");
    }

    function setProcessing(state) {
        isProcessing = state;
        submitBtn.disabled = state;
        submitBtn.classList.toggle("is-loading", state);
        if (state) {
            overlay.classList.add("visible");

            requestAnimationFrame(() => (overlay.style.opacity = "1"));
        } else {
            overlay.style.opacity = "0";
            setTimeout(() => overlay.classList.remove("visible"), 200);
        }
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (isProcessing) return;

        hideGlobalError();
        if (!validate()) return;

        const num = inpNumber.value.replace(/\s/g, "");
        if (!luhn(num)) {
            showFieldError(
                "card_number",
                window.PAY_I18N?.luhnFail ||
                    "Card number is invalid. Please check and try again.",
            );
            return;
        }

        setProcessing(true);

        try {
            const resp = await fetch(form.action, {
                method: "POST",
                headers: { "X-Requested-With": "XMLHttpRequest" },
                body: new FormData(form),
            });

            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

            const json = await resp.json();

            if (json.ok) {
                window.location.href = json.redirect_url;
            } else {
                showGlobalError(
                    json.error ||
                        window.PAY_I18N?.payFailed ||
                        "Payment failed. Please try again or use a different card.",
                );
                setProcessing(false);
            }
        } catch (err) {
            console.error("Payment fetch error:", err);
            showGlobalError(
                window.PAY_I18N?.networkErr ||
                    "A network error occurred. Please check your connection and try again.",
            );
            setProcessing(false);
        }
    });
})();
