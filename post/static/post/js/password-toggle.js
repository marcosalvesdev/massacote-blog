document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".password-toggle").forEach((button) => {
        button.addEventListener("click", () => {
            const input = document.getElementById(button.dataset.target);
            if (!input) return;
            const willShow = input.type === "password";
            input.type = willShow ? "text" : "password";
            button.textContent = willShow ? "Hide" : "Show";
        });
    });
});
