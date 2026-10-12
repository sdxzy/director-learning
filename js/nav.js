(function () {
  "use strict";

  var STORAGE_THEME = "director-site-theme";
  var STORAGE_LEARNED = "director-site-learned";
  var mqDesktop = window.matchMedia("(min-width: 1181px)");
  var mqMobile = window.matchMedia("(max-width: 860px)");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  var ICON_SUN =
    '<svg class="icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
  var ICON_MOON =
    '<svg class="icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M21 14.5A8.5 8.5 0 1 1 9.5 3 7 7 0 0 0 21 14.5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>';

  function savedTheme() {
    try {
      var saved = localStorage.getItem(STORAGE_THEME);
      if (saved === "light" || saved === "dark") return saved;
    } catch (e) {}
    return null;
  }

  function systemTheme() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }

  function paintTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.style.colorScheme = theme;
    var meta = document.querySelector('meta[name="theme-color"]');
    if (!meta) {
      meta = document.createElement("meta");
      meta.setAttribute("name", "theme-color");
      document.head.appendChild(meta);
    }
    meta.setAttribute("content", theme === "dark" ? "#121417" : "#f6f5f2");
    var btn = document.getElementById("theme-toggle");
    if (btn) {
      var toLight = theme === "dark";
      btn.setAttribute("aria-label", toLight ? "切换到浅色" : "切换到深色");
      btn.title = toLight ? "浅色模式" : "深色模式";
      btn.innerHTML = toLight ? ICON_SUN : ICON_MOON;
    }
  }

  if (!document.documentElement.getAttribute("data-theme")) {
    paintTheme(savedTheme() || systemTheme());
  }

  function assetPrefix() {
    var s = document.querySelector("script[src*='nav.js']");
    var src = s ? s.getAttribute("src") || "" : "";
    var i = src.lastIndexOf("js/nav.js");
    return i === -1 ? "" : src.slice(0, i);
  }

  function pathKey(url) {
    var u;
    try {
      u = new URL(url, window.location.href);
    } catch (e) {
      return "";
    }
    var p = decodeURIComponent(u.pathname).replace(/\/+$/, "");
    if (p.toLowerCase().endsWith("/index.html")) p = p.slice(0, -"/index.html".length);
    else if (p.toLowerCase().endsWith("index.html")) p = p.slice(0, -"index.html".length).replace(/\/$/, "");
    return p;
  }

  function prefersReduced() {
    return reduceMotion.matches;
  }

  (function openTocIfDesktop() {
    var details = document.getElementById("toc-details");
    if (details && mqDesktop.matches) details.open = true;
  })();

  document.addEventListener("DOMContentLoaded", function () {
    paintTheme(currentTheme());

    var themeBtn = document.getElementById("theme-toggle");
    if (themeBtn) {
      themeBtn.addEventListener("click", function () {
        var next = currentTheme() === "dark" ? "light" : "dark";
        try { localStorage.setItem(STORAGE_THEME, next); } catch (e) {}
        paintTheme(next);
      });
    }

    var scheme = window.matchMedia("(prefers-color-scheme: dark)");
    if (scheme.addEventListener) {
      scheme.addEventListener("change", function (e) {
        if (!savedTheme()) paintTheme(e.matches ? "dark" : "light");
      });
    }

    setupNav();
    setupMobileNav();
    wrapPractice();
    buildToc();
    setupScrollSpy();
    setupReadProgress();
    setupLearnProgress();
    setupChecklists();
    setupGlossary();
    setupSearch();
    setupBackToTop();
    var kbd = document.getElementById("search-kbd");
    if (kbd && /Mac|iPhone|iPad/.test(navigator.userAgent)) kbd.textContent = "⌘K";
  });

  function setupNav() {
    var here = pathKey(window.location.href);
    var active = null;
    document.querySelectorAll(".sidebar-nav a[href]").forEach(function (a) {
      if (pathKey(a.href) === here) {
        a.classList.add("active");
        a.setAttribute("aria-current", "page");
        active = a;
        var details = a.closest("details");
        if (details) details.open = true;
      }
    });
    if (active) {
      var nav = document.querySelector(".sidebar-nav");
      if (nav) {
        var top = active.offsetTop;
        var bottom = top + active.offsetHeight;
        if (top < nav.scrollTop || bottom > nav.scrollTop + nav.clientHeight) {
          nav.scrollTop = Math.max(0, top - nav.clientHeight / 3);
        }
      }
    }
  }

  function setupMobileNav() {
    var sidebar = document.getElementById("sidebar");
    var overlay = document.getElementById("sidebar-overlay");
    var menuBtn = document.getElementById("menu-toggle");
    var doc = document.querySelector(".doc-shell");
    if (!sidebar || !menuBtn) return;

    function setInert(on) {
      if (!doc) return;
      try { doc.inert = on; } catch (e) {}
    }

    function closeSidebar() {
      sidebar.classList.remove("open");
      if (overlay) overlay.classList.remove("open");
      menuBtn.setAttribute("aria-expanded", "false");
      menuBtn.setAttribute("aria-label", "打开菜单");
      document.body.classList.remove("scroll-lock");
      setInert(false);
    }
    function openSidebar() {
      sidebar.classList.add("open");
      if (overlay) overlay.classList.add("open");
      menuBtn.setAttribute("aria-expanded", "true");
      menuBtn.setAttribute("aria-label", "关闭菜单");
      document.body.classList.add("scroll-lock");
      setInert(true);
      var first = sidebar.querySelector("a, summary");
      if (first) first.focus();
    }

    menuBtn.addEventListener("click", function () {
      if (sidebar.classList.contains("open")) closeSidebar();
      else openSidebar();
    });
    if (overlay) overlay.addEventListener("click", closeSidebar);
    sidebar.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        if (mqMobile.matches) closeSidebar();
      });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && sidebar.classList.contains("open")) {
        closeSidebar();
        menuBtn.focus();
      }
    });
    if (mqMobile.addEventListener) {
      mqMobile.addEventListener("change", function (e) {
        if (!e.matches) closeSidebar();
      });
    }
    window.DirectorSite = window.DirectorSite || {};
    window.DirectorSite.closeSidebar = closeSidebar;
  }

  function wrapPractice() {
    document.querySelectorAll("main h3").forEach(function (h) {
      if ((h.textContent || "").trim() !== "练一练") return;
      if (h.closest(".callout-practice")) return;
      var box = document.createElement("div");
      box.className = "callout callout-practice";
      h.parentNode.insertBefore(box, h);
      box.appendChild(h);
      var n = box.nextSibling;
      while (n) {
        if (n.nodeType === 1) {
          var tag = n.tagName;
          if (/^H[1-3]$/.test(tag)) break;
          if (n.classList.contains("remember") || n.classList.contains("tip") ||
              n.classList.contains("warning-box") || n.classList.contains("example") ||
              n.classList.contains("chapter-nav") || n.classList.contains("learn-card")) break;
        }
        var next = n.nextSibling;
        box.appendChild(n);
        n = next;
      }
    });
  }

  function slugify(text, used) {
    var base = (text || "").trim().replace(/\s+/g, "-").replace(/[^\w\u4e00-\u9fff\-]+/g, "");
    if (!base) base = "section";
    var s = base;
    var i = 2;
    while (used[s] || document.getElementById(s)) {
      s = base + "-" + i;
      i += 1;
    }
    used[s] = true;
    return s;
  }

  function headingNodes() {
    return Array.prototype.filter.call(
      document.querySelectorAll("main h2, main h3"),
      function (h) {
        return !h.closest(".card, .habit, .chapter-nav, .learn-card, .syllabus");
      }
    );
  }

  function buildToc() {
    var list = document.getElementById("toc-list");
    var aside = document.getElementById("toc-aside");
    var layout = document.querySelector(".layout");
    if (!list || !aside) return;
    var headings = headingNodes();
    if (!headings.length) {
      aside.hidden = true;
      if (layout) layout.classList.add("toc-empty");
      return;
    }
    var used = {};
    var root = list;
    var sub = null;
    headings.forEach(function (h) {
      if (!h.id) h.id = slugify(h.textContent, used);
      else used[h.id] = true;
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = "#" + h.id;
      a.textContent = (h.textContent || "").trim();
      li.appendChild(a);
      if (h.tagName === "H2") {
        root.appendChild(li);
        sub = document.createElement("ol");
        li.appendChild(sub);
      } else if (sub) {
        sub.appendChild(li);
      } else {
        root.appendChild(li);
      }
      a.addEventListener("click", function (e) {
        e.preventDefault();
        h.scrollIntoView({ behavior: prefersReduced() ? "auto" : "smooth", block: "start" });
        if (history.replaceState) history.replaceState(null, "", "#" + h.id);
        setTocActive(a);
        if (!mqDesktop.matches) {
          var details = document.getElementById("toc-details");
          if (details) details.open = false;
        }
      });
    });
    if (mqDesktop.addEventListener) {
      mqDesktop.addEventListener("change", function (e) {
        var details = document.getElementById("toc-details");
        if (details && e.matches) details.open = true;
      });
    }
  }

  function setTocActive(link) {
    document.querySelectorAll(".toc-nav a.active").forEach(function (a) {
      a.classList.remove("active");
    });
    if (link) link.classList.add("active");
  }

  function setupScrollSpy() {
    var links = Array.prototype.slice.call(document.querySelectorAll(".toc-nav a"));
    if (!links.length || !("IntersectionObserver" in window)) return;
    var byId = {};
    links.forEach(function (a) {
      var id = (a.getAttribute("href") || "").slice(1);
      if (id) byId[id] = a;
    });
    if (links[0]) setTocActive(links[0]);
    var visible = [];
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var id = entry.target.id;
        var idx = visible.indexOf(id);
        if (entry.isIntersecting && idx === -1) visible.push(id);
        if (!entry.isIntersecting && idx !== -1) visible.splice(idx, 1);
      });
      if (!visible.length) return;
      visible.sort(function (a, b) {
        var ea = document.getElementById(a);
        var eb = document.getElementById(b);
        if (!ea || !eb) return 0;
        return ea.getBoundingClientRect().top - eb.getBoundingClientRect().top;
      });
      setTocActive(byId[visible[0]]);
    }, { rootMargin: "-80px 0px -65% 0px", threshold: [0, 1] });
    headingNodes().forEach(function (h) { if (h.id) observer.observe(h); });
  }

  function setupReadProgress() {
    var bar = document.getElementById("read-progress-fill");
    if (!bar) return;
    var ticking = false;
    function update() {
      var doc = document.documentElement;
      var max = doc.scrollHeight - window.innerHeight;
      var pct = max > 0 ? Math.min(100, (window.scrollY / max) * 100) : 0;
      bar.style.width = pct + "%";
      ticking = false;
    }
    window.addEventListener("scroll", function () {
      if (!ticking) {
        window.requestAnimationFrame(update);
        ticking = true;
      }
    }, { passive: true });
    update();
  }

  function getLearned() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_LEARNED) || "{}");
    } catch (e) {
      return {};
    }
  }

  function setLearned(map) {
    try { localStorage.setItem(STORAGE_LEARNED, JSON.stringify(map)); } catch (e) {}
  }

  function learnedCount(map) {
    return Object.keys(map).filter(function (k) { return map[k]; }).length;
  }

  function updateProgressUI() {
    var total = parseInt(document.body.getAttribute("data-total-pages") || "0", 10);
    var map = getLearned();
    var count = learnedCount(map);
    var pct = total ? Math.min(100, Math.round((count / total) * 100)) : 0;
    var bar = document.getElementById("progress-bar-fill");
    var text = document.getElementById("progress-text");
    var meter = document.getElementById("progress-bar");
    if (bar) bar.style.width = pct + "%";
    if (text) text.textContent = "已学完 " + count + " / " + total + " 页（" + pct + "%）";
    if (meter) meter.setAttribute("aria-valuenow", String(pct));
    var foot = document.getElementById("sidebar-progress");
    if (foot) {
      foot.textContent = "";
      var link = document.createElement("a");
      link.href = assetPrefix() + "index.html";
      link.textContent = "已学完 " + count + " / " + total;
      var track = document.createElement("div");
      track.className = "sidebar-meter";
      track.setAttribute("aria-hidden", "true");
      var fill = document.createElement("span");
      fill.style.width = pct + "%";
      track.appendChild(fill);
      foot.appendChild(link);
      foot.appendChild(track);
    }
  }

  function setupLearnProgress() {
    var cb = document.getElementById("learn-complete");
    var card = document.getElementById("learn-card");
    var pageId = document.body.getAttribute("data-page");
    function sync() {
      if (!cb || !pageId) return;
      var on = !!getLearned()[pageId];
      cb.checked = on;
      if (card) card.classList.toggle("is-done", on);
    }
    if (cb && pageId) {
      sync();
      cb.addEventListener("change", function () {
        var map = getLearned();
        map[pageId] = cb.checked;
        setLearned(map);
        if (card) card.classList.toggle("is-done", cb.checked);
        updateProgressUI();
      });
    }
    updateProgressUI();
    window.addEventListener("storage", function (e) {
      if (e.key === STORAGE_LEARNED) {
        sync();
        updateProgressUI();
      }
    });
  }

  function setupChecklists() {
    document.querySelectorAll(".checklist input[type=checkbox]").forEach(function (box) {
      var key = "check-" + (box.id || box.getAttribute("data-key") || "");
      if (!key || key === "check-") return;
      if (localStorage.getItem(key) === "1") box.checked = true;
      box.addEventListener("change", function () {
        localStorage.setItem(key, box.checked ? "1" : "0");
      });
    });
  }

  function setupGlossary() {
    var search = document.getElementById("glossary-search");
    if (!search) return;
    search.addEventListener("input", function () {
      var q = search.value.trim().toLowerCase();
      document.querySelectorAll(".term-row").forEach(function (row) {
        row.classList.toggle("hidden", !!(q && row.textContent.toLowerCase().indexOf(q) === -1));
      });
    });
  }

  function setupBackToTop() {
    var topBtn = document.getElementById("back-to-top");
    if (!topBtn) return;
    window.addEventListener("scroll", function () {
      topBtn.classList.toggle("visible", window.scrollY > 500);
    }, { passive: true });
    topBtn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: prefersReduced() ? "auto" : "smooth" });
    });
  }

  function setupSearch() {
    var trigger = document.getElementById("search-trigger");
    if (!trigger) return;
    var modal = document.createElement("div");
    modal.className = "search-modal";
    modal.id = "search-modal";
    modal.hidden = true;
    modal.innerHTML =
      '<div class="search-backdrop" data-close="1"></div>' +
      '<div class="search-dialog" role="dialog" aria-modal="true" aria-labelledby="search-label">' +
      '<label id="search-label" class="sr-only" for="search-input">搜索全站</label>' +
      '<input class="search-input" id="search-input" type="search" placeholder="搜索课程、术语、练习…" autocomplete="off" enterkeyhint="search">' +
      '<ul class="search-results" id="search-results"></ul>' +
      '<p class="search-hint"><kbd>↑</kbd> <kbd>↓</kbd> 选择 · <kbd>Enter</kbd> 打开 · <kbd>Esc</kbd> 关闭</p>' +
      "</div>";
    document.body.appendChild(modal);
    var input = modal.querySelector("#search-input");
    var results = modal.querySelector("#search-results");
    var selected = 0;
    var lastFocus = null;

    function openSearch() {
      lastFocus = document.activeElement;
      modal.hidden = false;
      document.body.classList.add("scroll-lock");
      renderResults(input.value);
      input.focus();
      input.select();
    }
    function closeSearch() {
      modal.hidden = true;
      document.body.classList.remove("scroll-lock");
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }
    function isOpen() { return !modal.hidden; }

    function normalize(s) {
      return (s || "").toLowerCase().replace(/\s+/g, " ").trim();
    }

    function snippet(text, terms) {
      var lower = text.toLowerCase();
      var idx = -1;
      var hit = terms[0] || "";
      terms.forEach(function (t) {
        var j = lower.indexOf(t);
        if (j !== -1 && (idx === -1 || j < idx)) { idx = j; hit = t; }
      });
      if (idx < 0) return text.slice(0, 80);
      var start = Math.max(0, idx - 18);
      var end = Math.min(text.length, idx + hit.length + 48);
      return (start > 0 ? "…" : "") + text.slice(start, end).trim() + (end < text.length ? "…" : "");
    }

    function highlight(text, terms) {
      var frag = document.createDocumentFragment();
      var lower = text.toLowerCase();
      var i = 0;
      while (i < text.length) {
        var found = -1;
        var len = 0;
        terms.forEach(function (t) {
          var j = lower.indexOf(t, i);
          if (j !== -1 && (found === -1 || j < found)) { found = j; len = t.length; }
        });
        if (found === -1) {
          frag.appendChild(document.createTextNode(text.slice(i)));
          break;
        }
        if (found > i) frag.appendChild(document.createTextNode(text.slice(i, found)));
        var mark = document.createElement("mark");
        mark.textContent = text.slice(found, found + len);
        frag.appendChild(mark);
        i = found + len;
      }
      return frag;
    }

    function queryIndex(q) {
      var terms = normalize(q).split(" ").filter(Boolean);
      var index = window.DIRECTOR_SEARCH_INDEX || [];
      if (!terms.length) return [];
      var out = [];
      index.forEach(function (item) {
        var title = normalize(item.title);
        var section = normalize(item.section);
        var text = normalize(item.text);
        var hay = title + " " + section + " " + text;
        if (!terms.every(function (t) { return hay.indexOf(t) !== -1; })) return;
        var score = 0;
        terms.forEach(function (t) {
          if (title.indexOf(t) !== -1) score += 12;
          if (section.indexOf(t) !== -1) score += 4;
          if (text.indexOf(t) !== -1) score += 2;
        });
        out.push({ item: item, score: score, terms: terms });
      });
      out.sort(function (a, b) { return b.score - a.score || a.item.title.localeCompare(b.item.title, "zh"); });
      return out.slice(0, 12);
    }

    function renderResults(q) {
      results.textContent = "";
      selected = 0;
      var trimmed = (q || "").trim();
      if (!trimmed) {
        var hint = document.createElement("li");
        hint.className = "search-empty";
        hint.textContent = "输入关键词，搜索全部 " + ((window.DIRECTOR_SEARCH_INDEX || []).length || 34) + " 页";
        results.appendChild(hint);
        return;
      }
      if (!window.DIRECTOR_SEARCH_INDEX) {
        var missing = document.createElement("li");
        missing.className = "search-empty";
        missing.textContent = "搜索索引未加载";
        results.appendChild(missing);
        return;
      }
      var hits = queryIndex(trimmed);
      if (!hits.length) {
        var empty = document.createElement("li");
        empty.className = "search-empty";
        empty.textContent = "没有找到与「" + trimmed + "」相关的页面";
        results.appendChild(empty);
        return;
      }
      var prefix = assetPrefix();
      hits.forEach(function (hit, i) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = prefix + hit.item.path;
        a.setAttribute("data-index", String(i));
        var title = document.createElement("span");
        title.className = "search-hit-title";
        title.appendChild(highlight(hit.item.title, hit.terms));
        var meta = document.createElement("span");
        meta.className = "search-hit-meta";
        meta.textContent = hit.item.section || "";
        var snip = document.createElement("span");
        snip.className = "search-hit-snippet";
        snip.appendChild(highlight(snippet(hit.item.text, hit.terms), hit.terms));
        a.appendChild(title);
        a.appendChild(meta);
        a.appendChild(snip);
        li.appendChild(a);
        results.appendChild(li);
      });
      markSelected();
    }

    function resultLinks() {
      return Array.prototype.slice.call(results.querySelectorAll("a"));
    }
    function markSelected() {
      var links = resultLinks();
      links.forEach(function (a, i) { a.classList.toggle("is-active", i === selected); });
      var active = links[selected];
      if (!active) return;
      var top = active.offsetTop;
      var bottom = top + active.offsetHeight;
      if (top < results.scrollTop) results.scrollTop = top;
      else if (bottom > results.scrollTop + results.clientHeight) {
        results.scrollTop = bottom - results.clientHeight;
      }
    }

    trigger.addEventListener("click", openSearch);
    modal.addEventListener("click", function (e) {
      if (e.target && e.target.getAttribute("data-close")) closeSearch();
    });
    input.addEventListener("input", function () { renderResults(input.value); });
    input.addEventListener("keydown", function (e) {
      var links = resultLinks();
      if (e.key === "ArrowDown") {
        e.preventDefault();
        if (links.length) { selected = (selected + 1) % links.length; markSelected(); }
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        if (links.length) { selected = (selected - 1 + links.length) % links.length; markSelected(); }
      } else if (e.key === "Enter") {
        if (links[selected]) {
          e.preventDefault();
          window.location.href = links[selected].href;
        }
      } else if (e.key === "Escape") {
        e.preventDefault();
        e.stopPropagation();
        closeSearch();
      }
    });
    document.addEventListener("keydown", function (e) {
      var key = (e.key || "").toLowerCase();
      if ((e.metaKey || e.ctrlKey) && key === "k") {
        e.preventDefault();
        if (isOpen()) closeSearch();
        else openSearch();
      } else if (e.key === "Escape" && isOpen()) {
        closeSearch();
      }
    });
  }

  window.DirectorSite = window.DirectorSite || {};
  window.DirectorSite.getLearned = getLearned;
})();
