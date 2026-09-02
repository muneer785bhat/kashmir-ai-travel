// ===============================
// MOBILE MENU
// ===============================

const menuBtn = document.getElementById("menuBtn");

const navLinks = document.querySelector(".nav-links");

if (menuBtn) {

    menuBtn.addEventListener("click", () => {

        navLinks.classList.toggle("mobile-open");

    });

}


// ===============================
// NAVBAR SCROLL EFFECT
// ===============================

window.addEventListener("scroll", () => {

    const navbar = document.querySelector(".navbar");

    if (window.scrollY > 50) {

        navbar.style.background = "rgba(10, 30, 21, 0.75)";
        navbar.style.backdropFilter = "blur(15px)";

    } else {

        navbar.style.background = "transparent";
        navbar.style.backdropFilter = "none";

    }

});


// ===============================
// REVEAL ANIMATION
// ===============================

const revealElements =
    document.querySelectorAll(
        ".feature-card, .destination, .intro-section, .ai-section"
    );

const observer = new IntersectionObserver(
    (entries) => {

        entries.forEach((entry) => {

            if (entry.isIntersecting) {

                entry.target.style.opacity = "1";
                entry.target.style.transform = "translateY(0)";

            }

        });

    },
    {
        threshold: 0.12
    }
);


revealElements.forEach((element) => {

    element.style.opacity = "0";
    element.style.transform = "translateY(30px)";
    element.style.transition = "opacity .7s ease, transform .7s ease";

    observer.observe(element);

});