document.addEventListener("DOMContentLoaded", function () {
    const tabs = document.querySelectorAll(".profile-tab");
    const sections = document.querySelectorAll(".profile-posts__section");

    if (!tabs.length) return;

    function activate(tab) {
        tabs.forEach((t) => t.classList.remove("profile-tab--active"));
        sections.forEach((s) => s.setAttribute("hidden", ""));
        tab.classList.add("profile-tab--active");
        document.getElementById(tab.dataset.tab).removeAttribute("hidden");
    }

    tabs.forEach((tab) => tab.addEventListener("click", () => activate(tab)));

    activate(tabs[0]);
});
