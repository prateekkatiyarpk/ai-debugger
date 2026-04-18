(function () {
  const demoButton = document.getElementById("load-demo");
  const errorLog = document.getElementById("id_error_log");
  const codeContext = document.getElementById("id_code_context");
  const githubUrl = document.getElementById("id_github_url");
  const repoZip = document.getElementById("id_repo_zip");
  const form = document.getElementById("debug-form");
  const submitStatus = document.getElementById("submit-status");
  const submitButton = document.querySelector("[data-submit-button]");

  if (!demoButton || !errorLog || !codeContext) {
    return;
  }

  function readJsonScript(id) {
    const node = document.getElementById(id);
    if (!node) {
      return "";
    }
    return JSON.parse(node.textContent);
  }

  demoButton.addEventListener("click", function () {
    errorLog.value = readJsonScript("demo-error-log");
    codeContext.value = readJsonScript("demo-code-context");
    if (githubUrl) {
      githubUrl.value = "";
    }
    if (repoZip) {
      repoZip.value = "";
    }
    errorLog.focus();
  });

  if (form && submitButton) {
    form.addEventListener("submit", function () {
      if (!form.checkValidity()) {
        return;
      }
      submitButton.textContent = "Analyzing...";
      submitButton.disabled = true;
      demoButton.disabled = true;
      if (submitStatus) {
        submitStatus.hidden = false;
      }
    });
  }

  document.querySelectorAll("[data-copy-source]").forEach(function (button) {
    button.addEventListener("click", function () {
      const source = document.getElementById(button.dataset.copySource);
      if (!source || !navigator.clipboard) {
        return;
      }

      let text = source.textContent;
      if (source.type === "application/json") {
        text = JSON.stringify(JSON.parse(source.textContent), null, 2);
      }

      navigator.clipboard.writeText(text).then(function () {
        const original = button.textContent;
        button.textContent = "Copied";
        window.setTimeout(function () {
          button.textContent = original;
        }, 1400);
      });
    });
  });
})();
