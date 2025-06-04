from flask import Flask, render_template, request, send_file
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import io
import csv
import time

app = Flask(__name__)

def check_link_status(url, timeout):
    try:
        resp = requests.head(url, timeout=timeout, allow_redirects=True)
        return 200 <= resp.status_code < 400
    except Exception:
        return False

def fetch_links_with_selenium(url, div_class_string):
    class_selector = '.' + '.'.join(div_class_string.strip().split())
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        divs = soup.select(f"div{class_selector}")
        links = []
        for div in divs:
            for a in div.find_all("a", href=True):
                link = a["href"]
                if not link.startswith("http"):
                    link = requests.compat.urljoin(url, link)
                links.append(link)
        return list(set(links))
    finally:
        driver.quit()

@app.route('/', methods=['GET', 'POST'])
def index():
    up_links = []
    down_links = []
    links = []
    url = ''
    div_class = ''
    error = None
    timeout = 5
    if request.method == 'POST':
        url = request.form['url']
        div_class = request.form['div_class']
        timeout = int(request.form.get('timeout', 5))
        try:
            links = fetch_links_with_selenium(url, div_class)
            if not links:
                error = f"No links found in divs with class '{div_class}'."
            else:
                for link in links:
                    if check_link_status(link, timeout):
                        up_links.append(link)
                    else:
                        down_links.append(link)
        except Exception as e:
            error = f"Error: {e}"
    summary = {
        "up_count": len(up_links),
        "down_count": len(down_links),
        "total": len(up_links) + len(down_links)
    }
    return render_template(
        'index.html',
        up_links=up_links,
        down_links=down_links,
        url=url,
        div_class=div_class,
        error=error,
        summary=summary,
        timeout=timeout
    )

@app.route('/download/<status>')
def download_csv(status):
    links = request.args.getlist('links')
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['link'])
    for link in links:
        cw.writerow([link])
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    filename = f"{status}_links.csv"
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(debug=True)