(function () {
  const demoButton = document.getElementById("load-demo");
  const errorLog = document.getElementById("id_error_log");
  const codeContext = document.getElementById("id_code_context");

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
    errorLog.focus();
  });
})();
