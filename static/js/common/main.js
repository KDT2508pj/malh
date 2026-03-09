(() => {
    const menuToggle = document.getElementById("menuToggle");
    const mobileMenu = document.getElementById("mobileMenu");
    if (!menuToggle || !mobileMenu) return;

    const closeMenu = () => {
        document.body.classList.remove("mobile-menu-open");
        menuToggle.setAttribute("aria-expanded", "false");
    };

    const openMenu = () => {
        document.body.classList.add("mobile-menu-open");
        menuToggle.setAttribute("aria-expanded", "true");
    };

    menuToggle.addEventListener("click", () => {
        const isOpen = document.body.classList.contains("mobile-menu-open");
        if (isOpen) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    document.addEventListener("click", (event) => {
        if (!document.body.classList.contains("mobile-menu-open")) return;
        const target = event.target;
        if (!(target instanceof Node)) return;
        if (mobileMenu.contains(target) || menuToggle.contains(target)) return;
        closeMenu();
    });

    mobileMenu.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", closeMenu);
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth > 992) closeMenu();
    });
})();

