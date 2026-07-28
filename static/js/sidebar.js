document.addEventListener("DOMContentLoaded", () => {

    const menus = document.querySelectorAll(".cx-sidebar__menu");

    menus.forEach((menu) => {

        const button = menu.querySelector(".cx-sidebar__item");
        const submenu = menu.querySelector(".cx-sidebar__submenu");

        if (!button || !submenu) {
            return;
        }

        button.addEventListener("click", () => {

            const expanded = menu.classList.contains("is-expanded");

            // Close every other menu
            menus.forEach((otherMenu) => {

                if (otherMenu === menu) {
                    return;
                }

                otherMenu.classList.remove("is-expanded");

                const otherButton = otherMenu.querySelector(".cx-sidebar__item");
                const otherSubmenu = otherMenu.querySelector(".cx-sidebar__submenu");

                if (otherButton) {
                    otherButton.setAttribute("aria-expanded", "false");
                }

                if (otherSubmenu) {
                    otherSubmenu.style.maxHeight = null;
                }

            });

            if (expanded) {

                menu.classList.remove("is-expanded");
                button.setAttribute("aria-expanded", "false");
                submenu.style.maxHeight = null;

            } else {

                menu.classList.add("is-expanded");
                button.setAttribute("aria-expanded", "true");
                submenu.style.maxHeight = submenu.scrollHeight + "px";

            }

        });

    });

});