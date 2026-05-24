async function loadAndApplyTheme() {
    const rootHtml = document.documentElement;
    
    // 1. Find the custom theme variable specified in the page front matter
    // MkDocs translates "page_theme: x" into <meta name="page_theme" content="x">
    const themeMeta = document.querySelector('meta[name="page_theme"]');
    let activeThemeKey = "default";

    if (themeMeta && themeMeta.getAttribute('content')) {
        activeThemeKey = themeMeta.getAttribute('content');
    } else {
        // Fallback directory tracking if you forget to add metadata to a subpage
        const currentPath = window.location.pathname.toLowerCase();
        if (currentPath.includes("celesta-public-archive")) activeThemeKey = "celesta-archive";
        else if (currentPath.includes("stellar-republic-database")) activeThemeKey = "stellar-republic";
    }

    try {
        // 2. Fetch your centralized JSON color lookup database
        // Adjust the path below to match where your file is hosted relative to the base URL
        const response = await fetch('/javascripts/theme-palettes.json');
        const themes = await response.json();
        
        // Pick the selected profile configuration or use default
        const palette = themes[activeThemeKey] || themes["default"];

        // 3. Brute force apply the design variable layout
        rootHtml.style.setProperty("--md-primary-fg-color", palette.primary, "important");
        rootHtml.style.setProperty("--md-primary-fg-color--light", palette.light, "important");
        rootHtml.style.setProperty("--md-primary-fg-color--dark", palette.dark, "important");
        rootHtml.style.setProperty("--custom-nav-text-color", palette.text, "important");
        rootHtml.style.setProperty("--md-bg-color", palette.bg, "important");
        rootHtml.style.setProperty("--md-bg-color--light", palette.bg_light, "important");

    } catch (error) {
        console.error("Multiverse Theme Engine failed to load palette configuration:", error);
    }
}

// Run immediately on page mount execution
loadAndApplyTheme();

// Hook into MkDocs Material's pushState instant loading cycle engine
if (typeof document$ !== "undefined") {
    document$.subscribe(function() {
        loadAndApplyTheme();
    });
}