async function fetchRankingData(bookstoreId, chartType) {
  const response = await fetch(`/api/ranking?bookstore_id=${bookstoreId}&chart_type=${chartType}`);
  return response.json();
}

async function renderRanking(bookstoreId, chartType) {
  const rankingBooks = await fetchRankingData(bookstoreId, chartType);
  const fragment = document.createDocumentFragment(); // 👈 用 fragment 暫存所有卡片

  rankingBooks.forEach(item => {
    const bookBlock = document.createElement("div");
    bookBlock.className = "book-block";

    const title = document.createElement("h3");
    title.textContent = item.title;

    const author = document.createElement("p");
    author.textContent = item.author;

    const image = document.createElement("img");
    image.src = item.image_url_s;
    image.alt = item.title;

    bookBlock.appendChild(image);
    bookBlock.appendChild(title);
    bookBlock.appendChild(author);

    fragment.appendChild(bookBlock);
  });
	return fragment; // ✅ 回傳 fragment
}

// 設定排行榜容器與條件
const container = document.querySelector(".ranking__container--card");
const bookstoreIdList = [1, 2];
const chartTypeList = ['yearly', 'daily'];

(async () => {
  for (const bookstoreId of bookstoreIdList) {
    for (const chartType of chartTypeList) {
      const fragment = await renderRanking(bookstoreId, chartType);
      container.appendChild(fragment); // ✅ 插入 DOM
    }
  }
})();