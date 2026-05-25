// Minimal lang toggle. Each translatable element carries data-lang-en / data-lang-id / data-lang-cn.
// One per language is "active" at a time; .active = visible, others are hidden by CSS.
(function () {
  "use strict";

  var KEY = "ntra.lang";
  var SUPPORTED = ["en", "id", "cn"];

  function setLang(lang) {
    if (SUPPORTED.indexOf(lang) === -1) lang = "en";
    document.documentElement.setAttribute("lang", lang === "cn" ? "zh-CN" : lang);

    SUPPORTED.forEach(function (code) {
      var nodes = document.querySelectorAll("[data-lang-" + code + "]");
      nodes.forEach(function (n) {
        if (code === lang) n.classList.add("active");
        else n.classList.remove("active");
      });
    });

    var buttons = document.querySelectorAll(".lang-toggle button[data-set]");
    buttons.forEach(function (b) {
      if (b.getAttribute("data-set") === lang) b.classList.add("active");
      else b.classList.remove("active");
    });

    try {
      localStorage.setItem(KEY, lang);
    } catch (e) {
      // private mode etc — silent
    }
  }

  function init() {
    var saved = null;
    try {
      saved = localStorage.getItem(KEY);
    } catch (e) {
      saved = null;
    }
    setLang(saved || "en");

    var buttons = document.querySelectorAll(".lang-toggle button[data-set]");
    buttons.forEach(function (b) {
      b.addEventListener("click", function () {
        setLang(b.getAttribute("data-set"));
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
