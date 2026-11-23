// Publications: search and filters, BibTeX toggle and copy.
(function () {
  "use strict";

  // ---- Cite buttons (also used on project pages)
  document.querySelectorAll(".pub-cite").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var panel = document.getElementById(btn.getAttribute("aria-controls"));
      var open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!open));
      panel.hidden = open;
    });
  });
  document.querySelectorAll(".copy-bib").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var panel = btn.closest(".bibtex");
      var text = panel.querySelector("code").textContent;
      var status = panel.querySelector(".copy-status");
      function done(msg) { status.textContent = msg; setTimeout(function () { status.textContent = ""; }, 2500); }
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function () { done("Copied to clipboard"); }, function () { done("Select the text above to copy it"); });
      } else {
        var range = document.createRange();
        range.selectNodeContents(panel.querySelector("code"));
        var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);
        done("Text selected. Press Ctrl+C or Cmd+C to copy");
      }
    });
  });

  // ---- Filters (Publications page only)
  var form = document.querySelector(".pub-filters");
  if (!form) return;
  var search = document.getElementById("pub-search");
  var year = document.getElementById("pub-year");
  var project = document.getElementById("pub-project");
  var pubs = Array.prototype.slice.call(document.querySelectorAll(".pub"));
  var yearGroups = Array.prototype.slice.call(document.querySelectorAll(".pub-year"));
  var sections = Array.prototype.slice.call(document.querySelectorAll(".pub-section"));
  var counter = document.querySelector("[data-count]");
  var empty = document.querySelector(".empty-state");

  function apply() {
    var q = search.value.trim().toLowerCase();
    var type = form.querySelector("input[name=ptype]:checked").value;
    var y = year.value, p = project.value, shown = 0;
    pubs.forEach(function (el) {
      var ok = (type === "all" || el.dataset.type === type) &&
               (y === "all" || el.dataset.year === y) &&
               (p === "all" || (" " + el.dataset.projects + " ").indexOf(" " + p + " ") > -1) &&
               (!q || q.split(/\s+/).every(function (w) { return el.dataset.search.indexOf(w) > -1; }));
      el.hidden = !ok;
      if (ok) shown++;
    });
    yearGroups.forEach(function (g) { g.hidden = !g.querySelector(".pub:not([hidden])"); });
    sections.forEach(function (s) { s.hidden = !s.querySelector(".pub:not([hidden])"); });
    counter.textContent = shown;
    empty.hidden = shown !== 0;
  }
  function reset() {
    form.reset();
    apply();
    search.focus();
  }
  form.addEventListener("input", apply);
  form.addEventListener("change", apply);
  document.getElementById("pub-reset").addEventListener("click", reset);
  document.querySelectorAll("[data-reset]").forEach(function (b) { b.addEventListener("click", reset); });

  // If the page was opened at a specific paper (e.g. #J25), open its citation
  if (location.hash) {
    var target = document.getElementById(location.hash.slice(1));
    if (target && target.classList.contains("pub")) target.scrollIntoView();
  }
})();
