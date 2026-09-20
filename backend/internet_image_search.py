import os
import re
import time
import urllib.parse
import requests
from typing import List, Dict, Any, Optional

try:
    from ddgs import DDGS
    DDG_AVAILABLE = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        DDG_AVAILABLE = True
    except ImportError:
        DDG_AVAILABLE = False


try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


class InternetImageSearcher:
    """
    Multi-engine Internet Image Aggregator.
    Searches the open web across all websites (Google/Bing/DDG indices, Wikimedia, Unsplash open media)
    without restricting results to closed APIs like Pinterest.
    """

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def search(self, query: str, limit: int = 20, safe_search: str = "moderate") -> Dict[str, Any]:
        """
        Searches the total internet for images matching the query.
        Returns aggregated, deduplicated image items with metadata.
        """
        clean_query = query.strip()
        if not clean_query:
            return {"success": False, "query": query, "total_results": 0, "images": [], "error": "Query cannot be empty."}

        print(f"[InternetImageSearcher] Executing global internet image search for: '{clean_query}'")
        
        aggregated_images: List[Dict[str, Any]] = []
        seen_urls = set()

        # Engine 1: DuckDuckGo Global Web Image Search (DDGS Library)
        if DDG_AVAILABLE:
            try:
                print("[InternetImageSearcher] Querying DuckDuckGo DDGS Web Index...")
                with DDGS() as ddgs:
                    try:
                        ddg_results = list(ddgs.images(clean_query, max_results=limit * 2))
                    except TypeError:
                        ddg_results = list(ddgs.images(query=clean_query, max_results=limit * 2))

                    for item in ddg_results:
                        img_url = item.get("image") or item.get("thumbnail")
                        if img_url and img_url not in seen_urls:
                            seen_urls.add(img_url)
                            aggregated_images.append({
                                "id": len(aggregated_images) + 1,
                                "title": item.get("title", clean_query),
                                "image_url": img_url,
                                "thumbnail_url": item.get("thumbnail") or img_url,
                                "source_url": item.get("url", "#"),
                                "source_domain": self._extract_domain(item.get("url", "")),
                                "width": item.get("width"),
                                "height": item.get("height"),
                                "engine": "Web Image"
                            })
            except Exception as e:
                print(f"[InternetImageSearcher] DDGS Library warning: {e}. Trying direct HTTP fallback...")

        # Engine 2: Direct DuckDuckGo Web API HTTP Fallback (if DDGS returned few or failed)
        if len(aggregated_images) < limit:
            try:
                print("[InternetImageSearcher] Querying Direct DDG Web HTTP API...")
                ddg_http_results = self._search_duckduckgo_http(clean_query, max_results=limit)
                for item in ddg_http_results:
                    img_url = item.get("image_url")
                    if img_url and img_url not in seen_urls:
                        seen_urls.add(img_url)
                        item["id"] = len(aggregated_images) + 1
                        aggregated_images.append(item)
            except Exception as e:
                print(f"[InternetImageSearcher] DDG HTTP Fallback warning: {e}")

        # Engine 3: Wikimedia Commons Open Media API
        if len(aggregated_images) < limit * 1.5:
            try:
                print("[InternetImageSearcher] Querying Wikimedia Commons Open Media API...")
                wiki_results = self._search_wikimedia(clean_query, limit=limit)
                for item in wiki_results:
                    img_url = item.get("image_url")
                    if img_url and img_url not in seen_urls:
                        seen_urls.add(img_url)
                        item["id"] = len(aggregated_images) + 1
                        aggregated_images.append(item)
            except Exception as e:
                print(f"[InternetImageSearcher] Wikimedia Commons search warning: {e}")

        # Engine 4: Unsplash Open Media Fallback
        if len(aggregated_images) < limit:
            try:
                print("[InternetImageSearcher] Querying Unsplash Open Web Media...")
                unsplash_results = self._search_unsplash_open(clean_query, limit=10)
                for item in unsplash_results:
                    img_url = item.get("image_url")
                    if img_url and img_url not in seen_urls:
                        seen_urls.add(img_url)
                        item["id"] = len(aggregated_images) + 1
                        aggregated_images.append(item)
            except Exception as e:
                print(f"[InternetImageSearcher] Unsplash fallback warning: {e}")

        final_list = aggregated_images[:limit]
        print(f"[InternetImageSearcher] Search complete. Retrieved {len(final_list)} total web images.")

        return {
            "success": True,
            "query": clean_query,
            "total_results": len(final_list),
            "images": final_list,
            "provider": "Multi-Engine Global Web Aggregator (DuckDuckGo, Wikimedia, Open Web)"
        }

    def _search_duckduckgo_http(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Direct HTTP scraper for DuckDuckGo image search JSON endpoint.
        """
        results = []
        try:
            # Token request
            token_url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
            res = requests.get(token_url, headers=self.headers, timeout=8)
            match = re.search(r'vqd=([\d-]+)\&', res.text)
            if not match:
                match = re.search(r'vqd=["\']([\d-]+)["\']', res.text)
            
            if match:
                vqd = match.group(1)
                params = {
                    "l": "us-en",
                    "o": "json",
                    "q": query,
                    "vqd": vqd,
                    "f": ",,,",
                    "p": "1"
                }
                i_url = f"https://duckduckgo.com/i.js?{urllib.parse.urlencode(params)}"
                i_res = requests.get(i_url, headers=self.headers, timeout=8)
                if i_res.status_code == 200:
                    data = i_res.json()
                    for row in data.get("results", [])[:max_results]:
                        img_url = row.get("image")
                        if img_url:
                            results.append({
                                "title": row.get("title", query),
                                "image_url": img_url,
                                "thumbnail_url": row.get("thumbnail") or img_url,
                                "source_url": row.get("url", "#"),
                                "source_domain": self._extract_domain(row.get("url", "")),
                                "width": row.get("width"),
                                "height": row.get("height"),
                                "engine": "Web Image"
                            })
        except Exception as err:
            print(f"[DDG Direct HTTP Scraper] Exception: {err}")
        return results

    def _search_wikimedia(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Queries Wikimedia Commons for public domain & open licensed photos.
        """
        results = []
        try:
            api_url = "https://commons.wikimedia.org/w/api.php"
            params = {
                "action": "query",
                "generator": "search",
                "gsrsearch": f"file:{query}",
                "gsrnamespace": "6",
                "gsrlimit": limit,
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "format": "json"
            }
            res = requests.get(api_url, params=params, headers=self.headers, timeout=6)
            if res.status_code == 200:
                data = res.json()
                pages = data.get("query", {}).get("pages", {})
                for page_id, page in pages.items():
                    imageinfo = page.get("imageinfo", [{}])[0]
                    img_url = imageinfo.get("url")
                    if img_url and not img_url.endswith(".ogv") and not img_url.endswith(".webm"):
                        results.append({
                            "title": page.get("title", "").replace("File:", "").strip(),
                            "image_url": img_url,
                            "thumbnail_url": imageinfo.get("descriptionurl") or img_url,
                            "source_url": imageinfo.get("descriptionurl", "https://commons.wikimedia.org"),
                            "source_domain": "wikimedia.org",
                            "width": imageinfo.get("width"),
                            "height": imageinfo.get("height"),
                            "engine": "Wikimedia Commons Web API"
                        })
        except Exception as err:
            print(f"[Wikimedia API] Exception: {err}")
        return results

    def _search_unsplash_open(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Unsplash Open Photography fallback.
        """
        results = []
        try:
            url = f"https://unsplash.com/napi/search/photos?query={urllib.parse.quote(query)}&per_page={limit}"
            res = requests.get(url, headers=self.headers, timeout=6)
            if res.status_code == 200:
                data = res.json()
                for photo in data.get("results", []):
                    urls = photo.get("urls", {})
                    img_url = urls.get("regular") or urls.get("full")
                    if img_url:
                        results.append({
                            "title": photo.get("alt_description") or photo.get("description") or query,
                            "image_url": img_url,
                            "thumbnail_url": urls.get("small") or img_url,
                            "source_url": photo.get("links", {}).get("html", "https://unsplash.com"),
                            "source_domain": "unsplash.com",
                            "width": photo.get("width"),
                            "height": photo.get("height"),
                            "engine": "Unsplash Photography Web"
                        })
        except Exception as err:
            print(f"[Unsplash Open] Exception: {err}")
        return results

    def _extract_domain(self, url: str) -> str:
        """
        Helper to extract clean domain name from absolute URL.
        """
        if not url or not url.startswith("http"):
            return "web"
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception:
            return "web"
