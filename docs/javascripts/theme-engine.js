/* Dynamic Multiverse Theme Overrider for MkDocs Material */
function applyMultiverseTheme() {
    const currentPath = window.location.pathname;
    const rootHtml = document.documentElement;

    // Check if user is inside the Rise of the Changed (ROTC) folder
    if (currentPath.includes("celesta-public-archive")) {
        rootHtml.style.setProperty("--md-primary-fg-color", "#00D4FF", "important");       /* Signature Cyan */
        rootHtml.style.setProperty("--md-primary-fg-color--light", "#7ce9ffc9", "important");
        rootHtml.style.setProperty("--md-primary-fg-color--dark", "#00333d", "important");
        rootHtml.style.setProperty("--custom-nav-text-color", "#1e293b", "important");     /* Dark text to contrast with the bright color */
    } 
    // Check if user is inside the Terran Stellar Republic (TSR) folder
    else if (currentPath.includes("stellar-republic-database")) {
        rootHtml.style.setProperty("--md-primary-fg-color", "#3b6596", "important");       /* Republic Blue */
        rootHtml.style.setProperty("--md-primary-fg-color--light", "#6d85a0c9", "important");
        rootHtml.style.setProperty("--md-primary-fg-color--dark", "#1e344d", "important");
        rootHtml.style.setProperty("--custom-nav-text-color", "#9abbc4", "important");     /* Muted "professional" font color */
    } 
    // Fallback to Main Home Page (Jessica Red)
    else {
        rootHtml.style.setProperty("--md-primary-fg-color", "#FF0048", "important");       /* Jessica Red */
        rootHtml.style.setProperty("--md-primary-fg-color--light", "#c27a8fc9", "important");
        rootHtml.style.setProperty("--md-primary-fg-color--dark", "#410012", "important");
        rootHtml.style.setProperty("--custom-nav-text-color", "#ffffff", "important");     /* White Text for a contrast with neon-ish red */
    }
}

// Execute immediately to minimize layout flash before render
applyMultiverseTheme();

// Hook into MkDocs Material's instant loading lifecycle engine
if (typeof document$ !== "undefined") {
    document$.subscribe(function() {
        applyMultiverseTheme();
    });
}