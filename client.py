import requests, os

url = "https://www.youtube.com/watch?v=8ulA5-cb2po"

response = requests.post("http://127.0.0.1:8000/convert", json={"url": url})

with open("slides.pdf", "wb") as f:
    f.write(response.content)

os.startfile("slides.pdf")