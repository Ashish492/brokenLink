import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def is_valid_url(url):
    """ Check if the URL is valid. """
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def find_broken_and_empty_links(base_url, url, visited):
    """ Recursively find broken links and empty href tags. """
    broken_links = []
    empty_href_tags = []

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        for link in soup.find_all('a'):
            href = link.get('href')
            print(href,"processing")
            if not href or href == '#':
                empty_href_tags.append((url, str(link)))
            else:
                full_url = urljoin(base_url, href)
                parsed_full_url = urlparse(full_url)
                if parsed_full_url.netloc != urlparse(base_url).netloc:
                    continue

                if full_url not in visited:
                    visited.add(full_url)
                    if not is_valid_url(full_url):
                        broken_links.append((url, full_url))
                    else:
                        sub_broken, sub_empty = find_broken_and_empty_links(base_url, full_url, visited)
                        broken_links.extend(sub_broken)
                        empty_href_tags.extend(sub_empty)

    except requests.RequestException as e:
        print(f"Error accessing {url}: {e}")

    return broken_links, empty_href_tags

if __name__ == "__main__":
    target_url = "https://www.firekirinwebsite.com/"
    parsed_url = urlparse(target_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    visited = set()
    visited.add(target_url)
    broken_links, empty_href_tags = find_broken_and_empty_links(base_url, target_url, visited)

     # Generate a safe filename based on the base URL
    domain = parsed_url.netloc.replace(":", "_")
    filename = f"link_report_{domain}.txt"

    with open(filename, "w") as f:
        f.write("Broken Links:\n")
        for i, (base_page, broken_link) in enumerate(broken_links, 1):
            f.write(f"{i}. From page: {base_page} -> Broken link: {broken_link}\n")

        f.write("\nEmpty href tags:\n")
        for i, (base_page, empty_tag) in enumerate(empty_href_tags, 1):
            f.write(f"{i}. From page: {base_page} -> Empty href tag: {empty_tag}\n")

    print(f"Report written to {filename}")
