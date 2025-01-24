function toggleAnswer(element) {
    const answer = element.nextElementSibling;
    if (answer.style.display === "none" || !answer.style.display) {
        answer.style.display = "block";
    } else {
        answer.style.display = "none";
    }
}
window.onscroll = function() {scrollFunction()};

function scrollFunction() {
    var backToTopBtn = document.getElementById("backToTopBtn");
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        backToTopBtn.style.display = "block";
    } else {
        backToTopBtn.style.display = "none";
    }
}
function topFunction() {
    window.scrollTo({
    top: 0,
    behavior: 'smooth'
});   
}

document.querySelectorAll('.question').forEach(item => {
    item.addEventListener('click', event => {
        item.classList.toggle('clicked');
    });
});