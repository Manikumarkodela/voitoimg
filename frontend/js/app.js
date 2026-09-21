document.addEventListener("DOMContentLoaded", () => {
    // Current Configuration State
    let selectedMode = "ai_gen"; // 'ai_gen' | 'internet' | 'dual'
    let selectedAspect = "1:1";
    let selectedStyle = "real_photo";
    let uploadedFile = null;

    let currentPrompt = "";
    let sessionGallery = [];
    let savedGeminiKey = localStorage.getItem("GEMINI_API_KEY") || "";

    // DOM Elements
    const plusBtn = document.getElementById("plus-btn");
    const plusPopoverMenu = document.getElementById("plus-popover-menu");
    const plusUploadItem = document.getElementById("plus-upload-item");
    const imageUploadInput = document.getElementById("image-upload-input");

    const promptInput = document.getElementById("prompt-input");
    const clearBtn = document.getElementById("clear-btn");
    
    const activeModeBadge = document.getElementById("active-mode-badge");
    const activeModeText = document.getElementById("active-mode-text");
    
    const voiceBtn = document.getElementById("voice-btn");
    const generateBtn = document.getElementById("generate-btn");

    const visualizerContainer = document.getElementById("visualizer-container");
    const voiceStatusText = document.getElementById("voice-status-text");

    const chipModeVal = document.getElementById("chip-mode-val");
    const chipAspectVal = document.getElementById("chip-aspect-val");
    const chipStyleVal = document.getElementById("chip-style-val");
    const chipUploadVal = document.getElementById("chip-upload-val");

    const systemStatusText = document.getElementById("system-status-text");

    const resultsSection = document.getElementById("results-section");
    const resultsTitle = document.getElementById("results-title");
    const searchQueryText = document.getElementById("search-query-text");
    const resultCountBadge = document.getElementById("result-count-badge");
    const loadingBox = document.getElementById("loading-box");
    const loadingTitle = document.getElementById("loading-title");
    const loadingDesc = document.getElementById("loading-desc");
    const resultsGrid = document.getElementById("results-grid");

    const gallerySection = document.getElementById("gallery-section");
    const galleryRow = document.getElementById("gallery-row");

    const lightboxModal = document.getElementById("lightbox-modal");
    const lightboxImage = document.getElementById("lightbox-image");
    const lightboxTitle = document.getElementById("lightbox-title");
    const lightboxRatioTag = document.getElementById("lightbox-ratio-tag");
    const lightboxSourceLink = document.getElementById("lightbox-source-link");
    const lightboxDownloadBtn = document.getElementById("lightbox-download-btn");
    const closeLightboxBtn = document.getElementById("close-lightbox-btn");

    // Audio Visualizer Instance
    const visualizer = new AudioVisualizer("visualizer-canvas");

    // Check Backend Health
    checkBackendHealth();

    async function checkBackendHealth() {
        try {
            const res = await fetch("/api/health");
            if (res.ok) {
                const data = await res.json();
                if (systemStatusText) {
                    systemStatusText.textContent = data.has_gemini_key ? "Gemini & Imagen 3 Ready" : "API Online";
                }
            }
        } catch (e) {
            console.warn("Backend health check warning:", e);
            if (systemStatusText) systemStatusText.textContent = "Offline";
        }
    }

    const modeDropdownMenu = document.getElementById("mode-dropdown-menu");

    // Helper to close popover & dropdown menus
    function closeAllMenus() {
        if (plusPopoverMenu) plusPopoverMenu.classList.add("hidden");
        if (modeDropdownMenu) modeDropdownMenu.classList.add("hidden");
    }
    function closePlusMenu() {
        closeAllMenus();
    }

    // Toggle Plus Popover Menu
    if (plusBtn && plusPopoverMenu) {
        plusBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            if (modeDropdownMenu) modeDropdownMenu.classList.add("hidden");
            plusPopoverMenu.classList.toggle("hidden");
        });
    }

    // Dedicated Mode Badge Dropdown Menu Handler
    if (activeModeBadge && modeDropdownMenu) {
        activeModeBadge.addEventListener("click", (e) => {
            e.stopPropagation();
            if (plusPopoverMenu) plusPopoverMenu.classList.add("hidden");
            modeDropdownMenu.classList.toggle("hidden");
        });
    }

    // Close menus when clicking anywhere outside
    document.addEventListener("click", (e) => {
        if (plusPopoverMenu && !plusPopoverMenu.contains(e.target) && e.target !== plusBtn) {
            plusPopoverMenu.classList.add("hidden");
        }
        if (modeDropdownMenu && !modeDropdownMenu.contains(e.target) && !activeModeBadge.contains(e.target)) {
            modeDropdownMenu.classList.add("hidden");
        }
    });

    // Select Mode from Dedicated Dropdown Menu
    document.querySelectorAll(".mode-dropdown-item[data-mode]").forEach(item => {
        item.addEventListener("click", (e) => {
            e.stopPropagation();
            const mode = item.getAttribute("data-mode");
            selectedMode = mode;

            // Sync active state in dropdown
            document.querySelectorAll(".mode-dropdown-item").forEach(el => el.classList.remove("active"));
            item.classList.add("active");

            // Sync active state in plus menu mode grid
            const modeGrid = document.getElementById("mode-options-grid");
            if (modeGrid) {
                modeGrid.querySelectorAll(".opt-btn").forEach(btn => {
                    if (btn.getAttribute("data-value") === mode) {
                        btn.classList.add("active");
                    } else {
                        btn.classList.remove("active");
                    }
                });
            }

            updateConfigUI();
            closeAllMenus();
        });
    });

    // Upload Reference Image Handler
    if (plusUploadItem && imageUploadInput) {
        plusUploadItem.addEventListener("click", () => {
            imageUploadInput.click();
            closePlusMenu();
        });

        imageUploadInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                uploadedFile = e.target.files[0];
                selectedStyle = "real_photo";
                updateConfigUI();
                if (chipUploadVal) {
                    chipUploadVal.textContent = `📎 ${uploadedFile.name}`;
                    chipUploadVal.classList.remove("hidden");
                }
            }
        });
    }

    // Menu Option Grid Button Handler
    document.querySelectorAll(".opt-btn[data-type]").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const type = btn.getAttribute("data-type");
            const val = btn.getAttribute("data-value");

            // Update active state in group
            const parent = btn.closest(".menu-options-grid");
            if (parent) {
                parent.querySelectorAll(".opt-btn").forEach(b => b.classList.remove("active"));
            }
            btn.classList.add("active");

            if (type === "mode") selectedMode = val;
            if (type === "aspect") selectedAspect = val;
            if (type === "style") selectedStyle = val;

            updateConfigUI();
            closePlusMenu(); // Immediately close popover menu on selection!
        });
    });

    // Sync UI Badges with State
    function updateConfigUI() {
        const modeLabels = {
            "ai_gen": "Imagen 3",
            "internet": "Web Search",
            "dual": "Dual Engine"
        };
        const modeIcons = {
            "ai_gen": "fa-wand-magic-sparkles",
            "internet": "fa-globe",
            "dual": "fa-bolt"
        };
        const styleLabels = {
            "real_photo": "Real Photo",
            "cinematic": "Cinematic",
            "studio_portrait": "Studio Portrait",
            "landscape": "Landscape",
            "cyberpunk": "Cyberpunk",
            "anime": "Anime / Art"
        };

        if (activeModeText) activeModeText.textContent = modeLabels[selectedMode] || "Imagen 3";
        
        if (chipModeVal) {
            chipModeVal.innerHTML = `<i class="fa-solid ${modeIcons[selectedMode]}"></i> ${modeLabels[selectedMode]}`;
        }
        if (chipAspectVal) {
            chipAspectVal.innerHTML = `<i class="fa-solid fa-crop-simple"></i> ${selectedAspect} Aspect`;
        }
        if (chipStyleVal) {
            chipStyleVal.innerHTML = `<i class="fa-solid fa-palette"></i> ${styleLabels[selectedStyle] || selectedStyle}`;
        }
    }

    // Voice Agent Setup
    const voiceAgent = new VoiceAgent(
        (transcript, isFinal) => {
            promptInput.value = transcript;
            toggleClearButton();
            if (isFinal && transcript.trim()) {
                handleAction(transcript.trim());
            }
        },
        (state, message) => {
            if (voiceStatusText && visualizerContainer) {
                voiceStatusText.textContent = message;

                if (state === "listening") {
                    visualizerContainer.classList.remove("hidden");
                    voiceBtn.classList.add("active");
                    visualizer.start();
                } else {
                    voiceBtn.classList.remove("active");
                    visualizer.stop();
                    setTimeout(() => {
                        if (!voiceBtn.classList.contains("active")) {
                            visualizerContainer.classList.add("hidden");
                        }
                    }, 2500);
                }
            }
        }
    );

    if (voiceBtn) {
        voiceBtn.addEventListener("click", () => voiceAgent.toggle());
    }

    // Input Bar Triggers
    if (promptInput) {
        promptInput.addEventListener("input", toggleClearButton);
        promptInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                const prompt = promptInput.value.trim();
                if (prompt) handleAction(prompt);
            }
        });
    }

    function toggleClearButton() {
        if (clearBtn) {
            if (promptInput.value.trim().length > 0) {
                clearBtn.classList.remove("hidden");
            } else {
                clearBtn.classList.add("hidden");
            }
        }
    }

    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            promptInput.value = "";
            toggleClearButton();
            promptInput.focus();
        });
    }

    // Quick Suggestion Chips Click
    document.querySelectorAll(".prompt-chip[data-prompt]").forEach(chip => {
        chip.addEventListener("click", () => {
            const prompt = chip.getAttribute("data-prompt");
            promptInput.value = prompt;
            toggleClearButton();
            handleAction(prompt);
        });
    });

    // Generate Button Click
    if (generateBtn) {
        generateBtn.addEventListener("click", () => {
            const prompt = promptInput.value.trim();
            if (!prompt) return alert("Please enter or speak a prompt first.");
            handleAction(prompt);
        });
    }

    // Action Dispatcher
    function handleAction(prompt) {
        closePlusMenu();
        if (selectedMode === "internet") {
            triggerInternetSearch(prompt);
        } else if (selectedMode === "ai_gen") {
            triggerAIGeneration(prompt);
        } else if (selectedMode === "dual") {
            triggerDualEngine(prompt);
        }
    }

    // 🌐 Web Image Search API
    async function triggerInternetSearch(prompt) {
        currentPrompt = prompt;

        resultsSection.classList.remove("hidden");
        resultsGrid.innerHTML = "";
        loadingBox.classList.remove("hidden");
        loadingTitle.textContent = "Searching Web Images...";
        loadingDesc.textContent = "Fetching high-resolution web visuals matching prompt";
        searchQueryText.textContent = prompt;
        resultCountBadge.textContent = "Searching...";
        loadingBox.classList.remove("hidden");

        try {
            const payload = { prompt: prompt, limit: 30, enhance: true };
            if (savedGeminiKey) payload.gemini_api_key = savedGeminiKey;

            const res = await fetch("/api/search-internet-images", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            let data;
            const contentType = res.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                data = await res.json();
            } else {
                const text = await res.text();
                throw new Error(`Server returned HTTP ${res.status}: ${text.slice(0, 80)}`);
            }

            loadingBox.classList.add("hidden");

            if (!res.ok) throw new Error(data.detail || "Web search failed.");

            searchQueryText.textContent = data.optimized_query || prompt;

            if (data.images && data.images.length > 0) {
                resultCountBadge.textContent = `${data.images.length} Images`;
                renderImageCards(data.images, selectedAspect);
            } else {
                resultCountBadge.textContent = "0 Images";
                resultsGrid.innerHTML = `<p style="color:var(--text-muted); grid-column:1/-1; text-align:center; padding:30px;">No web images found for this prompt.</p>`;
            }

        } catch (err) {
            console.error("Web Search Error:", err);
            loadingBox.classList.add("hidden");
            resultCountBadge.textContent = "Error";
            resultsGrid.innerHTML = `<p style="color:#ef4444; grid-column:1/-1; text-align:center; padding:30px;">Web search error: ${err.message}</p>`;
        }
    }

    // 🎨 AI Image Generation API
    async function triggerAIGeneration(prompt) {
        currentPrompt = prompt;

        resultsSection.classList.remove("hidden");
        resultsGrid.innerHTML = "";
        loadingBox.classList.remove("hidden");
        loadingTitle.textContent = "Google Gemini Synthesizing Image...";
        loadingDesc.textContent = "Optimizing photorealistic prompt & rendering visual";
        searchQueryText.textContent = prompt;
        resultCountBadge.textContent = "Generating...";
        resultsTitle.textContent = "AI Generated Artwork";

        try {
            const payload = {
                prompt: prompt,
                style_preset: selectedStyle,
                aspect_ratio: selectedAspect,
                enhance: true
            };
            if (savedGeminiKey) payload.gemini_api_key = savedGeminiKey;

            const res = await fetch("/api/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            let data;
            const contentType = res.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                data = await res.json();
            } else {
                const text = await res.text();
                throw new Error(`Server returned HTTP ${res.status}: ${text.slice(0, 80)}`);
            }

            loadingBox.classList.add("hidden");

            if (!res.ok) throw new Error(data.detail || "AI Image generation failed.");

            const aiImage = [{
                title: data.enhanced_prompt || prompt,
                image_url: data.image_url,
                thumbnail_url: data.image_url,
                source_domain: data.provider || "Imagen 3",
                engine: "AI Generated",
                aspect_ratio: data.aspect_ratio || selectedAspect
            }];

            resultCountBadge.textContent = "1 Masterpiece";
            renderImageCards(aiImage, selectedAspect);
            addToGallery(data.image_url, data.enhanced_prompt || prompt, selectedAspect);

        } catch (err) {
            console.error("Generation Error:", err);
            loadingBox.classList.add("hidden");
            resultCountBadge.textContent = "Error";
            resultsGrid.innerHTML = `<p style="color:#ef4444; grid-column:1/-1; text-align:center; padding:30px;">AI Generation failed: ${err.message}</p>`;
        }
    }

    // ⚡ Dual Mode
    async function triggerDualEngine(prompt) {
        triggerInternetSearch(prompt);
    }

    // Clean up domain strings to remove DuckDuckGo Web Index and ugly names
    function sanitizeDomain(domainStr) {
        if (!domainStr) return "Web Image";
        let cleaned = domainStr.toString().trim();

        cleaned = cleaned.replace(/DuckDuckGo\s*Web\s*Index/gi, "")
                         .replace(/DuckDuckGo/gi, "")
                         .replace(/Google\s*Images/gi, "Web Image")
                         .trim();

        if (!cleaned || cleaned.length === 0) return "Web Image";
        cleaned = cleaned.replace(/^https?:\/\//i, '').replace(/^www\./i, '');
        return cleaned;
    }

    // Render Image Cards Grid
    function renderImageCards(images, defaultRatio = "1:1") {
        resultsGrid.innerHTML = "";
        images.forEach(item => {
            const card = document.createElement("div");
            card.className = "image-card";

            const rawDomain = item.source_domain || "Web Image";
            const cleanDomain = sanitizeDomain(rawDomain);
            let engineBadge = item.engine || "Web Image";
            
            if (engineBadge.toLowerCase().includes("duckduckgo") || engineBadge.toLowerCase().includes("ddg") || engineBadge.toLowerCase().includes("search")) {
                engineBadge = "Web Image";
            }

            const ratio = item.aspect_ratio || defaultRatio;

            const ratioClassMap = {
                "1:1": "ratio-1-1",
                "16:9": "ratio-16-9",
                "9:16": "ratio-9-16",
                "4:3": "ratio-4-3",
                "3:4": "ratio-3-4"
            };
            const ratioClass = ratioClassMap[ratio] || "ratio-1-1";

            card.innerHTML = `
                <div class="card-img-box ${ratioClass}">
                    <img src="${item.thumbnail_url || item.image_url}" alt="${item.title}" loading="lazy" onerror="this.src='${item.image_url}'">
                    <span class="tag-badge">${engineBadge}</span>
                    <span class="ratio-tag">${ratio}</span>
                </div>
                <div class="card-info">
                    <div class="card-prompt">${item.title || "Visual Artwork"}</div>
                    <div class="card-meta">
                        <span class="source-domain"><i class="fa-solid fa-globe"></i> ${cleanDomain}</span>
                    </div>
                </div>
            `;

            card.addEventListener("click", () => {
                openLightbox(item.image_url, item.title, item.source_url || "#", ratio);
                addToGallery(item.image_url, item.title, ratio);
            });

            resultsGrid.appendChild(card);
        });
    }

    // Lightbox Modal Controls
    function openLightbox(imageUrl, title, sourceUrl = "#", ratio = "1:1") {
        lightboxImage.src = imageUrl;
        lightboxTitle.textContent = title || "Expanded View";
        if (lightboxRatioTag) lightboxRatioTag.textContent = `Ratio: ${ratio}`;
        
        if (lightboxSourceLink) {
            lightboxSourceLink.href = sourceUrl;
            lightboxSourceLink.style.display = (sourceUrl && sourceUrl !== "#") ? "inline-flex" : "none";
        }
        
        lightboxModal.classList.remove("hidden");
    }

    if (closeLightboxBtn) {
        closeLightboxBtn.addEventListener("click", () => lightboxModal.classList.add("hidden"));
    }

    if (lightboxModal) {
        lightboxModal.addEventListener("click", (e) => {
            if (e.target === lightboxModal) lightboxModal.classList.add("hidden");
        });
    }

    if (lightboxDownloadBtn) {
        lightboxDownloadBtn.addEventListener("click", () => {
            if (!lightboxImage.src) return;
            const a = document.createElement("a");
            a.href = lightboxImage.src;
            a.download = `voitoimg_${Date.now()}.png`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        });
    }

    // Gallery Session Management
    function addToGallery(url, prompt, ratio = "1:1") {
        if (sessionGallery.some(item => item.url === url)) return;
        
        sessionGallery.unshift({ url, prompt, ratio });
        gallerySection.classList.remove("hidden");

        const thumb = document.createElement("img");
        thumb.src = url;
        thumb.className = "gallery-thumb";
        thumb.alt = prompt;
        thumb.title = `${prompt} (${ratio})`;
        thumb.addEventListener("click", () => {
            openLightbox(url, prompt, "#", ratio);
        });

        galleryRow.prepend(thumb);
    }
});
