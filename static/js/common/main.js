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

    const TIMEOUT_MS = 3600 * 1000;
    const isLogin = document.querySelector(".logout-link");

    if (isLogin) {
        setTimeout(() => {
            alert("장시간 이용하지 않아 로그아웃됩니다.");
            location.href = "/auth/logout";
        }, TIMEOUT_MS);
    }

    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('reason') === 'timeout') {
        alert("장시간 이용하지 않아 로그아웃되었습니다.");
        window.history.replaceState({}, document.title, window.location.pathname);
    }
})();

