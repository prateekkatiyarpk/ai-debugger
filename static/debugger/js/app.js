(function () {
  const root = document.documentElement;
  const themeToggle = document.getElementById("theme-toggle");
  const themeToggleValue = document.getElementById("theme-toggle-value");
  const themeMediaQuery = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
  const THEME_STORAGE_KEY = "ai-debugger-theme";
  const demoButton = document.getElementById("load-demo");
  const errorLog = document.getElementById("id_error_log");
  const reproCommand = document.getElementById("id_repro_command");
  const codeContext = document.getElementById("id_code_context");
  const githubUrl = document.getElementById("id_github_url");
  const repoZip = document.getElementById("id_repo_zip");
  const form = document.getElementById("debug-form");
  const submitStatus = document.getElementById("submit-status");
  const submitButton = document.querySelector("[data-submit-button]");

  function storedTheme() {
    try {
      return localStorage.getItem(THEME_STORAGE_KEY);
    } catch (error) {
      return "";
    }
  }

  function preferredTheme() {
    if (root.dataset.theme === "dark" || root.dataset.theme === "light") {
      return root.dataset.theme;
    }
    if (themeMediaQuery && themeMediaQuery.matches) {
      return "dark";
    }
    return "light";
  }

  function updateThemeToggle(theme) {
    if (!themeToggle || !themeToggleValue) {
      return;
    }
    const isDark = theme === "dark";
    themeToggleValue.textContent = isDark ? "Dark" : "Light";
    themeToggle.setAttribute("aria-pressed", String(isDark));
    themeToggle.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
    themeToggle.title = isDark ? "Switch to light mode" : "Switch to dark mode";
  }

  function applyTheme(theme, persist) {
    root.dataset.theme = theme;
    updateThemeToggle(theme);
    if (!persist) {
      return;
    }
    try {
      localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch (error) {
      return;
    }
  }

  updateThemeToggle(preferredTheme());

  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      applyTheme(preferredTheme() === "dark" ? "light" : "dark", true);
    });
  }

  if (themeMediaQuery) {
    const syncTheme = function (event) {
      if (storedTheme()) {
        return;
      }
      applyTheme(event.matches ? "dark" : "light", false);
    };

    if (themeMediaQuery.addEventListener) {
      themeMediaQuery.addEventListener("change", syncTheme);
    } else if (themeMediaQuery.addListener) {
      themeMediaQuery.addListener(syncTheme);
    }
  }

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
    if (reproCommand) {
      reproCommand.value = "";
    }
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
