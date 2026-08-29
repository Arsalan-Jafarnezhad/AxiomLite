
document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#account-edit-form");
    if (!form) return;

    const avatarInput = document.querySelector("#id_avatar");
    const avatarPreview = document.querySelector("#avatar-preview");
    const bio = document.querySelector("#id_biography");
    const counter = document.querySelector("#bio-counter");
    const warning = document.querySelector(".unsaved-warning");

    let changed = false;

    function updateCounter() {
        if (!bio || !counter) return;
        counter.textContent = `${bio.value.length}/500`;
    }

    updateCounter();

    bio?.addEventListener("input", updateCounter);

    avatarInput?.addEventListener("change", (e) => {
        const file = e.target.files[0];

        if (!file) return;

        const reader = new FileReader();

        reader.onload = (x) => {
            avatarPreview.src = x.target.result;
        };

        reader.readAsDataURL(file);
    });

    form.querySelectorAll("input,textarea,select").forEach((el) => {
        el.addEventListener("change", () => {
            changed = true;
            warning?.classList.add("show");
        });
    });

    form.addEventListener("submit", () => {
        changed = false;
    });

    window.addEventListener("beforeunload", (e) => {
        if (!changed) return;

        e.preventDefault();
        e.returnValue = "";
    });
});
