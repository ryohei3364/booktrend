// console.log("✅ auth.js loaded");

const loginNav = document.getElementById('loginNav');
const loginDialog = document.getElementById('loginDialog');
const submitGoogle = document.getElementById('submitGoogle');
const submitThreads = document.getElementById('submitThreads');
const submitEmail = document.getElementById('submitEmail');
const loginEmailDialog = document.getElementById('loginEmailDialog');
const loginForm = document.getElementById("loginForm");
const registerDialog = document.getElementById("registerDialog");
const registerForm = document.getElementById("registerForm");
const goToRegister = document.getElementById("goToRegister");
const userIcon = document.querySelector(".menu__item--member--user");
const userPic = document.getElementById("userPic");


// 1️⃣ Google OAuth callback: 儲存 token 並 reload
const urlParams = new URLSearchParams(window.location.search);
const tokenFromUrl = urlParams.get("token");
if (tokenFromUrl) {
  localStorage.setItem("token", tokenFromUrl);
  window.history.replaceState({}, "", "/"); // ✅ 清除網址參數
  window.location.reload(); // ✅ reload 觸發登入檢查
}

// 2️⃣ 自動登入檢查
window.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("token");  // 🔁 從這裡才開始正式讀取
  // console.log('token:', token);

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
        // ✅ 登入成功：隱藏登入按鈕，顯示使用者頭像
        const user = result.data;
        // console.log('user:', user);
        showUser(user);
        // updateMemberPage(user);
      } else {
        // ❌ token 無效：清除 localStorage
        localStorage.removeItem("token");
        showLoginButton();
      }
    } catch (err) {
      console.error("自動登入失敗", err);
      localStorage.removeItem("token");
      showLoginButton();
    }
  } else {
    // 尚未登入
    showLoginButton();
  }
});

// 3️⃣ 顯示用戶登入頭像
function showUser(user) {
  userIcon.style.display = "inline-block";
  if (user.picture) {
    userPic.src = user.picture;
  }
  // 隱藏登入按鈕
  loginNav.style.display = "none";
}
// 顯示登入按鈕
function showLoginButton() {
  userIcon.style.display = "none";
  loginNav.style.display = "inline-block";
}

// 5. 點擊導覽列登入按鈕 → 開啟選擇方式 dialog
loginNav.addEventListener("click", () => {
  loginDialog.showModal();
  // loginEmailDialog.showModal();
});

// 6. 點擊 Google 登入
submitGoogle.addEventListener("click", () => {
  fetch("/api/auth/google")
    .then((res) => res.json())
    .then((data) => {
      window.location.href = data.url;
    });
});

// 7. 點擊 Email 登入 → 開啟 loginEmailDialog
submitEmail.addEventListener("click", () => {
  loginDialog.close();
  loginEmailDialog.showModal();
});

// 8. 點擊「還沒有帳號？」 → 跳到註冊表單
if (goToRegister) {
  goToRegister.addEventListener("click", (e) => {
    e.preventDefault();
    loginDialog.showModal();
    // loginEmailDialog.close();
    registerDialog.showModal();
  });
}

// 9. Email 登入表單 submit
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;

  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const result = await res.json();

  if (res.ok) {
    localStorage.setItem("token", result.token);
    window.location.href = "/";
  } else if (res.status === 404) {
    // ✅ Email 沒註冊 → 自動跳轉註冊頁
    loginDialog.showModal();
    // loginEmailDialog.close();
    registerDialog.showModal();
    document.getElementById("registerEmail").value = email;
  } else {
    alert(result.error || "登入失敗");
  }
});

// 10. 註冊表單 submit
registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = document.getElementById("registerName").value;
  const email = document.getElementById("registerEmail").value;
  const password = document.getElementById("registerPassword").value;

  const res = await fetch("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
  const result = await res.json();
  // console.log('result', result);

  if (res.ok) {
    localStorage.setItem("token", result.token);
    registerDialog.close();
    showUser(result.user);
    window.location.href = "/";
  } else {
    alert(result.error || "註冊失敗");
  }
});


// 11. dialog 點擊彈窗外部自動關閉
function clickToClose(dialog) {
  dialog.addEventListener('click', (event) => {
    const rect = dialog.getBoundingClientRect();
    const isInDialog =
      rect.top <= event.clientY && event.clientY <= rect.bottom &&
      rect.left <= event.clientX && event.clientX <= rect.right;

    if (!isInDialog) {
      dialog.close();  // 用 close() 關閉彈窗
    }
  });
}
// 對 loginDialog 和 registerDialog 都套用
clickToClose(loginDialog);
clickToClose(loginEmailDialog);
clickToClose(registerDialog);
