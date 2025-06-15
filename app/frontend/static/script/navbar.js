// console.log("啟動navbar.js");

import { loadLang } from './language.js';

export async function initNavbar() {
  const { langContent } = await loadLang();
  renderNav(langContent);

  const selectLang = document.getElementById("langSwitcher");

  // 如果目前不是 zh，就隱藏 zh 選項
  if (selectLang.value !== 'zh') {
    const zhOption = selectLang.querySelector('option[value="zh"]');
    if (zhOption) {
      zhOption.hidden = true;  // ✅ 將 zh 隱藏
    }
  }
}

const searchNav = document.getElementById("searchNav");
const rankingNav = document.getElementById("rankingNav");

async function renderNav(data) {
  searchNav.textContent = data.search;
  rankingNav.textContent = data.ranking;
}