// console.log("啟動navbar.js");

import { loadLang } from './language.js';

export async function initNavbar() {
  const { langContent } = await loadLang(); 
  // console.log("langContent:", langContent);
  renderNav(langContent);

  const selectLang = document.getElementById("langSwitcher");
  selectLang.style.visibility = "visible";

  // ✅ 只攔截同語系的導航點擊
  document.querySelectorAll(".menu__item--header--a").forEach(link => {
    link.addEventListener("click", (e) => {
      const href = link.getAttribute("href");

      // 如果網址裡包含當前語系，才阻止 reload
      if (href.includes(`/` + lang + `/`)) {
        e.preventDefault();
        history.pushState({}, "", href);

        // 簡單：直接用 location.pathname 判斷要顯示哪個頁面
        if (href.includes("search")) {
          import("./search.js").then(m => m.initSearch());
        } else if (href.includes("ranking")) {
          import("./ranking.js").then(m => m.initRanking());
        }
      }
      // 如果不是同語系，就讓瀏覽器正常刷新
    });
  });

  // 處理上一頁 / 下一頁
  window.addEventListener("popstate", () => {
    if (location.pathname.includes("search")) {
      import("./search.js").then(m => m.initSearch());
    } else if (location.pathname.includes("ranking")) {
      import("./ranking.js").then(m => m.initRanking());
    }
  });

  // 🔐 自動登入檢查並更新會員資料
  const token = localStorage.getItem("token");
  if (token) {
    try {
      const res = await fetch("/api/auth/profile", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      });
      const result = await res.json();
      if (res.ok) {
        const user = result.data;
        updateMemberInfo(user);  // 🔁 呼叫更新函式
      } else {
        // console.warn("token 無效，登出中");
        localStorage.removeItem("token");
      }
    } catch (err) {
      // console.error("取得會員資料失敗：", err);
      localStorage.removeItem("token");
    }
  }
}

const searchNav = document.getElementById("searchNav");
const rankingNav = document.getElementById("rankingNav");
const forumNav = document.getElementById("forumNav");
const loginNav = document.getElementById("loginNav");
const submitGoogle = document.getElementById('submitGoogle');
// const submitThreads = document.getElementById('submitThreads');
const submitEmail = document.getElementById('submitEmail');

const loginTitle = document.getElementById('loginTitle');
const loginEmail = document.getElementById('loginEmail');
const loginPassword = document.getElementById('loginPassword');
const loginSubmit = document.getElementById('loginSubmit');
const loginMessage = document.getElementById('loginMessage');
const goToRegister = document.getElementById('goToRegister');

const registerTitle = document.getElementById('registerTitle');
const registerName = document.getElementById('registerName');
const registerEmail = document.getElementById('registerEmail');
const registerPassword = document.getElementById('registerPassword');
const registerSubmit = document.getElementById('registerSubmit');
const changePicBtn = document.getElementById('changePicBtn');
const logoutBtn = document.getElementById('logoutBtn');

async function renderNav(data) {
  searchNav.textContent = data.search;
  rankingNav.textContent = data.ranking;
  forumNav.textContent = data.forum;
  loginNav.textContent = data.login;
  submitGoogle.textContent = data.login_list.google;
  // submitThreads.textContent = data.login_list.threads;
  submitEmail.textContent = data.login_list.email.label;

  loginTitle.textContent = data.login_list.email.label;
  loginEmail.placeholder = data.login_list.email.options[0].email;
  loginPassword.placeholder = data.login_list.email.options[0].password;
  loginSubmit.textContent = data.login_list.email.options[0].submit;
  loginMessage.textContent = data.login_list.email.options[0].message;
  goToRegister.textContent = data.login_list.email.options[0].goto;

  registerTitle.textContent = data.register_list.email.label;
  registerName.placeholder = data.register_list.email.options[0].name;
  registerEmail.placeholder = data.register_list.email.options[0].email;
  registerPassword.placeholder = data.register_list.email.options[0].password;
  registerSubmit.textContent = data.register_list.email.options[0].submit;

  if (changePicBtn) changePicBtn.textContent = data.member.photo;
  if (logoutBtn) logoutBtn.textContent = data.member.logout;
}

function updateMemberInfo(user) {
  const nameDiv = document.getElementById("memberName");
  const emailDiv = document.getElementById("memberEmail");
  const picImg = document.getElementById("memberPic");

  if (nameDiv) nameDiv.textContent = user.name;
  if (emailDiv) emailDiv.textContent = user.email;
  if (picImg && user.picture) picImg.src = user.picture;
}