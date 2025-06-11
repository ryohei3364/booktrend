import { initNavbar } from './navbar.js';
await initNavbar();  // 等待 navbar 完成後再繼續執行

import { loadLang, switchLang } from './language.js';
switchLang();  // 綁定語言選單

async function initPage() {
  // await getUserCookie();
  const { countryList } = await loadLang();
  // renderNav(langContent);
  renderCard(countryList);
}

let sectionRenderQueue = [];
const cardContainer = document.querySelector(".main__card--container");

async function renderCard(data) {
  const filteredList = data.filter(data => data.id !== 3);

  const fragment = document.createDocumentFragment();
  filteredList.forEach(country => {
    const card = createCountryCard(country);
    fragment.appendChild(card);
  });
  cardContainer.appendChild(fragment);

  // ⬇️ 根據 section 類型批次渲染內容
  const renderOrder = ["category", "samebook", "author", "yearly", "daily", "wordcloud"];
  for (const sectionType of renderOrder) {
    const sectionsToRender = sectionRenderQueue.filter(s => s.className === sectionType);
    for (const { bookstoreId, contentContainer } of sectionsToRender) {
      switch (sectionType) {
        case "category":
          const canvas1 = document.createElement("canvas");
          canvas1.width = 300;
          canvas1.height = 450;
          contentContainer.appendChild(canvas1);
          await createCategory(bookstoreId, canvas1);
          break;
        case "samebook":
          await createSameBooks(bookstoreId, contentContainer);
          break;
        case "author":
          const canvas2 = document.createElement("canvas");
          contentContainer.appendChild(canvas2);
          await createAuthor(bookstoreId, canvas2);
          break;
        case "yearly":
          await createRanking(bookstoreId, contentContainer, fetchYearlyData);
          // await createYearly(bookstoreId, contentContainer);
          break;
        case "daily":
          await createRanking(bookstoreId, contentContainer, fetchDailyData);
          // await createDaily(bookstoreId, contentContainer);
          break;
        case "wordcloud":
          await createWordCloud(bookstoreId, contentContainer);
          break;
      }
    }
  }
}


function createCountryCard(data) {
  const card = document.createElement("div");
  card.className = "main__card";
  card.dataset.country = data.code;

	const title = document.createElement("div");
  title.className = "main__card--title";

	const span = document.createElement('span');
  span.className = "main__card--country";
	span.textContent = data.country;

	const logo = document.createElement('img');
	logo.className = 'logo';
	logo.src = data.logo;

	const map = document.createElement('img');
	map.className = 'map';
	map.src = data.map;

	title.appendChild(logo);
	title.appendChild(map);
  card.appendChild(span);
	card.appendChild(title);

  // 為每個 section 建立容器但不渲染內容
  data.sections.forEach(section => {
    const sectionDiv = document.createElement("div");
    sectionDiv.className = `main__card--section ${section.class}`;

    // 上方標題 + icon
    const header = document.createElement("div");
    header.className = "section-header";

    const icon = createSvgIcon("more");
    const titleSpan = document.createElement("span");
    titleSpan.textContent = section.title;

    header.appendChild(icon);
    header.appendChild(titleSpan);

    // 下方內容區塊（關鍵字雲）
    const content = document.createElement("div");
    content.className = "section-content";

    // 👉 推入待渲染佇列
    sectionRenderQueue.push({
      className: section.class,
      bookstoreId: data.bookstore_id,
      contentContainer: content
    });
    // 加入區塊到主卡片
    sectionDiv.appendChild(header);
    sectionDiv.appendChild(content);
    // 對 sectionDiv + header + content 套用 toggle 功能
    setupToggle(sectionDiv, header, content);
    card.appendChild(sectionDiv);
  });
  return card;
}

// async function sendUserLanguage() {
//   const userLanguages = navigator.languages.join(',');
//   const response = await fetch('/api/language', {
//     headers: {
//       "Accept-Language": userLanguages
//     }
//   });
//   const data = await response.json();
//   console.log("後端收到的語言偏好:", data);
// }

// async function fetchCardData() {
//   const response = await fetch("/api/language");
//   return response.json();
// }

async function fetchCategoryData(bookstoreId) {
  const response = await fetch(`/api/card/category/${bookstoreId}`);
  return response.json();
}

