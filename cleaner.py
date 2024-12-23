import os
import sys
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from collections import defaultdict

# Set up logging
log_format = '%(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)
logging.getLogger('').handlers[0].setFormatter(logging.Formatter(log_format))

HARDCODED_EXTENSIONS = [
    ".jpg", ".jpeg", ".png", ".gif", ".pdf", ".svg", ".json",
    ".css", ".js", ".webp", ".woff", ".woff2", ".eot", ".ttf", ".otf", ".mp4", ".txt"
]

def has_extension(url, extensions):
    """
    Check if the URL has a file extension matching any of the provided extensions.

    Args:
        url (str): The URL to check.
        extensions (list): List of file extensions to match against.

    Returns:
        bool: True if the URL has a matching extension, False otherwise.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    extension = os.path.splitext(path)[1].lower()

    return extension in extensions

def clean_url(url):
    """
    Clean the URL by removing redundant port information for HTTP and HTTPS URLs.

    Args:
        url (str): The URL to clean.

    Returns:
        str: Cleaned URL.
    """
    parsed_url = urlparse(url)
    
    if (parsed_url.port == 80 and parsed_url.scheme == "http") or (parsed_url.port == 443 and parsed_url.scheme == "https"):
        parsed_url = parsed_url._replace(netloc=parsed_url.netloc.rsplit(":", 1)[0])

    return parsed_url.geturl()

def clean_urls(urls, extensions, placeholder=None):
    """
    Clean a list of URLs by removing unnecessary parameters and query strings.

    Args:
        urls (list): List of URLs to clean.
        extensions (list): List of file extensions to check against.
        placeholder (str): Placeholder for parameter values. If None, keep the original values.

    Returns:
        list: List of cleaned URLs.
    """
    cleaned_urls = set()
    for url in urls:
        cleaned_url = clean_url(url)
        if not has_extension(cleaned_url, extensions):
            parsed_url = urlparse(cleaned_url)
            query_params = parse_qs(parsed_url.query)
            if placeholder:
                cleaned_params = {key: placeholder for key in query_params}
            else:
                cleaned_params = query_params
            cleaned_query = urlencode(cleaned_params, doseq=True)
            cleaned_url = parsed_url._replace(query=cleaned_query).geturl()
            cleaned_urls.add(cleaned_url)
    return list(cleaned_urls)

def merge_parameters(urls):
    """
    Merge parameters for the same endpoint into a single URL.

    Args:
        urls (list): List of URLs to process.

    Returns:
        list: List of merged URLs.
    """
    endpoint_params = defaultdict(dict)
    for url in urls:
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)
        endpoint = urlunparse(parsed_url._replace(query=""))

        for key, value in params.items():
            if key in endpoint_params[endpoint]:
                endpoint_params[endpoint][key].update(value)
            else:
                endpoint_params[endpoint][key] = set(value)

    merged_urls = []
    for endpoint, params in endpoint_params.items():
        merged_query = urlencode({key: list(values)[0] for key, values in params.items()}, doseq=True)
        merged_urls.append(urlunparse(urlparse(endpoint)._replace(query=merged_query)))

    return merged_urls

def process_urls(input_file, placeholder=None):
    """
    Process URLs from the input file, clean them, merge parameters, and save to output file.

    Args:
        input_file (str): The input file containing URLs.
        placeholder (str): Placeholder for parameter values. If None, keep the original values.

    Returns:
        None
    """
    with open(input_file, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    logging.info(f"Found {len(urls)} URLs in {input_file}")

    cleaned_urls = clean_urls(urls, HARDCODED_EXTENSIONS, placeholder)
    logging.info(f"Found {len(cleaned_urls)} URLs after cleaning")

    merged_urls = merge_parameters(cleaned_urls)
    logging.info(f"Found {len(merged_urls)} URLs after merging parameters")

    sorted_urls = sorted(merged_urls)

    output_file = os.path.splitext(input_file)[0] + "_cleaned.txt"
    with open(output_file, "w") as f:
        for url in sorted_urls:
            f.write(url + "\n")

    logging.info(f"Saved cleaned URLs to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python cleaner.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    if not os.path.isfile(input_file):
        print(f"Error: File {input_file} not found")
        sys.exit(1)

    process_urls(input_file)
