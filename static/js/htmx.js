/*
|--------------------------------------------------------------------------
| ClassiX HTMX Manager
|--------------------------------------------------------------------------
*/


/*
|--------------------------------------------------------------------------
| HTMX Trigger Events
|--------------------------------------------------------------------------
*/

document.body.addEventListener("htmx:afterRequest", (event) => {

    const trigger = event.detail.xhr.getResponseHeader("HX-Trigger");

    if (!trigger) {
        return;
    }

    let events;

    try {
        events = JSON.parse(trigger);
    } catch {
        return;
    }

    /*
    |--------------------------------------------------------------------------
    | Close Modal
    |--------------------------------------------------------------------------
    */

    if (events["modal:close"]) {

        const container = document.getElementById("modal-container");

        if (container) {
            container.innerHTML = "";
        }

    }

    /*
    |--------------------------------------------------------------------------
    | Toast (future)
    |--------------------------------------------------------------------------
    */

    if (events["toast:show"]) {

        console.log(events["toast:show"]);

    }

});


/*
|--------------------------------------------------------------------------
| Modal Interaction
|--------------------------------------------------------------------------
*/

document.body.addEventListener("click", (event) => {

    /*
    |--------------------------------------------------------------------------
    | Close button
    |--------------------------------------------------------------------------
    */

    if (event.target.closest("[data-modal-close]")) {

        const container = document.getElementById("modal-container");

        if (container) {
            container.innerHTML = "";
        }

        return;
    }

    /*
    |--------------------------------------------------------------------------
    | Click outside modal
    |--------------------------------------------------------------------------
    */

    if (event.target.classList.contains("modal___overlay")) {

        const container = document.getElementById("modal-container");

        if (container) {
            container.innerHTML = "";
        }

    }

});


/*
|--------------------------------------------------------------------------
| ESC closes modal
|--------------------------------------------------------------------------
*/

document.addEventListener("keydown", (event) => {

    if (event.key !== "Escape") {
        return;
    }

    const container = document.getElementById("modal-container");

    if (container) {
        container.innerHTML = "";
    }

});


/*
|--------------------------------------------------------------------------
| HTMX Lifecycle
|--------------------------------------------------------------------------
*/

document.body.addEventListener("htmx:afterSwap", (event) => {

    if (event.target.id !== "modal-container") {
        return;
    }

    const overlay = event.target.querySelector(".modal___overlay");

    if (!overlay) {
        return;
    }

    requestAnimationFrame(() => {
        overlay.classList.add("active");
    });

});


/*
|--------------------------------------------------------------------------
| HTMX Errors
|--------------------------------------------------------------------------
*/

document.body.addEventListener("htmx:responseError", (event) => {

    console.error(
        "HTMX Response Error",
        event.detail,
    );

});


document.body.addEventListener("htmx:sendError", (event) => {

    console.error(
        "HTMX Send Error",
        event.detail,
    );

});