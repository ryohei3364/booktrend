![booktrend logo](<public/booktrend_logo.png>)

# BookTrend - Global Book Trend Monitoring Platform
BookTrend is a web platform that visualizes global bookstore bestseller trends with multilingual support. Users can explore real-time rankings by country, category, or keyword to discover popular books across different markets.

### Demo: https://booktrend.online
### API: https://booktrend.online/docs
### Test Account: 
<div style="width: 300px;">

| Account | Password |
|--------|----------|
| test@test   | test |

</div>

# Main Feature
### multilingual interface support
Supports a multi-language interface, including the navigation bar, buttons, and titles.

➤ Technologies Used: navigator.languages, multilingual jsons

![multilingual gif](<public/multilingual.gif>)

### Cross-Language Book Matching
Uses fuzzy matching to detect and link the same book in different languages.

➤ Technologies Used: googletrans, RapidFuzz

![multilingual gif](<public/same book.png>)

### Automated daily web crawler
Automated web crawlers run daily to update real-time bestseller rankings.

➤ Technologies Used: Seleium, Beautiful soup, Docker, Crontab

![multilingual gif](<public/web crawler.gif>)

### Book Trend Word Clouds
Country-specific keyword word clouds for visualizing book trends.

➤ Technologies Used: SpaCy, D3.js

![multilingual gif](<public/wordcloud.png>)

# Artictecture
![multilingual gif](<public/web_structure.png>)

# Database Schema
![multilingual gif](<public/database.png>)

# Contact
- 錢芝萍 Chih Pin Chien
- Email: ryohei3364@gmail.com