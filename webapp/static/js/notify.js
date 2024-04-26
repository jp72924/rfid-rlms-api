const notifications = document.querySelectorAll('.notification-card');

notifications.forEach(div => {
    div.addEventListener('click', () => {
        div.remove();
    });

    setTimeout(() => {
        div.classList.add("fade-out");
        setTimeout(() => {div.remove();}, 1000);
    }, 5000);
});