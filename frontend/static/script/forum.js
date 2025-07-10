// console.log("✅ forum.js loaded");

import { initNavbar } from './navbar.js'; 
import { switchLang } from './language.js';

document.addEventListener("DOMContentLoaded", async () => {
  await initNavbar();   // 等 navbar 初始化
  switchLang();         // 綁定語言選單
});