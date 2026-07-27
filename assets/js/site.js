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

  /* --- gallery lightbox ------------------------------------------------ */
  var gallery = document.querySelector('.gallery');
  var lightbox = document.querySelector('.lightbox');

  if (gallery && lightbox) {
    var shots = Array.prototype.slice.call(gallery.querySelectorAll('button'));
    var frame = lightbox.querySelector('img');
    var count = lightbox.querySelector('.lightbox-count');
    var index = 0;
    var opener = null;

    var show = function (i) {
      index = (i + shots.length) % shots.length;
      var thumb = shots[index].querySelector('img');
      frame.src = shots[index].getAttribute('data-full') || thumb.src;
      frame.alt = thumb.alt;
      if (count) count.textContent = (index + 1) + ' / ' + shots.length;
    };

    shots.forEach(function (btn, i) {
      btn.addEventListener('click', function () {
        opener = btn;
        show(i);
        lightbox.classList.add('open');
        document.body.style.overflow = 'hidden';
        lightbox.querySelector('.lightbox-close').focus();
      });
    });

    var close = function () {
      lightbox.classList.remove('open');
      document.body.style.overflow = '';
      if (opener) opener.focus();
    };

    lightbox.querySelector('.lightbox-close').addEventListener('click', close);
    lightbox.querySelector('.lightbox-prev').addEventListener('click', function () { show(index - 1); });
    lightbox.querySelector('.lightbox-next').addEventListener('click', function () { show(index + 1); });
    lightbox.addEventListener('click', function (e) { if (e.target === lightbox) close(); });

    document.addEventListener('keydown', function (e) {
      if (!lightbox.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(index - 1);
      if (e.key === 'ArrowRight') show(index + 1);
    });
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
    // threshold must stay 0: an article taller than the viewport can never
    // reach a percentage threshold, and would stay invisible forever.
    }, { rootMargin: '0px 0px -40px 0px', threshold: 0 });
    Array.prototype.forEach.call(revealables, function (el) { io.observe(el); });
  } else {
    Array.prototype.forEach.call(revealables, function (el) { el.classList.add('in'); });
  }
})();
