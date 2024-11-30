import requests
from bs4 import BeautifulSoup

url = "https://simplicable.com/en/industries"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
print(soup)
# Extract industries (assuming they're in list elements)
industries = [item.text for item in soup.find_all("span")]
print(industries)