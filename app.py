from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

app = Flask(__name__)

def fetch_site_data(url):
    if not url.startswith("http"):
        url = "http://" + url
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "Tidak ada"
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc["content"] if meta_desc else "Tidak ditemukan"
        h1 = soup.find("h1").text.strip() if soup.find("h1") else "Tidak ditemukan"
        word_count = len(soup.get_text().split())
        has_https = url.startswith("https://")
        return {
            "title": title,
            "meta_desc": meta_desc,
            "h1": h1,
            "word_count": word_count,
            "https": has_https,
            "error": None
        }
    except Exception as e:
        return {"error": str(e)}

def generate_insight(data):
    insights = []
    if data["word_count"] < 300:
        insights.append("Konten terlalu tipis. Tambahkan lebih banyak paragraf atau penjelasan.")
    if "Tidak ditemukan" in data["h1"]:
        insights.append("H1 (judul utama) tidak ditemukan. Tambahkan heading H1 untuk SEO.")
    if "Tidak ditemukan" in data["meta_desc"]:
        insights.append("Meta description tidak ada. Tambahkan deskripsi untuk meningkatkan CTR.")
    if not data["https"]:
        insights.append("Website belum menggunakan HTTPS. Aktifkan SSL untuk keamanan dan SEO.")
    if len(data["title"]) < 20:
        insights.append("Title terlalu pendek. Gunakan judul yang lebih deskriptif.")
    if not insights:
        insights.append("Struktur halaman cukup baik. Fokus ke backlink dan optimasi konten.")
    return insights

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        url = request.form["url"]
        data = fetch_site_data(url)
        if data.get("error"):
            result = {"error": data["error"]}
        else:
            insights = generate_insight(data)
            result = {**data, "insights": insights, "domain": url}
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

