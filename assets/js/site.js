/* Glas za Bosnu — navigation, scroll helpers, reveal animations */
(function () {
  'use strict';

  var nav = document.querySelector('.nav');
  var menu = nav && nav.querySelector('.menu');
  var toggle = nav && nav.querySelector('.nav-toggle');
  var isMobile = function () { return window.matchMedia('(max-width: 1050px)').matches; };

  /* --- mobile menu ---------------------------------------------------- */
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* --- dropdowns: hover on desktop, tap on mobile --------------------- */
  var parents = nav ? nav.querySelectorAll('.has-sub') : [];

  Array.prototype.forEach.call(parents, function (li) {
    var link = li.querySelector('a');

    li.addEventListener('mouseenter', function () {
      if (!isMobile()) openItem(li);
    });
    li.addEventListener('mouseleave', function () {
      if (!isMobile()) closeItem(li);
    });

    link.addEventListener('click', function (e) {
      // On mobile, a parent with a real target still needs one tap to expand.
      if (isMobile()) {
        e.preventDefault();
        li.classList.contains('open') ? closeItem(li) : openItem(li);
      } else if (link.getAttribute('href') === '#') {
        e.preventDefault();
        li.classList.contains('open') ? closeItem(li) : openItem(li);
      }
    });

    // Keyboard: close the dropdown and return focus to its trigger.
    li.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && li.classList.contains('open')) {
        closeItem(li);
        link.focus();
      }
    });
    li.addEventListener('focusout', function (e) {
      if (!isMobile() && !li.contains(e.relatedTarget)) closeItem(li);
    });
  });

  function openItem(li) {
    if (!isMobile()) {
      Array.prototype.forEach.call(parents, function (o) { if (o !== li) closeItem(o); });
    }
    li.classList.add('open');
    li.querySelector('a').setAttribute('aria-expanded', 'true');
  }

  function closeItem(li) {
    li.classList.remove('open');
    li.querySelector('a').setAttribute('aria-expanded', 'false');
  }

  document.addEventListener('click', function (e) {
    if (nav && !nav.contains(e.target)) {
      Array.prototype.forEach.call(parents, closeItem);
      if (menu) menu.classList.remove('open');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
    }
  });

  /* --- back to top ---------------------------------------------------- */
  var totop = document.querySelector('.totop');
  if (totop) {
    totop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    window.addEventListener('scroll', function () {
      totop.classList.toggle('show', window.scrollY > 500);
    }, { passive: true });
  }

  /* --- reveal on scroll ----------------------------------------------- */
  var revealables = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && revealables.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    Array.prototype.forEach.call(revealables, function (el) { io.observe(el); });
  } else {
    Array.prototype.forEach.call(revealables, function (el) { el.classList.add('in'); });
  }
})();
