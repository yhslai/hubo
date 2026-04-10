#!/usr/bin/env python3
import argparse
import re
import sys
import requests
from bs4 import BeautifulSoup

# ANSI escape codes for colored terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def streamtape_get_dl_link(link):
    """Extracts the direct download link from a Streamtape URL."""
    try:
        # Convert embed link to video link if necessary
        if "/e/" in link:
            link = link.replace("/e/", "/v/")

        # Fetch the page
        response = requests.get(link)
        response.raise_for_status() 
        html_source = response.text

        # Extract the token string using regex
        norobot_link_pattern = re.compile(r"document\.getElementById\('norobotlink'\)\.innerHTML = (.+?);")
        norobot_link_matcher = norobot_link_pattern.search(html_source)

        if norobot_link_matcher:
            norobot_link_content = norobot_link_matcher.group(1)
            token_pattern = re.compile(r"token=([^&']+)")
            token_matcher = token_pattern.search(norobot_link_content)

            if token_matcher:
                token = token_matcher.group(1)

                # Parse HTML to find the hidden div
                soup = BeautifulSoup(html_source, 'html.parser')
                div_element = soup.select_one("div#ideoooolink[style='display:none;']")

                if div_element:
                    streamtape = div_element.get_text()
                    full_url = f"https:/{streamtape}&token={token}"
                    return f"{full_url}&dl=1s"
                    
        return None # Return None if patterns weren't found

    except requests.exceptions.RequestException as e:
        print(f"{RED}Network Error:{RESET} {e}", file=sys.stderr)
    except Exception as e:
        print(f"{RED}An unexpected error occurred:{RESET} {e}", file=sys.stderr)
        
    return None

def main():
    # Set up the command line argument parser
    parser = argparse.ArgumentParser(
        description="Extract direct download links from Streamtape URLs.",
        epilog="Example: python streamtape_cli.py https://streamtape.com/v/..."
    )
    
    # Add the URL argument
    parser.add_argument(
        "url", 
        help="The Streamtape URL (either /v/ or /e/ format)"
    )
    
    # Add an optional flag to only output the raw URL (useful for piping into downloaders)
    parser.add_argument(
        "-q", "--quiet", 
        action="store_true", 
        help="Only output the raw download URL (no colors or extra text)"
    )

    args = parser.parse_args()

    if not args.quiet:
        print(f"{YELLOW}Processing URL...{RESET}")

    dl_link = streamtape_get_dl_link(args.url)

    if dl_link:
        if args.quiet:
            # Print ONLY the link so it can be piped to wget/curl
            print(dl_link)
        else:
            print(f"{GREEN}{BOLD}Success! Direct Link Extracted:{RESET}")
            print(dl_link)
    else:
        if not args.quiet:
            print(f"{RED}Failed to extract the download link. The file might be deleted or the script regex needs updating.{RESET}", file=sys.stderr)
        sys.exit(1) # Return a non-zero exit code to indicate failure to the OS

if __name__ == "__main__":
    main()