async function fetchSameBooksData(bookstoreId) {
  const response = await fetch(`/api/card/samebook/${bookstoreId}`);
  return response.json();
}

async function fetchAuthorData(bookstoreId) {
  const response = await fetch(`/api/card/author/${bookstoreId}`);
  return response.json();
}

async function fetchYearlyData(bookstoreId) {
  const response = await fetch(`/api/card/yearly/${bookstoreId}`);
  return response.json();
}

async function fetchDailyData(bookstoreId) {
  const response = await fetch(`/api/card/daily/${bookstoreId}`);
  return response.json();
}

async function fetchWordCloudData(bookstoreId) {
  const response = await fetch(`/api/card/wordcloud/${bookstoreId}`);
  return response.json();
}

async function createCategory(bookstoreId, canvas) {
  const chartData = await fetchCategoryData(bookstoreId);
  createChart(canvas, chartData);
}

async function createSameBooks(bookstoreId, container) {
  const sameBooks = await fetchSameBooksData(bookstoreId);

  sameBooks.forEach(book => {
    const bookCard = document.createElement("div");
    bookCard.className = "book-card";

    const author = document.createElement("h4");
    author.textContent = book.name;

    const img = document.createElement("img");
    img.src = book.image_url;
    img.alt = book.title;

    const title = document.createElement("p");
    title.textContent = book.title;

    // 加入所有元素
    bookCard.appendChild(author);
    bookCard.appendChild(img);
    bookCard.appendChild(title);

    container.appendChild(bookCard);
  });
}


async function createAuthor(bookstoreId, canvas) {
  const authors = await fetchAuthorData(bookstoreId);

  const labels = authors.map(a => a.author_name);
  const data = authors.map(a => a.times);

  const chartData = {
    labels: labels,
    datasets: [{
      label: '暢銷書本數',
      data: data,
      backgroundColor: ['#f94144', '#f3722c', '#f8961e'],
      borderWidth: 1
    }]
  };
  createChart(canvas, chartData, "bar");
}

async function createRanking(bookstoreId, container, fetchFn) {
  const books = await fetchFn(bookstoreId);
  books.forEach(book => {
    const bookCard = document.createElement("div");
    bookCard.className = "book-card";

    const rank = document.createElement("div");
    rank.className = "book-rank";
    rank.textContent = `No. ${book.ranking}`;

    const author = document.createElement("h4");
    author.textContent = book.author_name;

    const img = document.createElement("img");
    img.src = book.image_url;
    img.alt = book.title;

    const title = document.createElement("p");
    title.textContent = book.title;

    bookCard.appendChild(rank);
    bookCard.appendChild(author);
    bookCard.appendChild(img);
    bookCard.appendChild(title);
    container.appendChild(bookCard);
  });
}

