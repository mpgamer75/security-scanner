/* Red Team Field Report — client behavior. No dependencies. Progressive:
   the report is fully readable with JS disabled; this adds filter/sort/theme,
   a live result count, clickable status readout, and an animated risk gauge. */
(function () {
  "use strict";

  /* ---- Theme toggle (persisted) ---- */
  var root = document.documentElement;
  var stored = null;
  try { stored = localStorage.getItem("rt-theme"); } catch (e) {}
  if (stored) root.setAttribute("data-theme", stored);

  function isDark() {
    return root.getAttribute("data-theme") === "dark" ||
      (!root.getAttribute("data-theme") &&
        window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
  }
  var toggle = document.querySelector(".theme-toggle");
  if (toggle) {
    var syncToggle = function () { toggle.textContent = isDark() ? "☀ Light" : "☾ Dark"; };
    toggle.addEventListener("click", function () {
      var next = isDark() ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("rt-theme", next); } catch (e) {}
      syncToggle();
    });
    syncToggle();
  }

  /* ---- Animated risk gauge (draw the arc 0 -> score on load) ---- */
  var arc = document.getElementById("gauge-arc");
  if (arc) {
    var score = parseFloat(arc.getAttribute("data-score")) || 0;
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      arc.setAttribute("stroke-dasharray", score + " 100");
    } else if (window.requestAnimationFrame) {
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { arc.setAttribute("stroke-dasharray", score + " 100"); });
      });
    } else {
      arc.setAttribute("stroke-dasharray", score + " 100");
    }
  }

  /* ---- Section jumping (used by the status readout) ---- */
  function scrollToId(id) {
    var el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  /* ---- Findings filter / search / sort ---- */
  var table = document.getElementById("findings-table");
  var searchBox = document.getElementById("finding-search");
  var emptyHint = document.getElementById("findings-empty");
  var countEl = document.getElementById("findings-count");
  var clearBtn = document.getElementById("clear-filters");
  var totalFindings = countEl ? (parseInt(countEl.getAttribute("data-total"), 10) || 0) : 0;

  var activeSeverities = new Set();
  var searchTerm = "";

  function rows() {
    return table ? Array.prototype.slice.call(table.querySelectorAll("tbody tr.frow")) : [];
  }
  function filtersActive() { return activeSeverities.size > 0 || searchTerm.length > 0; }

  function updateChrome(shown) {
    if (countEl) {
      countEl.textContent = filtersActive()
        ? (shown + " of " + totalFindings + " shown")
        : (totalFindings + " total");
    }
    if (clearBtn) clearBtn.classList.toggle("hidden", !filtersActive());
    // Dim severity bands not in the active filter so the spine reflects state.
    document.querySelectorAll("[data-sev-filter]").forEach(function (el) {
      var sev = el.getAttribute("data-sev-filter");
      el.classList.toggle("dimmed", activeSeverities.size > 0 && !activeSeverities.has(sev));
    });
  }

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
    updateChrome(shown);
  }

  function setSeverity(sev, pressed) {
    if (pressed) activeSeverities.add(sev); else activeSeverities.delete(sev);
    document.querySelectorAll('[data-sev-filter="' + sev + '"]').forEach(function (el) {
      el.setAttribute("aria-pressed", pressed ? "true" : "false");
    });
    applyFilters();
  }
  function toggleSeverity(sev) { setSeverity(sev, !activeSeverities.has(sev)); }

  document.querySelectorAll("[data-sev-filter]").forEach(function (el) {
    if (el.classList.contains("empty")) return;
    el.addEventListener("click", function () { toggleSeverity(el.getAttribute("data-sev-filter")); });
  });

  if (searchBox) {
    searchBox.addEventListener("input", function () {
      searchTerm = searchBox.value.trim().toLowerCase();
      applyFilters();
    });
  }

  function clearAll() {
    activeSeverities.clear();
    if (searchBox) searchBox.value = "";
    searchTerm = "";
    document.querySelectorAll("[data-sev-filter]").forEach(function (el) {
      el.setAttribute("aria-pressed", "false");
    });
    applyFilters();
  }
  if (clearBtn) clearBtn.addEventListener("click", clearAll);

  /* ---- Status readout: severity stats filter; the rest jump to a section ---- */
  document.querySelectorAll(".statusline .stat").forEach(function (el) {
    el.addEventListener("click", function () {
      var sev = el.getAttribute("data-sev");
      var jump = el.getAttribute("data-jump");
      if (sev) { toggleSeverity(sev); scrollToId("findings"); }
      else if (jump) { scrollToId(jump); }
    });
  });

  /* ---- Sort ---- */
  var sortState = { key: "severity", dir: -1 };
  function markSort() {
    document.querySelectorAll("th.sortable").forEach(function (th) {
      th.classList.remove("sort-asc", "sort-desc");
      if (th.getAttribute("data-sort") === sortState.key) {
        th.classList.add(sortState.dir === 1 ? "sort-asc" : "sort-desc");
      }
    });
  }
  function sortBy(key) {
    if (!table) return;
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
    markSort();
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

  /* ---- Keyboard: "/" focuses search, Esc clears filters ---- */
  document.addEventListener("keydown", function (e) {
    if (e.key === "/" && searchBox && document.activeElement !== searchBox) {
      e.preventDefault(); searchBox.focus();
    } else if (e.key === "Escape") {
      if (document.activeElement === searchBox) searchBox.blur();
      if (filtersActive()) clearAll();
    }
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
  var navBtn = document.getElementById("export-navigator");
  var navEl = document.getElementById("navigator-data");
  if (navBtn && navEl) {
    navBtn.addEventListener("click", function () {
      download("navigator.json", navEl.textContent, "application/json");
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

  /* ---- Initial sync ---- */
  markSort();
  updateChrome(totalFindings);
})();
