const form = document.querySelector("[data-analysis-form]");
const submitButton = document.querySelector("[data-submit-button]");
const loader = document.querySelector("[data-loader]");
const fileInput = document.querySelector("[data-file-input]");
const fileMeta = document.querySelector("[data-file-meta]");
const copyButton = document.querySelector("[data-copy-button]");
const reportContent = document.querySelector("[data-report-content]");

if (fileInput && fileMeta) {
    fileInput.addEventListener("change", () => {
        const file = fileInput.files && fileInput.files[0];

        if (!file) {
            fileMeta.textContent = "Nenhum arquivo selecionado.";
            return;
        }

        const sizeInMegabytes = (file.size / (1024 * 1024)).toFixed(2);
        fileMeta.textContent = `${file.name} • ${sizeInMegabytes} MB`;

        if (file.size > 10 * 1024 * 1024) {
            fileInput.setCustomValidity("O arquivo excede o limite de 10 MB.");
            fileMeta.textContent += " • Arquivo acima do limite";
        } else {
            fileInput.setCustomValidity("");
        }
    });
}

if (form && submitButton && loader) {
    form.addEventListener("submit", () => {
        submitButton.disabled = true;
        submitButton.textContent = "Analisando contrato...";
        loader.classList.add("is-visible");
    });
}

if (copyButton && reportContent) {
    copyButton.addEventListener("click", async () => {
        const originalText = copyButton.textContent;

        try {
            await navigator.clipboard.writeText(reportContent.textContent || "");
            copyButton.textContent = "Relatório copiado";
        } catch (_error) {
            copyButton.textContent = "Não foi possível copiar";
        }

        window.setTimeout(() => {
            copyButton.textContent = originalText;
        }, 2200);
    });
}
