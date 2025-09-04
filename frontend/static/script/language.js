// 多國語系切換
export async function loadLang() {
  const cookieLang = await getUserCookie();
  // 如果 cookie 中有設定語言偏好，就使用它；否則使用瀏覽器提供的語言清單
  const userLang = cookieLang || navigator.languages[0];
  // const userLang = cookieLang ? cookieLang : navigator.languages.join(',');
  const cacheKey = `lang-${userLang}`;

  // 先檢查 localStorage 有沒有快取
  const cached = localStorage.getItem(cacheKey);
  if (cached) {
    try {
      const parsed = JSON.parse(cached);
      return parsed; // { langContent, countryList }
    } catch (err) {
      console.warn("語言快取解析失敗，清除後重新載入");
      localStorage.removeItem(cacheKey);
    }
  }

  try {
    const response = await fetch('/api/language/', {
      headers: {
        "Accept-Language": userLang
      }
    });
    const result = await response.json();
    console.log("語言 API 回傳資料:", result);
    // 第一個元素是語言對應表
    const langContent = result.content[0]; // nav + card_title
    const countryList = result.content.slice(1); // 其餘為國家資訊
    // 存進 localStorage
    localStorage.setItem(cacheKey, JSON.stringify({ langContent, countryList }));

    return { langContent, countryList };
  } catch (error) {
    // console.error("載入語言檔失敗:", error);
    return null;
  }
}

export function switchLang() {
  const langSelect = document.getElementById("language-select");
  if (langSelect) {
    langSelect.addEventListener("change", (e) => {
      const selectedLang = e.target.value;
      const currentLang = getLangFromCookie();

      if (selectedLang !== currentLang) {
        setLangPrefer(selectedLang); // 更新 cookie
        localStorage.clear();       // ✅ 清空舊快取，避免混用
        location.reload();          // ✅ 只在語言變更時刷新
      }
    });

    // 取得目前 cookie 裡的語言
    const currentLang = getLangFromCookie();
    if (currentLang) {
      // 對應 zh-TW 這種情況，只取 zh 部分
      // const normalizedLang = currentLang.split('-')[0];
      const options = Array.from(langSelect.options).map(opt => opt.value);
      if (options.includes(currentLang)) {
        langSelect.value = currentLang;  // ✅ 選中對應語言
      } else {
        langSelect.value = 'en-US';  // fallback 預設
      }
    }
    // ✅ 保證語言選單顯示
    document.getElementById("langSwitcher").style.visibility = "visible";
  }
};


export async function getUserCookie() {
  const langcode = getCookie("booktrend-lang");
  if (langcode) {
    // console.log("使用者語言偏好為：", langcode);
    return langcode;
  } else {
    // console.log("未設定語言偏好，讀取使用者的語言偏好，並設置成cookies");
    const langcode = navigator.languages[0];  // 只取第一個語言
    setLangPrefer(langcode);
    return langcode;
  }
}

// 設定語言偏好（儲存在 cookie 中，有效期一年）
export function setLangPrefer(langcode) {
  const langToStore = Array.isArray(langcode) ? langcode[0] : langcode || '';
  document.cookie = `booktrend-lang=${langToStore}; path=/; max-age=31536000`;
}

// 讀取特定 cookie 值
export function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

// 讀取 cookie 語言函式
export function getLangFromCookie() {
  const match = document.cookie.match(/(^|;) ?booktrend-lang=([^;]*)/);
  return match ? match[2] : null;
}