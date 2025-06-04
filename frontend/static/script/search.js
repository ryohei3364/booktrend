// const lang = navigator.language.slice(0, 2);
const lang = "zh"; // 👉 你可以在這裡強制指定測試語系
// const supportedLangs = ["en", "fr", "de", "it", "zh"];
// const selectedLang = supportedLangs.includes(lang) ? lang : "zh";

renderSearch(lang);

document.getElementById("searchInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    const keyword = e.target.value.trim();
    if (keyword) {
      searchBooks(keyword);
    }
  }
});

function renderSearch(lang) {
  fetch(`/api/search/${lang}`)
    .then((res) => res.json())
    .then((i18n) => {
      // ✅ 這裡可以安全使用 i18n
      // console.log("全部資料：", lang);
      // console.log("載入的 i18n 內容：", i18n);

      // ✅ 設定到 DOM
      document.getElementById("title").textContent = i18n.search_title;
      document.getElementById("searchInput").placeholder =
        i18n.search_placeholder;
      // 自動設定 topic1 ~ topic6
      for (let i = 1; i <= 6; i++) {
        const el = document.getElementById(`topic${i}`);
        if (el && i18n[`topic${i}`]) {
          el.textContent = i18n[`topic${i}`];
        }
      }
    })
    .catch((err) => {
      console.error("載入語系 JSON 發生錯誤：", err);
    });
}

function searchBooks(keyword) {
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



// let debounceTimer = null;

// document.getElementById("searchInput").addEventListener("input", function () {
//   clearTimeout(debounceTimer); // 每次輸入都會「重新計時」，防止短時間內發送過多 API 請求

//   const keyword = this.value.trim();
//   if (!keyword) return;

//   debounceTimer = setTimeout(() => {
//     fetch(`/api/search?keyword=${encodeURIComponent(keyword)}`)
//       .then((res) => res.json())
//       .then((data) => {
//         const resultsDiv = document.getElementById("searchResults");
//         resultsDiv.innerHTML = "";

//         const fragment = document.createDocumentFragment();

//         data.forEach((book) => {
//           const bookDiv = document.createElement("div");

//           const titleEl = document.createElement("h3");
//           titleEl.appendChild(highlightKeyword(book.title, keyword));

//           const descEl = document.createElement("p");
//           descEl.appendChild(highlightKeyword(book.description, keyword));

//           bookDiv.appendChild(titleEl);
//           bookDiv.appendChild(descEl);
//           bookDiv.appendChild(document.createElement("hr"));

//           fragment.appendChild(bookDiv);
//         });
//         resultsDiv.appendChild(bookDiv);
//       })
//       .catch((err) => {
//         console.error("搜尋失敗", err);
//       });
//   }, 300);
// });
