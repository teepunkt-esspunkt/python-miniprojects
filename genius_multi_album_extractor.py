# first attempt to get lyrics from genius

import os
import re
import time
import hashlib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# === CONFIG ===
ALBUM_URLS = [ 
  #put genius album urls here
]

LINK_PATTERN = re.compile(r"https://genius\.com/[^\"?#]+-lyrics")


# === SETUP ===
options = Options()
options.add_argument("--headless")
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)

# === FUNCTIONS ===
def get_next_folder_name(base_name="lyrics"):
    counter = 1
    while os.path.exists(f"{base_name}{counter}"):
        counter += 1
    return f"{base_name}{counter}"

def short_hash(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()[:4]

def extract_album_year(soup):
    for span in soup.find_all("span"):
        text = span.get_text(strip=True)
        match = re.search(r"(19|20)\\d{2}", text)
        if match:
            return match.group(0)
    return "____"

def get_song_links(album_url):
    print(f"Loading album page: {album_url}")
    driver.get(album_url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    year = extract_album_year(soup)
    links = []

    # Only find links inside the tracklist (chart_row-content)
    track_links = soup.select("div.chart_row-content a[href]")
    for a in track_links:
        href = a["href"]
        if LINK_PATTERN.match(href):
            links.append(href.strip())

    # Deduplicate and preserve order
    seen = set()
    ordered_links = []
    for i, href in enumerate(links):
        if href not in seen:
            seen.add(href)
            ordered_links.append((i + 1, href, year))

    return ordered_links

def extract_lyrics(url):
    print(f"Visiting: {url}")
    driver.get(url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    lyrics_blocks = soup.find_all("div", {"data-lyrics-container": "true"})
    if not lyrics_blocks:
        return None

    # Collect lines while filtering out non-lyrics content
    lines = []
    for block in lyrics_blocks:
        for line in block.stripped_strings:
            # Skip common non-lyrics patterns
            if "Contributors" in line or "Read More" in line or "Lyrics" in line:
                continue
            lines.append(line)

    # DEBUG (optional)
    print("RAW LINES:", lines)

    # Filter out any text before first [Verse], [Hook], etc.
    for idx, line in enumerate(lines):
        if line.startswith('['):  # First verse/hook found
            lines = lines[idx:]
            break

    lyrics_text = "\n".join(lines)
    return lyrics_text.strip()





def save_lyrics(title, lyrics, album_name, year, output_file):
    safe_title = re.sub(r'[\\/*?:\"<>|]', "_", title)
    heading = f"{{{safe_title} - {album_name} - {year}}}"

    with open(output_file, "a", encoding="utf-8") as f:
        f.write(f"{heading}\n\n{lyrics}\n\n{'=' * 50}\n\n")

def generate_unique_filename(base_name):
    if not os.path.exists(base_name):
        return base_name

    name, ext = os.path.splitext(base_name)
    counter = 1
    while os.path.exists(f"{name}_{counter}{ext}"):
        counter += 1
    return f"{name}_{counter}{ext}"

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, get_next_folder_name())
    os.makedirs(output_dir, exist_ok=True)

    for url in ALBUM_URLS:
        album_slug = url.rstrip("/").split("/")[-1]
        album_name = album_slug.replace("-", " ").lower()

        # Save each album's lyrics inside this new folder
        base_output_file = os.path.join(output_dir, f"{album_slug[:10].lower()}_{short_hash(album_slug)}.txt")
        output_file = generate_unique_filename(base_output_file)

        print(f"\n== Scraping album: {album_name} ==")
        links = get_song_links(url)
        print(f"Found {len(links)} songs.")

        if not links:
            print(f"⚠️ No songs found for: {album_name}")
            continue

        for i, (track_num, link, year) in enumerate(links, 1):
            lyrics = extract_lyrics(link)
            if lyrics:
                title = link.split("/")[-1].replace("-lyrics", "").replace("-", " ").title()
                save_lyrics(title, lyrics, album_name, year, output_file)
                print(f"[{i}/{len(links)}] ✓ Added: {title}")
            else:
                print(f"[{i}/{len(links)}] ✗ No lyrics found.")

    driver.quit()


# === RUN ===
if __name__ == "__main__":
    main()
