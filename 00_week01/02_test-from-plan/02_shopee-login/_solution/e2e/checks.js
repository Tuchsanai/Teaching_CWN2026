// Page checks used in the real run (2026-11-02). Each function is passed to the Playwright MCP
// (browser_evaluate) on the matching page; they only read the page and never click.

// TC-AUTH-01 · home page: logged in = no login/sign-up link at top right
() => {
  const nav = document.querySelector('header nav, nav');
  const text = nav ? nav.innerText : document.body.innerText;
  const cart = document.querySelector('a[href*="/cart"]');
  return {
    loginButtonVisible: /เข้าสู่ระบบ|สมัครใหม่/.test(text),
    cartBadge: cart ? cart.innerText.trim() : null,   // the account name is deliberately not returned
  };
}

// TC-SRCH-01 · search results (scroll down slowly first so all cards load)
() => {
  const items = [...document.querySelectorAll('li.shopee-search-item-result__item')];
  const titles = items.map((li) => {
    const t = li.querySelector('[class*="line-clamp-2"]');
    const img = li.querySelector('img[alt]');
    return ((t && t.textContent) || (img && img.alt) || '').trim();
  });
  const top = titles.slice(0, 20);
  const hits = top.filter((t) => /แมว|cat/i.test(t)).length;
  return { count: items.length, hits, ratio: hits / top.length, pass: items.length >= 20 && hits / top.length >= 0.8 };
}

// TC-CART-01 · cart page: is the toy there, and how many rows in total
() => ({
  toyInCart: [...document.querySelectorAll('a')].some((a) => a.textContent.includes('ซ่อนหาอัตโนมัติ')),
  selectAll: (document.body.innerText.match(/เลือกทั้งหมด \((\d+)\)/) || [])[1],
})
