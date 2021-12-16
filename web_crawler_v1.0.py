import os
import sys
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from argparse import ArgumentParser
from colorama import Fore, Style, init


# Looking for all href and src on the site
def href_and_src_parser(site_url):
    # Make url view, like https://examle.com
    parts = urlparse(address)
    filtered_address = f"{parts.scheme}://{parts.netloc}"

    # Get request and parse it with BeautifulSoup
    req = requests.get(site_url)
    soup = BeautifulSoup(req.text, 'html.parser')

    href = soup.find_all(href=True)
    src = soup.find_all(src=True)

    urls = set()

    # Find all href
    for value in href:
        if value.get('href').startswith('http'):
            urls.add(value.get('href'))
        if value.get('href').startswith('/'):
            urls.add(filtered_address + value.get('href'))
        if value.get('href').startswith('?'):
            urls.add(filtered_address + '/' + value.get('href'))

    # Find all src
    for value in src:
        if value.get('src').startswith('http'):
            urls.add(value.get('src'))
        if value.get('src').startswith('/'):
            urls.add(filtered_address + value.get('src'))
        if value.get('src').startswith('?'):
            urls.add(filtered_address + '/' + value.get('href'))

    # Get only unique urls
    return urls


# Find urls, that belongs to our site
# for example: api.example.com, example1.com, example.net
# and not: somesite.net, github.com, etc.
def sub_and_domains_only(site_urls):
    # Make url view, like example.com
    domain = urlparse(address)
    filtered_address = domain.netloc

    filtered_urls = []

    for url in site_urls:
        # Regex for sub and domains only
        if re.match(r'(https?://)?(www\.)?([-a-zA-Z0-9()@:%_+.~#?&/=]*\.)?'+filtered_address+r'\b([-a-zA-Z0-9()@:%_+.~#?&/=]*)', url):
            filtered_urls.append(url)
        else:
            continue

    return filtered_urls


# Find, if urls contain interesting to us [extensions]
def extensions_and_directories_only(site_urls):
    filtered_urls = []

    for url in site_urls:
        if ('.' not in url.split('/')[-1]) or (url.split('.')[-1] in extensions):
            filtered_urls.append(url)
        else:
            continue
    return filtered_urls


# Recursive function to get urls from another url
# for example: check for links in example1.com, if we find example2.com
# check for links in example2.com and etc.
def crawler(site_url, count):
    # Do all the previous steps, to collect the links
    filtered_urls = extensions_and_directories_only(sub_and_domains_only(href_and_src_parser(site_url)))

    for filtered_url in filtered_urls:
        # Make global [base_urls], to check if it already contains our url
        if filtered_url in base_urls:
            continue
        # If we want, to collect some amount of urls(not all)
        if count != 0:
            if len(base_urls) == count:
                break
        base_urls.append(filtered_url)
        # Print url
        print(Fore.GREEN+'[+]  Processing:'+Style.RESET_ALL, filtered_url)
        crawler(filtered_url, count)


# Save collected urls to file
def save_urls_to_file(path, urls_to_download):
    with open(path, 'w') as file:
        for url_to_download in urls_to_download:
            file.write(url_to_download+'\n')
        print(Fore.GREEN+'[+]  All urls successfully downloaded'+Style.RESET_ALL)


if __name__ == '__main__':
    init()
    extensions = ['js', 'html']
    base_urls = []

    # Available arguments(in cmd type -h for help)
    parser = ArgumentParser()
    parser.add_argument('-a', '--address', help="Example: https://example.com", default='', required=True)
    parser.add_argument('-c', '--count', help="Count of urls(default - 0(get all))", default=0)
    parser.add_argument('-f', '--file', help="Save results to file", default='')
    args = parser.parse_args()

    try:
        # Check, if file already exists
        if args.file != '':
            if os.path.exists(args.file):
                print(Fore.RED + '[!]  Output file cannot be used because it already exists' + Style.RESET_ALL)
                sys.exit(1)
        # Regex, to match the correct url format
        if re.match(r'(https?://(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&/=]*))', args.address):
            address = str(args.address)
            crawler(address, int(args.count))
            print(Fore.GREEN+'[+]  Count of unique URLS:'+Style.RESET_ALL, len(base_urls))
        else:
            print(Fore.RED+'[!]  Not correct URL format'+Style.RESET_ALL)
            sys.exit(1)
        # Save results to file
        if args.file != '':
            try:
                save_urls_to_file(args.file, base_urls)
            except FileNotFoundError:
                print(Fore.RED+'[!]  Not existing file or path'+Style.RESET_ALL)
    # We can interrupt the program at any time(ctrl+c)
    except KeyboardInterrupt:
        print(Fore.RED+'[!]  Interrupted'+Style.RESET_ALL)
        print(Fore.GREEN+'[+]  Count of unique URLS:'+Style.RESET_ALL, len(base_urls))
