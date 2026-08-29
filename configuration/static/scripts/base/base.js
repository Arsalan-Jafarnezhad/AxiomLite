const changeTheme = (theme) => {
    localStorage.setItem("theme", theme);
    document.documentElement.setAttribute("data-theme", theme);
    const elements = document.getElementsByClassName("theme-active");
    for (const element of elements) {
        element.remove();
    }
    document.querySelector(
        `.grid[data-theme="${theme}"]`,
    ).parentElement.innerHTML +=
        "<i class='w-4 h-4 fa fa-check theme-active'></i>";
};
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(";").shift();
    }
    return null;
}



const copy = async (element) => {
    try {
        await navigator.clipboard.writeText(element.innerText);
        alert("Copied to clipboard!");
    } catch (err) {
        console.error("Failed to copy: ", err);
    }
};

const removeAlert = (event) => {
    const element = event.target;
    console.log(element);
    console.log(element.parentElement);
    if (element.parentElement.classList.contains("alert")) {
        element.parentElement.remove();
    } else if (element.parentElement.tagName == "DIV") {
        element.parentElement.parentElement.remove();
    } else {
        element.parentElement.parentElement.parentElement.remove();
    }
};

const alerts = document.querySelectorAll(".alert-remover");
for (const alert of alerts) {
    console.log(alert);
    alert.addEventListener("click", removeAlert);
}

