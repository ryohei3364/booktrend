// console.log("✅ search.js loaded");

import { initNavbar } from './navbar.js';
await initNavbar();  // 等待 navbar 完成後再繼續執行

import { switchLang, loadLang } from './language.js';
switchLang();  // 綁定語言選單

async function initPage() {
  // await getUserCookie();
  const { langContent } = await loadLang();
}
initPage();

let cachedLang = null;
renderSearch();

document.getElementById("searchInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    const keyword = e.target.value.trim();
    if (keyword) {
      searchBooks(keyword);
    }
  }
});

function renderSearch() {
  if (cachedLang) {
    updateDOMWithLang(cachedLang);
    return;
  }

  fetch('/api/language')
    .then((res) => res.json())
    .then((i18n) => {
      console.log(i18n.content[0].search_list);
      const langData = i18n.content[0].search_list[0];  // ✅ 只取需要的部分
      console.log("載入的語系內容：", langData);
      cachedLang = langData;
      updateDOMWithLang(langData);
    })
    .catch((err) => {
      console.error("載入語系 JSON 發生錯誤：", err);
    });
}

async function fetchHotSearches() {
  const response = await fetch('/api/search/hot');
  return response.json();
}

function updateDOMWithLang(data) {
  document.getElementById("title").textContent = data.search_title;
  document.getElementById("searchInput").placeholder = data.search_placeholder;

  // ✅ 另外呼叫 fetchHotSearches 來填熱門關鍵字
  fetchHotSearches()
    .then((hotKeywords) => {
      console.log("🔥 熱門搜尋關鍵字：", hotKeywords);

      for (let i = 1; i <= 6; i++) {
        const el = document.getElementById(`topic${i}`);
        const keyword = hotKeywords[i - 1]['keyword'];
        if (el && keyword) {
          el.textContent = keyword;
          el.style.cursor = "pointer"; // 滑鼠提示可點擊
          el.onclick = () => triggerSearch(keyword);
        }
      }
    })
    .catch((err) => {
      console.error("載入熱門搜尋失敗：", err);
    });
}

function triggerSearch(keyword) {
  const input = document.getElementById("searchInput");
  input.value = keyword; // 填入搜尋框
  // document.getElementById("searchButton").click(); // 模擬點擊搜尋按鈕
  searchBooks(keyword);  // <== 呼叫搜尋函數，觸發搜尋
}

function searchBooks(keyword) {
  console.log("搜尋關鍵字：", keyword);
  fetch(`/api/search?keyword=${encodeURIComponent(keyword)}`)
    .then((res) => res.json())
    .then((results) => {
      const resultsDiv = document.getElementById("searchResults");
      const searchListDiv = document.getElementById("searchList");
      resultsDiv.innerHTML = ""; // 清空舊結果
      searchListDiv.innerHTML = ""; // 清空舊結果

      if (!results.length) {
        resultsDiv.textContent = "找不到任何結果。";
        return;
      }

      results.forEach((book) => {
        const bookDiv = document.createElement("div");
        bookDiv.className = "book-item";

        const img = document.createElement("img");
        img.src = book.image_url;
        img.alt = book.title;
        img.className = "book-image";

        const titleEl = document.createElement("a");
        titleEl.href = book.book_url;
        titleEl.target = "_blank";
        titleEl.className = "book-title";
        titleEl.appendChild(highlightKeyword(book.title, keyword));  // 高亮

        const infoEl = document.createElement("p");
        infoEl.className = "book-info";
        infoEl.textContent = `${book.publisher}・${book.published_date}`;

        const descEl = document.createElement("p");
        descEl.className = "book-desc";
        const shortDesc = book.description.slice(0, 100) + "...";
        descEl.appendChild(highlightKeyword(shortDesc, keyword));  // 高亮

        bookDiv.appendChild(img);
        bookDiv.appendChild(titleEl);
        bookDiv.appendChild(infoEl);
        bookDiv.appendChild(descEl);

        resultsDiv.appendChild(bookDiv);
      });
    })
    .catch((err) => {
      console.error("搜尋失敗：", err);
      document.getElementById("searchResults").textContent =
        "搜尋失敗，請稍後再試。";
    });
}

// ✅ 安全 escape regex 關鍵字
function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function highlightKeyword(text, keyword) {
  const safeKeyword = escapeRegExp(keyword);
  const regex = new RegExp(safeKeyword, 'gi');
  const fragment = document.createDocumentFragment();

  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    // 加入前段文字
    if (match.index > lastIndex) {
      fragment.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
    }

    // 加入 <mark> 包住的關鍵字
    const mark = document.createElement("mark");
    mark.textContent = match[0];
    fragment.appendChild(mark);

    lastIndex = regex.lastIndex;
  }

  // 加入剩餘文字
  if (lastIndex < text.length) {
    fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
  }

  return fragment;
}
