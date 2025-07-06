console.log("✅ forum.js loaded");

import { initNavbar } from './navbar.js'; 
import { switchLang } from './language.js';

document.addEventListener("DOMContentLoaded", async () => {
  await initNavbar();   // 等 navbar 初始化
  switchLang();         // 綁定語言選單

  // 等畫面渲染完成後再 alert
  setTimeout(() => {
    alert("🔧 討論區實作進行中");
  }, 100); // 100ms 就夠讓畫面跑出來了
});