// console.log("✅ member.js loaded");

import { initNavbar } from './navbar.js';
await initNavbar(); 

import { switchLang } from './language.js';
switchLang();  // 綁定語言選單

document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "/";  // 未登入者導回首頁
    return;
  }

  try {
    const res = await fetch("/api/auth/profile", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    const result = await res.json();
    // console.log("👤 會員資料：", result);

    if (res.ok) {
      const user = result.data;
      updateMemberPage(user);
    } else {
      localStorage.removeItem("token");
      window.location.href = "/";
    }
  } catch (err) {
    // console.error("⚠️ 無法取得會員資料", err);
    localStorage.removeItem("token");
    window.location.href = "/";
  }
});

document.getElementById("logoutBtn").addEventListener("click", () => {
  localStorage.removeItem("token");
  window.location.href = "/";
});

document.getElementById("changePicBtn").addEventListener("click", () => {
  alert("🔧 更換頭像功能尚未實作");
  // 將來可導向 /change-avatar 或開啟對話框
});

function updateMemberPage(user) {
  const nameElement = document.getElementById("memberName");
  const emailElement = document.getElementById("memberEmail");
  const picElement = document.getElementById("memberPic");

  if (nameElement) nameElement.textContent = user.name;
  if (emailElement) emailElement.textContent = user.email;
  if (picElement && user.picture) picElement.src = user.picture;
}


