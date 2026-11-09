(function () {
  'use strict';
  var doc = document.documentElement;
  doc.classList.add('js');

  // ヘッダーの影・スマホ下部固定ボタン
  var header = document.querySelector('.site-header');
  var floatBar = document.querySelector('.float-bar');
  var floatFrom = document.querySelector('.home-hero') ? -1 : 400; // トップは最初から表示する
  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle('is-scrolled', y > 10);
    if (floatBar) floatBar.classList.toggle('is-show', y > floatFrom);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ハンバーガーメニュー
  var toggle = document.querySelector('.menu-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = document.body.classList.toggle('is-menu-open');
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'メニューを閉じる' : 'メニューを開く');
    });
    document.querySelectorAll('.drawer a').forEach(function (a) {
      a.addEventListener('click', function () {
        document.body.classList.remove('is-menu-open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // スクロールでふわっと表示
  var items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('is-in'); });
  }

  // お知らせ一覧のカテゴリ絞り込みとページ送り
  var filter = document.querySelector('.news-filter');
  if (filter) {
    var buttons = filter.querySelectorAll('button');
    var news = document.querySelectorAll('.news-item');
    var empty = document.querySelector('.news-empty');
    var pager = document.querySelector('.pager');
    var perPage = Number(pager.getAttribute('data-per-page'));

    // 戻る操作で同じページに戻れるよう、絞り込みとページ番号をURLに残す
    var query = new URLSearchParams(location.search);
    var cat = query.get('cat') || 'all';
    var page = parseInt(query.get('page'), 10) || 1;
    if (!filter.querySelector('button[data-cat="' + cat.replace(/[^a-z]/g, '') + '"]')) cat = 'all';

    var saveUrl = function () {
      var q = [];
      if (cat !== 'all') q.push('cat=' + cat);
      if (page > 1) q.push('page=' + page);
      // ダブルクリックで開いたプレビュー（file://）では書き換えられないことがある
      try { history.replaceState(null, '', location.pathname + (q.length ? '?' + q.join('&') : '')); } catch (e) {}
    };

    // 表示するページ番号（多いときは間を「…」で省略）
    var pageList = function (total) {
      var list = [];
      for (var i = 1; i <= total; i++) {
        if (i === 1 || i === total || Math.abs(i - page) <= 1) list.push(i);
        else if (list[list.length - 1] !== 0) list.push(0);
      }
      return list;
    };

    var pagerButton = function (label, text, to, disabled) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = text;
      b.setAttribute('aria-label', label);
      b.disabled = disabled;
      b.addEventListener('click', function () {
        page = to;
        render();
        saveUrl();
        filter.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
      return b;
    };

    var renderPager = function (total) {
      pager.innerHTML = '';
      pager.hidden = total < 2;
      if (total < 2) return;
      pager.appendChild(pagerButton('前のページ', '‹', page - 1, page === 1));
      pageList(total).forEach(function (n) {
        if (n === 0) {
          var gap = document.createElement('span');
          gap.className = 'pager__gap';
          gap.textContent = '…';
          gap.setAttribute('aria-hidden', 'true');
          pager.appendChild(gap);
          return;
        }
        var b = pagerButton(n + 'ページ目', String(n), n, false);
        if (n === page) b.setAttribute('aria-current', 'page');
        pager.appendChild(b);
      });
      pager.appendChild(pagerButton('次のページ', '›', page + 1, page === total));
    };

    var render = function () {
      var hits = Array.prototype.filter.call(news, function (n) {
        return cat === 'all' || n.getAttribute('data-cat') === cat;
      });
      // 先頭の大きな記事は1ページ目だけに出し、件数にはカードだけを数える
      var cards = hits.filter(function (n) { return !n.classList.contains('news-feature'); });
      var total = Math.max(1, Math.ceil(cards.length / perPage));
      page = Math.min(Math.max(page, 1), total);
      var start = (page - 1) * perPage;
      var visible = cards.slice(start, start + perPage);
      news.forEach(function (n) {
        n.hidden = n.classList.contains('news-feature') ? (hits.indexOf(n) < 0 || page > 1) : visible.indexOf(n) < 0;
      });
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-cat') === cat)); });
      if (empty) empty.hidden = hits.length > 0;
      renderPager(total);
    };

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        cat = btn.getAttribute('data-cat');
        page = 1;
        render();
        saveUrl();
      });
    });
    render();
  }

  // お問い合わせフォーム：二重送信防止・送信エラー時は入力内容を復元
  var form = document.querySelector('.contact-form');
  if (form) {
    var KEY = 'onestep-contact';
    var fields = form.querySelectorAll('input[name]:not([type=checkbox]):not([name=website]), select[name], textarea[name]');
    if (/[?&]error=1/.test(location.search)) {
      var msg = form.querySelector('.form-msg--error');
      if (msg) msg.hidden = false;
      try {
        var saved = JSON.parse(sessionStorage.getItem(KEY) || '{}');
        fields.forEach(function (f) { if (saved[f.name]) f.value = saved[f.name]; });
      } catch (err) { /* 保存領域が使えない環境では復元しない */ }
    }
    form.addEventListener('submit', function () {
      try {
        var data = {};
        fields.forEach(function (f) { data[f.name] = f.value; });
        sessionStorage.setItem(KEY, JSON.stringify(data));
      } catch (err) { /* noop */ }
      var b = form.querySelector('button[type=submit]');
      if (b) { b.disabled = true; b.style.opacity = '.6'; }
    });
  }
  if (location.pathname.indexOf('/contact/thanks') === 0) {
    try { sessionStorage.removeItem('onestep-contact'); } catch (err) { /* noop */ }
  }
})();
