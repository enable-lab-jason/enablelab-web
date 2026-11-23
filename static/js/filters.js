// Chip filters for the Research and News pages.
// Buttons carry data-filter; items carry data-theme; optional groups carry data-year-group.
(function () {
  "use strict";
  var chips = Array.prototype.slice.call(document.querySelectorAll(".chip[data-filter]"));
  if (!chips.length) return;
  var items = Array.prototype.slice.call(document.querySelectorAll("[data-theme]"));
  var groups = Array.prototype.slice.call(document.querySelectorAll("[data-year-group]"));
  var counter = document.querySelector("[data-count]");

  function apply(value, updateHash) {
    var shown = 0;
    chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c.dataset.filter === value)); });
    items.forEach(function (it) {
      var match = value === "all" || it.dataset.theme === value;
      it.hidden = !match;
      if (match) shown++;
    });
    groups.forEach(function (g) { g.hidden = !g.querySelector("[data-theme]:not([hidden])"); });
    if (counter) counter.textContent = shown;
    if (updateHash) history.replaceState(null, "", value === "all" ? location.pathname : "#" + value);
  }

  chips.forEach(function (c) {
    c.addEventListener("click", function () { apply(c.dataset.filter, true); });
  });

  // Links such as research/#wearable-technologies preselect a filter
  var hash = decodeURIComponent(location.hash.slice(1));
  if (hash && chips.some(function (c) { return c.dataset.filter === hash; })) apply(hash, false);
})();
