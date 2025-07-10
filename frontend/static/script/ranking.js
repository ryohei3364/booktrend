// console.log("✅ ranking.js loaded");

import { initNavbar } from './navbar.js';
await initNavbar(); 

import { switchLang } from './language.js';
switchLang();  // 綁定語言選單

const container = document.querySelector(".ranking__container--card");
const bookstoreIdList = [1, 2];
const chartTypeList = ['yearly', 'daily'];

async function fetchRankingList() {
  const response = await fetch('/api/ranking/list');
  if (!response.ok) {
    throw new Error('Failed to fetch ranking list');
  }
  return await response.json();
}

async function fetchRankingData(bookstoreId, chartType) {
  const response = await fetch(`/api/ranking?bookstore_id=${bookstoreId}&chart_type=${chartType}`);
  if (!response.ok) {
    throw new Error('Failed to fetch ranking data');
  }
  return await response.json();
}

async function renderRanking(bookstoreId, chartType, rankingList) {
  const rankingBooks = await fetchRankingData(bookstoreId, chartType);

  const key = (bookstoreId === 1 ? "first" : "second") + "_bookstore_" + chartType;
  const titleText = rankingList[key] || chartType;

  const fragment = document.createDocumentFragment();

  const section = document.createElement("section");
  section.className = "ranking-section";

  const sectionTitle = document.createElement("h1");
  sectionTitle.textContent = titleText;
  sectionTitle.className = "ranking-title";

  const bookList = document.createElement("div");
  bookList.className = "book-list";

  rankingBooks.forEach((item, index) => {
    const bookBlock = document.createElement("div");
    bookBlock.className = "book-block";
    bookBlock.style.position = "relative";  // 讓徽章定位相對於書卡

    const link = document.createElement("a");
    link.href = item.book_url;
    link.target = "_blank"; // 開新分頁
    link.rel = "noopener noreferrer"; // 安全性
  
    const rankBadge = document.createElement("div");
    rankBadge.className = "book-rank-badge";
    rankBadge.textContent = index + 1;  // 排名數字

    const image = document.createElement("img");
    image.src = item.image_url;
    image.alt = item.title;

    link.appendChild(image);       // 把圖片放進連結裡
    bookBlock.appendChild(link);   // 把連結放進書卡裡

    const title = document.createElement("h2");
    title.textContent = item.title;

    const author = document.createElement("p");
    author.textContent = item.author;

    bookBlock.appendChild(rankBadge);
    bookBlock.appendChild(title);
    bookBlock.appendChild(author);
  
    bookList.appendChild(bookBlock);
  });

  section.appendChild(sectionTitle);
  section.appendChild(bookList);
  fragment.appendChild(section);

  return fragment;
}

(async () => {
  try {
    const rankingList = await fetchRankingList(); // 只呼叫一次
    // console.log("✅ rankingList:", rankingList);

    for (const bookstoreId of bookstoreIdList) {
      for (const chartType of chartTypeList) {
        const fragment = await renderRanking(bookstoreId, chartType, rankingList);
        container.appendChild(fragment);
      }
    }
  } catch (error) {
    // console.error("Error loading rankings:", error);
  }
})();