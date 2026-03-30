document.addEventListener("DOMContentLoaded", () => {
    // Ten plik steruje formularzem katalogu po stronie przeglądarki.
    // Najważniejsze zadania to:
    // 1. przełączanie podkategorii i bloków tagów po wyborze kategorii,
    // 2. odświeżanie podglądu karty jeszcze przed zapisaniem wpisu.
    const form = document.querySelector("[data-catalog-form]");
    if (!form) {
        return;
    }

    const categorySelect = form.querySelector("#id_category");
    const subcategorySelect = form.querySelector("#id_subcategory");
    const subcategoryWrapper = form.querySelector("[data-subcategory-wrapper]");
    const subcategoryLabel = form.querySelector("[data-subcategory-label]");
    const categorySpecificBlocks = form.querySelectorAll("[data-category-specific]");
    const subcategoryConfigElement = document.getElementById("catalog-subcategory-config");
    // Konfiguracja podkategorii przychodzi z Django przez json_script,
    // dzięki czemu JS nie musi mieć na sztywno wpisanych opcji dla każdej kategorii.
    const subcategoryConfigs = subcategoryConfigElement ? JSON.parse(subcategoryConfigElement.textContent) : {};

    const titleInput = form.querySelector("#id_title");
    const pickReasonInput = form.querySelector("#id_pick_reason");
    const bannerInput = form.querySelector("#id_banner");
    const bannerClearInput = form.querySelector('input[name="banner-clear"]');

    const previewCategory = form.querySelector("[data-preview-category]");
    const previewSubcategory = form.querySelector("[data-preview-subcategory]");
    const previewTags = form.querySelector("[data-preview-tags]");
    const previewTitle = form.querySelector("[data-preview-title]");
    const previewReason = form.querySelector("[data-preview-reason]");
    const previewImage = form.querySelector("[data-preview-image]");
    const previewImageEmpty = form.querySelector("[data-preview-image-empty]");

    // Gdy użytkownik kilka razy zmienia plik, zwalniamy stary lokalny URL,
    // żeby przeglądarka nie trzymała niepotrzebnie poprzednich obrazków w pamięci.
    let objectPreviewUrl = null;

    if (!categorySelect) {
        return;
    }

    // Gdy zmieniamy kategorię, ukrywamy zaznaczenia z niepasujących bloków,
    // żeby formularz nie wysyłał starych tagów z poprzedniego wyboru.
    const clearCheckboxes = (container) => {
        if (!container) {
            return;
        }

        container.querySelectorAll('input[type="checkbox"]').forEach((input) => {
            input.checked = false;
        });
    };

    // Po zmianie kategorii od razu podmieniamy listę podkategorii,
    // żeby formularz nie mieszał opcji między filmem, serialem i grą.
    const renderSubcategoryOptions = (config, selectedValue = "") => {
        if (!subcategorySelect) {
            return;
        }

        subcategorySelect.innerHTML = "";

        const placeholderOption = document.createElement("option");
        placeholderOption.value = "";
        placeholderOption.textContent = "Wybierz podkategorię";
        subcategorySelect.appendChild(placeholderOption);

        (config?.options || []).forEach((option) => {
            const optionElement = document.createElement("option");
            optionElement.value = option.value;
            optionElement.textContent = option.label;
            subcategorySelect.appendChild(optionElement);
        });

        subcategorySelect.value = selectedValue;
        if (subcategorySelect.value !== selectedValue) {
            subcategorySelect.value = "";
        }
    };

    // Podgląd ma działać jak szybkie sprawdzenie karty jeszcze przed zapisem.
    const updatePreviewText = () => {
        if (previewTitle) {
            previewTitle.textContent = titleInput?.value.trim() || "Tu pojawi się tytuł wpisu.";
        }

        if (previewReason) {
            previewReason.textContent = pickReasonInput?.value.trim() || "Tu pojawi się krótkie „dlaczego warto”.";
        }
    };

    // Kategoria i podkategoria muszą być widoczne osobno,
    // bo na karcie pełnią dwie różne role: typ i doprecyzowanie klimatu.
    const updatePreviewCategory = () => {
        if (previewCategory) {
            const categoryLabel = categorySelect.options[categorySelect.selectedIndex]?.textContent?.trim() || "Kategoria";
            previewCategory.textContent = categoryLabel;
        }

        if (!previewSubcategory || !subcategorySelect) {
            return;
        }

        const selectedOption = subcategorySelect.options[subcategorySelect.selectedIndex];
        const subcategoryText = selectedOption && selectedOption.value ? selectedOption.textContent.trim() : "";

        previewSubcategory.textContent = subcategoryText;
        previewSubcategory.classList.toggle("is-hidden", !subcategoryText);
    };

    // Na karcie pokazujemy tylko kilka tagów, żeby preview wyglądał tak jak realny katalog.
    const updatePreviewTags = () => {
        if (!previewTags) {
            return;
        }

        previewTags.querySelectorAll("[data-preview-dynamic-tag]").forEach((tag) => tag.remove());

        const checkedTags = Array.from(form.querySelectorAll('input[name="tags"]:checked'))
            .map((input) => input.closest("label")?.querySelector("span")?.textContent?.trim())
            .filter(Boolean)
            .slice(0, 3);

        checkedTags.forEach((tagName) => {
            const tagElement = document.createElement("span");
            tagElement.className = "catalog-card-vibe";
            tagElement.dataset.previewDynamicTag = "1";
            tagElement.textContent = tagName;
            previewTags.appendChild(tagElement);
        });
    };

    // Samo przełączanie widoczności obrazka trzymamy osobno,
    // żeby obsłużyć tak samo nowy plik, stary obraz i wyczyszczenie pola.
    const setPreviewImage = (src) => {
        if (!previewImage || !previewImageEmpty) {
            return;
        }

        const hasImage = Boolean(src);
        previewImage.classList.toggle("is-hidden", !hasImage);
        previewImageEmpty.classList.toggle("is-hidden", hasImage);

        if (hasImage) {
            previewImage.src = src;
        } else {
            previewImage.removeAttribute("src");
        }
    };

    // Dla nowo wybranego pliku używamy lokalnego URL,
    // żeby od razu zobaczyć okładkę bez wysyłania jej na serwer.
    const updatePreviewImage = () => {
        if (!previewImage) {
            return;
        }

        if (objectPreviewUrl) {
            URL.revokeObjectURL(objectPreviewUrl);
            objectPreviewUrl = null;
        }

        const selectedFile = bannerInput?.files?.[0];
        if (selectedFile) {
            objectPreviewUrl = URL.createObjectURL(selectedFile);
            setPreviewImage(objectPreviewUrl);
            return;
        }

        if (bannerClearInput?.checked) {
            setPreviewImage("");
            return;
        }

        setPreviewImage(previewImage.dataset.initialSrc || "");
    };

    // To spina całą zmianę kategorii:
    // select podkategorii, bloki tagów i preview muszą przełączyć się razem.
    const updateCatalogCategoryFields = () => {
        const selectedCategory = categorySelect.value;
        const subcategoryConfig = subcategoryConfigs[selectedCategory];

        if (subcategoryWrapper) {
            subcategoryWrapper.classList.toggle("is-hidden", !subcategoryConfig);
        }

        if (subcategoryLabel) {
            subcategoryLabel.textContent = subcategoryConfig?.label || "Podkategoria";
        }

        renderSubcategoryOptions(subcategoryConfig, subcategorySelect?.value || "");

        if (!subcategoryConfig && subcategorySelect) {
            subcategorySelect.value = "";
        }

        categorySpecificBlocks.forEach((block) => {
            const isActive = block.dataset.categorySpecific === selectedCategory;
            block.classList.toggle("is-hidden", !isActive);

            // Ukryty blok czyścimy od razu, żeby stare zaznaczenia
            // nie wróciły do formularza po zmianie kategorii.
            if (!isActive) {
                clearCheckboxes(block);
            }
        });

        updatePreviewCategory();
        updatePreviewTags();
    };

    categorySelect.addEventListener("change", updateCatalogCategoryFields);
    subcategorySelect?.addEventListener("change", updatePreviewCategory);
    titleInput?.addEventListener("input", updatePreviewText);
    pickReasonInput?.addEventListener("input", updatePreviewText);
    bannerInput?.addEventListener("change", updatePreviewImage);
    bannerClearInput?.addEventListener("change", updatePreviewImage);

    // Tagi mogą zmieniać się pojedynczo, więc łapiemy to zbiorczo na formularzu,
    // zamiast podpinać osobny listener pod każdy checkbox.
    form.addEventListener("change", (event) => {
        if (event.target.matches('input[name="tags"]')) {
            updatePreviewTags();
        }
    });

    // Na starcie synchronizujemy cały formularz z preview,
    // żeby edycja istniejącego wpisu od razu pokazywała aktualny stan.
    updateCatalogCategoryFields();
    updatePreviewText();
    updatePreviewImage();
});
