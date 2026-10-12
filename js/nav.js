(function () {
  "use strict";

  var STORAGE_THEME = "director-site-theme";
  var STORAGE_PROGRESS = "director-site-progress";

  /* Theme */
  function getPreferredTheme() {
    var saved = localStorage.getItem(STORAGE_THEME);
    if (saved === "light" || saved === "dark") return saved;
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(STORAGE_THEME, theme);
    var btn = document.getElementById("theme-toggle");
    if (btn) {
      btn.setAttribute("aria-label", theme === "dark" ? "切换到浅色" : "切换到深色");
      btn.textContent = theme === "dark" ? "☀" : "☾";
      btn.title = theme === "dark" ? "浅色模式" : "深色模式";
    }
  }

  applyTheme(getPreferredTheme());

  document.addEventListener("DOMContentLoaded", function () {
    var themeBtn = document.getElementById("theme-toggle");
    if (themeBtn) {
      themeBtn.addEventListener("click", function () {
        var cur = document.documentElement.getAttribute("data-theme");
        applyTheme(cur === "dark" ? "light" : "dark");
      });
    }

    /* Mobile sidebar */
    var sidebar = document.getElementById("sidebar");
    var overlay = document.getElementById("sidebar-overlay");
    var menuBtn = document.getElementById("menu-toggle");

    function closeSidebar() {
      if (sidebar) sidebar.classList.remove("open");
      if (overlay) overlay.classList.remove("open");
    }
    function openSidebar() {
      if (sidebar) sidebar.classList.add("open");
      if (overlay) overlay.classList.add("open");
    }

    if (menuBtn) {
      menuBtn.addEventListener("click", function () {
        if (sidebar && sidebar.classList.contains("open")) closeSidebar();
        else openSidebar();
      });
    }
    if (overlay) overlay.addEventListener("click", closeSidebar);

    /* Active nav link */
    var path = location.pathname.replace(/\\/g, "/");
    var file = path.split("/").pop() || "index.html";
    var folder = "";
    var parts = path.split("/").filter(Boolean);
    if (parts.length >= 2) {
      folder = parts[parts.length - 2];
    }
    /* Also handle file:// paths */
    if (!folder && path.indexOf("stage") !== -1) {
      var m = path.match(/(stage\d|appendix)/);
      if (m) folder = m[1];
    }

    document.querySelectorAll(".sidebar a[href]").forEach(function (a) {
      var href = a.getAttribute("href") || "";
      var hrefFile = href.split("/").pop();
      var isActive = false;
      if (href === file || href.endsWith("/" + file)) isActive = true;
      if (folder && href.indexOf(folder + "/" + file) !== -1) isActive = true;
      /* relative from same folder */
      if (hrefFile === file && !href.startsWith("../") && !href.startsWith("http")) {
        if (folder === "stage1" || folder === "stage2" || folder === "stage3" || folder === "stage4" || folder === "appendix") {
          if (!href.includes("/") || href.startsWith("./")) isActive = true;
        }
      }
      if (isActive) {
        a.classList.add("active");
        var details = a.closest("details");
        if (details) details.open = true;
      }
    });

    /* Back to top */
    var topBtn = document.getElementById("back-to-top");
    if (topBtn) {
      window.addEventListener("scroll", function () {
        if (window.scrollY > 400) topBtn.classList.add("visible");
        else topBtn.classList.remove("visible");
      });
      topBtn.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    }

    /* Progress tracking */
    var pageId = document.body.getAttribute("data-page");
    if (pageId) {
      markVisited(pageId);
      updateProgressUI();
    }

    /* Checklists persistence */
    document.querySelectorAll(".checklist input[type=checkbox]").forEach(function (cb) {
      var key = "check-" + (cb.id || cb.getAttribute("data-key") || "");
      if (!key || key === "check-") return;
      if (localStorage.getItem(key) === "1") cb.checked = true;
      cb.addEventListener("change", function () {
        localStorage.setItem(key, cb.checked ? "1" : "0");
        updateProgressUI();
      });
    });

    /* Glossary search */
    var search = document.getElementById("glossary-search");
    if (search) {
      search.addEventListener("input", function () {
        var q = search.value.trim().toLowerCase();
        document.querySelectorAll(".term-row").forEach(function (row) {
          var text = row.textContent.toLowerCase();
          row.classList.toggle("hidden", q && text.indexOf(q) === -1);
        });
      });
    }
  });

  function getProgress() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_PROGRESS) || "{}");
    } catch (e) {
      return {};
    }
  }

  function markVisited(pageId) {
    var p = getProgress();
    p[pageId] = true;
    localStorage.setItem(STORAGE_PROGRESS, JSON.stringify(p));
  }

  function updateProgressUI() {
    var total = parseInt(document.body.getAttribute("data-total-pages") || "0", 10);
    var bar = document.getElementById("progress-bar-fill");
    var text = document.getElementById("progress-text");
    if (!total || (!bar && !text)) return;
    var p = getProgress();
    var count = Object.keys(p).filter(function (k) { return p[k]; }).length;
    var pct = Math.min(100, Math.round((count / total) * 100));
    if (bar) bar.style.width = pct + "%";
    if (text) text.textContent = "已浏览 " + count + " / " + total + " 页（" + pct + "%）";
  }

  window.DirectorSite = { markVisited: markVisited, getProgress: getProgress };
})();
