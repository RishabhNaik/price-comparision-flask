from flask import Flask, render_template
from flask_mysqldb import MySQL
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pricecomparator'

mysql = MySQL(app)

def get_price(url):
    # Set headers to imitate a browser
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    # HTTP Request
    webpage = requests.get(url)
    
    # Soup Object containing all data
    soup = BeautifulSoup(webpage.content, "html.parser")
    
    # Check which website the URL belongs to and extract the price accordingly
    if "vijaysales.com" in url:
        price_span = soup.find('span', class_='to_top').find_next_sibling('span')
        price = price_span.text.strip()
        domain = "vijaysales.com"
    elif "reliancedigital.in" in url:
        price_span = soup.find('span', class_='TextWeb__Text-sc-1cyx778-0 cJQfDP')
        price = price_span.text.strip()
        domain = "reliancedigital.in"
    elif "kohinoorelectronics.com" in url:
        price_span = soup.find('li', class_='joy-price-value')
        price = price_span.text.strip().split()[1]  # Extract the second part which is the price
        domain = "kohinoorelectronics.com"
    elif "amazon.in" in url:
        # For Amazon, use lxml parser
        soup = BeautifulSoup(webpage.content, "lxml")
        print(soup)
        price_element = soup.find("span", attrs={'class': 'a-price-whole'})
        if price_element:
            price_text = price_element.text.strip()
            price_without_comma = price_text.replace(',', '')
            price_without_dot = price_without_comma.replace('.','')
            price = price_without_dot
        else:
            price = "Price information not found"
        domain = "amazon.in"
    else:
        # If the URL format doesn't match any of the supported websites, return None
        print("Website not supported or URL format not recognized.")
        return None
    
    return price, domain

def get_prices(urls):
    prices = []
    for url in urls:
        price = get_price(url)
        if price:
            prices.append(price)
    return prices

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product")
    data = cur.fetchall()
    cur.close()
    print(data)
    return render_template('index.html', data=data)

@app.route('/product/<pid>')
def show_product(pid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product WHERE id = %s", (pid,))
    product = cur.fetchone()
    cur.execute("SELECT url FROM urls WHERE product_id = %s", (pid,))
    urls = cur.fetchall()
    cur.close()
    
    product_title = product[1]  # Assuming the product title is in the second column
    product_image = product[2]  # Assuming the product image path is in the third column
    
    urls_list = [url[0] for url in urls]
    data = get_prices(urls_list)
    
    return render_template('detail.html', product_title=product_title,
                           product_image=product_image,
                           data=data)


if __name__ == '__main__':
    app.run(debug=True)