async function createWordCloud(bookstoreId, container) {
  const cloudData = await fetchWordCloudData(bookstoreId);

  // 1️⃣ 先依照頻率排序（高到低）
  cloudData.sort((a, b) => b.size - a.size);

  // 2️⃣ 計算最大與最小頻率，建立字體縮放比例尺
  const maxFreq = cloudData[0].size;
  const minFreq = cloudData[cloudData.length - 1].size;

  const fontSizeScale = d3.scaleLinear()
    .domain([minFreq, maxFreq])
    .range([36, 80]); // 最小字體到最大字體大小，可自行調整
  
  const width = 500;
  const height = 350;
  const colorScale = d3.scaleOrdinal(d3.schemeCategory10);

  d3.layout.cloud()
    .size([width, height])
    .words(cloudData.map(d => ({
      text: d.text,
      size: fontSizeScale(d.size),
    })))
    .padding(5)
    // .rotate(() => (Math.random() > 0.5 ? 0 : 90)) 
    .rotate(d => {
      // 👉 大字不旋轉，小字才隨機旋轉
      if (d.size > 40) return 0;
      return Math.random() > 0.5 ? 90 : -90;
    })
    .font("Impact")
    .fontSize(d => {
      const isChinese = /[\u4e00-\u9fff]/.test(d.text);
      return isChinese ? d.size * 1 : d.size;
    })
    .on("end", (words) => {
      d3.select(container)
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width / 2},${height / 2})`)
        .selectAll("text")
        .data(words)
        .enter()
        .append("text")
        .style("font-family", "Impact")
        .style("font-size", d => `${d.size}px`)
        .style("fill", (d, i) => colorScale(i))
        .attr("text-anchor", "middle")
        .attr("transform", d => `translate(${d.x},${d.y}) rotate(${d.rotate})`)
        .text(d => d.text);
    })
    .start();
}

function createSvgIcon(type) {
	const svgNS = "http://www.w3.org/2000/svg";
	const svgMap = document.createElementNS(svgNS, "svg");
	svgMap.classList.add("icon");
	svgMap.setAttribute("xmlns", svgNS);
	svgMap.setAttribute("fill", "none");
	svgMap.setAttribute("viewBox", "0 0 24 24");
	svgMap.setAttribute("width", "36");
	svgMap.setAttribute("height", "36");
	svgMap.setAttribute("stroke-width", "1.5");
	svgMap.style.stroke = "var(--mintgreen-color)";
	svgMap.style.backgroundColor = "transparent";
	svgMap.style.flexShrink = "0"; // 防止縮小

	const path = document.createElementNS(svgNS, "path");
	path.setAttribute("stroke-linecap", "round");
	path.setAttribute("stroke-linejoin", "round");
	path.setAttribute("fill", "none");

	if (type === "more") {
		path.setAttribute("d", "M12 9v6m3-3H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z");
	} else {
		path.setAttribute("d", "M15 12H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z");
	}
	svgMap.appendChild(path);
	return svgMap;
}



function setupToggle(sectionDiv, header, content) {
  // 預設為展開
  let isOpen = true;
  content.classList.remove("collapsed");
  header.querySelector("svg")?.replaceWith(createSvgIcon("less"));

  // let isOpen = false;

  // sectionDiv.addEventListener("mouseenter", () => {
  //   isOpen = true;
  //   content.classList.remove("collapsed");
  //   header.querySelector("svg")?.replaceWith(createSvgIcon("less"));
  // });

  // sectionDiv.addEventListener("mouseleave", () => {
  //   isOpen = false;
  //   content.classList.add("collapsed");
  //   header.querySelector("svg")?.replaceWith(createSvgIcon("more"));
  // });
  sectionDiv.addEventListener("click", () => {
    isOpen = !isOpen;

    if (isOpen) {
      content.classList.remove("collapsed");
      header.querySelector("svg")?.replaceWith(createSvgIcon("less"));
    } else {
      content.classList.add("collapsed");
      header.querySelector("svg")?.replaceWith(createSvgIcon("more"));
    }
  });
}

function createChart(canvas, chartData, defaultType = "doughnut") {
  // tooltip 會因為沒有重畫被擋住，加了就OK了
  // ✅ 確保同一個 canvas 不會被畫第二次
  const existingChart = Chart.getChart(canvas);
  if (existingChart) {
    existingChart.destroy(); // 清除前一個圖表
  }
  const ctx = canvas.getContext("2d");

  // 從 chartData 取出翻譯對應表（如果有）
  const translations = chartData.translations || {};
  console.log(translations);

  // 判斷是否為完整的 Chart.js 設定（含 type 和 options）
  const config = chartData.type
    ? chartData // 已是完整的 config，直接使用
    : {
        type: defaultType, // 預設類型
        data: chartData,
        options: {
          responsive: false, // ✅ 停用自動縮放
          maintainAspectRatio: false, // ✅ 允許手動控制比例
          // cutout: "80%", // ✅ 控制圓心空白比例
          // radius: "100%", // ✅ 控制圓餅整體大小（可調整）
          plugins: {
            legend: {
              position: "bottom"
            },
            tooltip: {
              enabled: true,
              callbacks: {
                label: function (tooltipItem) {
                  const dataIndex = tooltipItem.dataIndex;
                  const datasetIndex = tooltipItem.datasetIndex;

                  const originalLabel = chartData.labels[dataIndex];
                  const translatedLabel = translations[originalLabel] || originalLabel;
                  const value = chartData.datasets[datasetIndex].data[dataIndex];

                  return `${translatedLabel}: ${value}`;
                }
              }
            }
          }
        }
      };

  new Chart(ctx, config);
}
initPage();