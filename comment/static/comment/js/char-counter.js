document.addEventListener("DOMContentLoaded", function () {
    const textarea = document.querySelector(".comment-form__body");
    if (!textarea) return;

    const max = textarea.maxLength;
    const counter = document.querySelector(".comment-form__char-count");
    if (!counter) return;

    function update() {
        const remaining = max - textarea.value.length;
        counter.textContent = `${textarea.value.length} / ${max}`;
        counter.classList.toggle("comment-form__char-count--warn", remaining <= 50);
    }

    textarea.addEventListener("input", update);
    update();
});
