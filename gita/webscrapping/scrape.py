import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import os
import time

def scrape_page_content(url):
    """
    Scrapes the main text content from a given page URL.
    The content is expected to be within relevant divs containing textual content.
    """
    try:
        print(f"  -> Scraping content from: {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        page = {"heading": soup.select_one("h1").text.strip() if soup.select_one("h1") else "No Heading"}
        page['body'] = []

        # Extract text from all potential text-holding elements
        selectors = [".text-center", ".text-base", ".em\\:mb-4.em\\:leading-8.em\\:text-base.s-justify"]

        for selector in selectors:
            for elem in soup.select(selector):
                text = elem.get_text(strip=True)
                if text:
                    page['body'].append(text)

        content_text = "\n".join(page['body'])
        return content_text

    except requests.exceptions.RequestException as e:
        print(f"    [Error] Could not fetch {url}: {e}")
        return None
    except Exception as e:
        print(f"    [Error] An error occurred while scraping {url}: {e}")
        return None

def scrape_vedabase_bg_chapters():
    """
    Scrapes introductory links and their content from the Bhagavad-gītā
    library page on vedabase.io and saves it to a JSON file.
    """
    base_url = "https://vedabase.io"
    library_url = f"{base_url}/en/library/bg/"
    
    # --- Output File Configuration ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "json_output")
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, "gita.json")
    
    print(f"Scraping index page: {library_url}")

    try:
        # Send an HTTP GET request to the URL
        response = requests.get(library_url)
        response.raise_for_status()

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # This selector finds all divs with class="mb-4", which contain the introductory links.
        all_divs = soup.select(".mb-4")

        if not all_divs:
            print("No introductory links found. The website structure might have changed.")
            return

        scraped_data = []
        print("\n--- Found Introductory Links ---")
        print("Beginning to scrape content from each link...\n")
        
        # Loop through each link, scrape its content, and store it
        for div_tag in all_divs:
            link_tag = div_tag.find('a')
            if not link_tag:
                continue
            
            title = link_tag.get_text(strip=True)
            relative_url = link_tag.get('href')
            full_url = urljoin(base_url, relative_url)
            
            print(f"Processing: {title}")
            
            content = scrape_page_content(full_url)
            
            if content:
                scraped_data.append({
                    "title": title,
                    "url": full_url,
                    "content": content
                })
            
            # Be polite and add a small delay between requests
            time.sleep(1)

        # Save the collected data to a JSON file
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=4)
        
        print(f"\nScraping complete. Data for {len(scraped_data)} pages saved to '{output_filename}'")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the URL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    scrape_vedabase_bg_chapters()