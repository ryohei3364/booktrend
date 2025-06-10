console.log("啟動navbar.js");

import { loadLang } from './language.js';

export async function initNavbar() {
  const { langContent } = await loadLang();
  renderNav(langContent);
}
const searchNav = document.getElementById("searchNav");
const rankingNav = document.getElementById("rankingNav");

async function renderNav(data) {
  searchNav.textContent = data.search;
  rankingNav.textContent = data.ranking;
}



// initPage();


// const navContainer = document.querySelector(".menu__navbar--container");

// export function renderNav(data) {
//   const navBar = createNavBar(data);
//   navContainer.appendChild(navBar);
// }

// function createNavBar(data) {
//   const NavBar = document.createElement("div");
//   NavBar.className = "menu__item--header";

//   const links = [
//     { href: "/search", key: "search" },
//     { href: "/ranking", key: "ranking" }
//   ];

//   links.forEach(link => {
//     const aTag = document.createElement("a");
//     aTag.href = link.href;
//     aTag.className = "menu__item--header--a";
//     aTag.textContent = data[link.key];
//     NavBar.appendChild(aTag);
//   });

//   return NavBar;
// }
