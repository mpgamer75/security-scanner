/* Red Team Field Report — client behavior. No dependencies. Progressive:
   the report is fully readable with JS disabled; this adds filter/sort/theme. */
(function () {
  "use strict";

  /* ---- Theme toggle (persisted) ---- */
  var root = document.documentElement;
  var stored = null;
  try { stored = localStorage.getItem("rt-theme"); } catch (e) {}
  if (stored) root.setAttribute("data-theme", stored);

  var toggle = document.querySelector(".theme-toggle");
  if (toggle) {
    var sync = function () {
      var dark = root.getAttribute("data-theme") === "dark" ||
        (!root.getAttribute("data-theme") &&
          window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
      toggle.textContent = dark ? "☀ Light" : "☾ Dark";
    };
    toggle.addEventListener("click", function () {
      var dark = root.getAttribute("data-theme") === "dark" ||
        (!root.getAttribute("data-theme") &&
          window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
      var next = dark ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("rt-theme", next); } catch (e) {}
      sync();
    });
    sync();
  }

  /* ---- Findings filter / search / sort ---- */
  var table = document.getElementById("findings-table");
  if (!table) return;

  var activeSeverities = new Set();
  var searchTerm = "";
  var searchBox = document.getElementById("finding-search");
  var emptyHint = document.getElementById("findings-empty");

  var rows = function () {
    return Array.prototype.slice.call(table.querySelectorAll("tbody tr.frow"));
  };

  function applyFilters() {
    var shown = 0;
    rows().forEach(function (row) {
      var sev = row.getAttribute("data-sev");
      var hay = (row.getAttribute("data-search") || "").toLowerCase();
      var sevOk = activeSeverities.size === 0 || activeSeverities.has(sev);
      var textOk = !searchTerm || hay.indexOf(searchTerm) !== -1;
      var visible = sevOk && textOk;
      row.classList.toggle("hidden", !visible);
      var ev = row.nextElementSibling;
      if (ev && ev.classList.contains("evidence-row") && !visible) ev.classList.add("hidden");
      if (visible) shown++;
    });
    if (emptyHint) emptyHint.classList.toggle("hidden", shown !== 0);
  }

  function toggleSeverity(sev, pressed) {
    if (pressed) activeSeverities.add(sev); else activeSeverities.delete(sev);
    document.querySelectorAll('[data-sev-filter="' + sev + '"]').forEach(function (el) {
      el.setAttribute("aria-pressed", pressed ? "true" : "false");
    });
    applyFilters();
  }

  document.querySelectorAll("[data-sev-filter]").forEach(function (el) {
    if (el.classList.contains("empty")) return;
    el.addEventListener("click", function () {
      var sev = el.getAttribute("data-sev-filter");
      toggleSeverity(sev, el.getAttribute("aria-pressed") !== "true");
    });
  });

  if (searchBox) {
    searchBox.addEventListener("input", function () {
      searchTerm = searchBox.value.trim().toLowerCase();
      applyFilters();
    });
  }

  /* ---- Sort ---- */
  var sortState = { key: "severity", dir: -1 };
  function sortBy(key) {
    var tbody = table.querySelector("tbody");
    if (sortState.key === key) sortState.dir *= -1;
    else { sortState.key = key; sortState.dir = key === "severity" ? -1 : 1; }
    var pairs = rows().map(function (row) {
      var ev = row.nextElementSibling;
      return { row: row, ev: (ev && ev.classList.contains("evidence-row")) ? ev : null };
    });
    pairs.sort(function (a, b) {
      var av = a.row.getAttribute("data-" + key) || "";
      var bv = b.row.getAttribute("data-" + key) || "";
      if (key === "severity" || key === "port") {
        av = parseFloat(av) || 0; bv = parseFloat(bv) || 0;
        return (av - bv) * sortState.dir;
      }
      return av.localeCompare(bv) * sortState.dir;
    });
    pairs.forEach(function (p) { tbody.appendChild(p.row); if (p.ev) tbody.appendChild(p.ev); });
  }
  document.querySelectorAll("th.sortable").forEach(function (th) {
    th.addEventListener("click", function () { sortBy(th.getAttribute("data-sort")); });
  });

  /* ---- Evidence expand ---- */
  document.querySelectorAll(".expand-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var id = btn.getAttribute("data-target");
      var ev = document.getElementById(id);
      if (!ev) return;
      var open = !ev.classList.contains("hidden");
      ev.classList.toggle("hidden", open);
      btn.textContent = open ? "+" : "−";
      btn.setAttribute("aria-expanded", open ? "false" : "true");
    });
  });

  /* ---- Exports ---- */
  var dataEl = document.getElementById("report-data");
  var data = null;
  if (dataEl) { try { data = JSON.parse(dataEl.textContent); } catch (e) {} }

  function download(name, text, type) {
    var blob = new Blob([text], { type: type });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url; a.download = name; document.body.appendChild(a); a.click();
    document.body.removeChild(a); URL.revokeObjectURL(url);
  }

  var jsonBtn = document.getElementById("export-json");
  if (jsonBtn && data) {
    jsonBtn.addEventListener("click", function () {
      download("assessment.json", JSON.stringify(data, null, 2), "application/json");
    });
  }
  var mdBtn = document.getElementById("copy-markdown");
  if (mdBtn) {
    mdBtn.addEventListener("click", function () {
      var md = document.getElementById("markdown-source");
      var text = md ? md.textContent : "";
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () {
          var prev = mdBtn.textContent; mdBtn.textContent = "Copied";
          setTimeout(function () { mdBtn.textContent = prev; }, 1400);
        });
      } else {
        download("assessment.md", text, "text/markdown");
      }
    });
  }
})();
