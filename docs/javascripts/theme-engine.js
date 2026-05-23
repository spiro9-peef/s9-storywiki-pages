/* Dynamic Multiverse Theme Overrider for MkDocs Material */
function applyMultiverseTheme() {
    // Force lower case to guarantee text matching safety across diverse browser environments
    const currentPath = window.location.pathname.toLowerCase();
    const rootHtml = document.documentElement;

    // 1. RISE OF THE CHANGED (ROTC) ENVIRONMENT LAYER
    if (currentPath.includes("celesta-public-archive")) {
        rootHtml.style.setProperty("--md-primary-fg-color", "#00D4FF", "important");       /* Signature Cyan */
        rootHtml.style.setProperty("--md-primary-fg-color--light", "#7ce9ffc9", "important");
        rootHtml.style.setProperty("--md-primary-fg-color--dark", "#00333d", "important");   /* Deep Dark Cyan backdrop for contrast */
        rootHtml.style.setProperty("--custom-nav-text-color", "#17191c", "important");     /* Dark text to contrast with bright Cyan */
        
        /* PAGE BACKGROUND SETTING */
        rootHtml.style.setProperty("--md-bg-color", "#011114", "important");                /* Deep Cyan-tinted Dark BG */
        rootHtml.style.setProperty("--md-bg-color--light", "#7ce9ff0f", "important");
    } 
    // 2. TERRAN STELLAR REPUBLIC (TSR) ENVIRONMENT LAYER
    else if (currentPath.includes("stellar-republic-database")) {
        rootHtml.style.setProperty("--md-primary-fg-color", "#3b6596", "important");       /* Republic Blue */
        rootHtml.style.setProperty("--md-primary-fg-color--light", "#6d85a0c9", "important");
        rootHtml.style.setProperty("--md-primary-fg-color--dark", "#1e344d", "important");   /* Dark Navy backdrop */
        rootHtml.style.setProperty("--custom-nav-text-color", "#9abbc4", "important");     /* Muted professional font color */
        
        /* PAGE BACKGROUND SETTING */
        rootHtml.style.setProperty("--md-bg-color", "#0b0f19", "important");                /* Deep Space Blue-tinted Dark BG */
        rootHtml.style.setProperty("--md-bg-color--light", "#6d85a00f", "important");
    } 
    // 3. GLOBAL FALLBACK BASELINE (Jessica Red Configuration)
    else {
        rootHtml.style.setProperty("--md-primary-fg-color", "#FF0048", "important");       /* Jessica Red */
        rootHtml.style.setProperty("--md-primary-fg-color--light", "#c27a8fc9", "important");
        rootHtml.style.setProperty("--md-primary-fg-color--dark", "#410012", "important");   /* Deep Crimson backdrop */
        rootHtml.style.setProperty("--custom-nav-text-color", "#ffffff", "important");     /* White Text for high contrast */
        
        /* PAGE BACKGROUND SETTING */
        rootHtml.style.setProperty("--md-bg-color", "#140006", "important");                /* Deep Crimson-tinted Dark BG */
        rootHtml.style.setProperty("--md-bg-color--light", "#c27a8f0f", "important");
    }
}

// Execute immediately to catch processing nodes before the browser paints the body layout
applyMultiverseTheme();

// Handle instant SPA routing updates natively handled by MkDocs Material
if (typeof document$ !== "undefined") {
    document$.subscribe(function() {
        applyMultiverseTheme();
    });
}