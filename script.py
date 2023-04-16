import requests
from bs4 import BeautifulSoup
import csv
import sqlite3
from datetime import date

class VergeScraper:
    def __init__(self):
        self.url = "https://www.theverge.com"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

#   this function extracts the useful information from the bs4 tag.
    def extract_dicts_from_soup(self, soup):
        article_list = []
        a_tags_title = soup.find_all('a', class_='group-hover:shadow-underline-franklin')
        a_tags_autohors = soup.find_all('a',class_='text-gray-31 hover:shadow-underline-inherit dark:text-franklin mr-8')
        span_tags_dates = soup.find_all('span',class_='text-gray-63 dark:text-gray-94')
        a_tags_urls = soup.find_all('a',class_='group-hover:shadow-underline-franklin')
        titles = []
        authors = []
        dates = []
        urls = []
        for a_tag_title in a_tags_title:
            title = a_tag_title.text
            titles.append(title)
        for a_tag_author in a_tags_autohors:
            author = a_tag_author.text
            authors.append(author)
        for span_tag_date in span_tags_dates:
            date = span_tag_date.text
            dates.append(date)
        for a_tag_url in a_tags_urls:
            url = self.url + a_tag_url['href']
            urls.append(url)

        for i in range(len(titles)):
            article_dict = {'headline' : titles[i], 'url' : urls[i], 'author' : authors[i+1], 'date_posted' : dates[i+1]}
            article_list.append(article_dict)
        return article_list
    

    def get_articles(self):
        page = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        article_list = self.extract_dicts_from_soup(soup)
        return article_list

    def store_csv(self, article_list):
        filename = date.today().strftime('%d%m%Y') + '_verge.csv'
        with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'url', 'headline', 'author', 'date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i, article in enumerate(article_list):
                writer.writerow({'id': i, 'url': article['url'], 'headline': article['headline'], 'author': article['author'], 'date': article['date_posted']})

    def store_sqlite(self, article_list):
        conn = sqlite3.connect('articles.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS articles
                     (id INTEGER PRIMARY KEY, url TEXT, headline TEXT, author TEXT, date TEXT)''')
        for i, article in enumerate(article_list):
            c.execute("INSERT OR IGNORE INTO articles (id, url, headline, author, date) VALUES (?, ?, ?, ?, ?)", (i, article['url'], article['headline'], article['author'], article['date_posted']))
        conn.commit()
        conn.close()
if __name__ == "__main__":
    scraper = VergeScraper()
    article_list = scraper.get_articles()
    scraper.store_csv(article_list)
    scraper.store_sqlite(article_list)
