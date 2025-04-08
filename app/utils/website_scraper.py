# app/utils/website_scraper.py
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def scrape_website(url: str) -> dict:
    """
    Scrape a website using AsyncWebCrawler and return the full page content.
    
    Args:
        url: The website URL to scrape
        
    Returns:
        dict: Website information with full content
    """
    try:
        logging.info(f"Scraping website: {url}")
        
        # Extract domain name
        domain = urlparse(url).netloc
        
        # Initialize basic website info
        website_info = {
            'domain': domain,
            'url': url,
            'content': ''  # Will store the full page content
        }

        crawl_config = CrawlerRunConfig(page_timeout=120000)
        
        # Use the AsyncWebCrawler to extract content
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(url=url, config=crawl_config)
            
            if not result.success:
                raise Exception(f"Failed to crawl website: {result.error if hasattr(result, 'error') else 'Unknown error'}")
            
            # Store the full markdown content
            website_info['content'] = result.markdown
        
        logging.info(f"Successfully scraped website: {url}")
        return website_info
        
    except Exception as e:
        logging.error(f"Error scraping website {url}: {str(e)}")
        return {
            'domain': domain if 'domain' in locals() else urlparse(url).netloc,
            'url': url,
            'error': str(e),
            'content': ''
        }

# async def scrape_website(url: str) -> dict:
#     """
#     Scrape a website and extract useful information for email generation.
#     """

#     try:
#         logging.info(f"Scraping website: {url}")
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#         }
        
#         response = requests.get(url, headers=headers, timeout=15)
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.text, 'html.parser')
        
#         # Extract domain name
#         domain = urlparse(url).netloc
        
#         # Extract basic website information
#         website_info = {
#             'domain': domain,
#             'url': url,
#             'title': soup.title.string if soup.title else '',
#             'meta_description': '',
#             'company_name': '',
#             'headings': [],
#             'main_text': '',
#             'contact_info': {
#                 'email': '',
#                 'phone': '',
#                 'address': ''
#             }
#         }
        
#         # Extract meta description
#         meta_desc = soup.find('meta', attrs={'name': 'description'})
#         if meta_desc and 'content' in meta_desc.attrs:
#             website_info['meta_description'] = meta_desc['content']
        
#         # Extract company name (often in logo alt text or certain HTML elements)
#         logo = soup.find('img', alt=True)
#         if logo and logo.get('alt'):
#             website_info['company_name'] = logo.get('alt')
        
#         # If no company name from logo, try to get from title
#         if not website_info['company_name'] and website_info['title']:
#             title_parts = website_info['title'].split('|')
#             if len(title_parts) > 1:
#                 website_info['company_name'] = title_parts[0].strip()
#             else:
#                 title_parts = website_info['title'].split('-')
#                 if len(title_parts) > 1:
#                     website_info['company_name'] = title_parts[0].strip()
        
#         # Extract headings
#         for i in range(1, 4):  # h1, h2, h3
#             for heading in soup.find_all(f'h{i}'):
#                 if heading.text.strip():
#                     website_info['headings'].append(heading.text.strip())
        
#         # Extract main text content (paragraphs)
#         main_text = []
#         for p in soup.find_all('p'):
#             if p.text.strip() and len(p.text.strip()) > 20:  # Filter out short paragraphs
#                 main_text.append(p.text.strip())
#         website_info['main_text'] = '\n\n'.join(main_text[:5])  # Limit to first 5 substantial paragraphs
        
#         # Look for contact information
#         # Email (basic pattern, can be enhanced)
#         email_links = soup.select('a[href^="mailto:"]')
#         if email_links:
#             href = email_links[0].get('href')
#             website_info['contact_info']['email'] = href.replace('mailto:', '')
        
#         # Phone (basic pattern, can be enhanced)
#         phone_links = soup.select('a[href^="tel:"]')
#         if phone_links:
#             href = phone_links[0].get('href')
#             website_info['contact_info']['phone'] = href.replace('tel:', '')
        
#         logging.info(f"Successfully scraped website: {url}")
#         logging.info(f"Scraped website info is: {website_info}")
#         return website_info
        
#     except Exception as e:
#         logging.error(f"Error scraping website {url}: {str(e)}")
#         return {
#             'domain': urlparse(url).netloc,
#             'url': url,
#             'error': str(e),
#             'title': '',
#             'meta_description': '',
#             'company_name': '',
#             'headings': [],
#             'main_text': '',
#             'contact_info': {}
#         }