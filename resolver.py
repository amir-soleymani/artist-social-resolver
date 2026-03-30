import pandas as pd
import argparse
import os
import re
import time
from urlib.parse import quote_plus
import requests
from typing import List, Dict, Optional

# Constants for MusicBrainz
MUSICBRAINZ_BASE = "https://musicbrainz.org/ws/2"
MB_HEADERS = {
    "User_Agent": "ArtistSocialMediaResolver/1.0 (local-script)"
}
    
def normalize_whitespace(s: str) -> str:
    """Collapses multiple spaces and removes leading/trailing whitespace."""
    return re.sub(r"\s+", " ", (s or "")).strip()

def normalize_spotify_link(raw: str) -> str:
    """Extracts Spotify ID and returns the canonical URL format."""
    if raw is None:
        return ""
    s = str(raw).strip()
    if not s:
        return ""

    # This pattern matches 'spotify:artist:ID' or 'open.spotify.com/artist/ID'
    m = re.search(r"artist/([A-Za-z0-9]{22})|artist:([A-Za-z0-9]{22})", s)
    if m:
        # Use whichever group (1 or 2) captured the 22-character ID
        artist_id = m.group(1) or m.group(2)
        return f"https://open.spotify.com/artist/{artist_id}"

    return s

def normalize_instagram_id(raw: str) -> str:
    """Turns input into a clean Instagram handle (no @, no URL parts)."""
    if raw is None:
        return ""
    s = str(raw).strip()
    if not s:
        return ""

    # Remove hidden characters and URL parameters
    s = s.replace("\ufeff", "")
    s = s.split("?")[0].split("#")[0].strip()
    s = s.strip("/")

    if s.startswith("@"):
        s = s[1:]

    # If it's a full URL, take the last path segment (the handle)
    m = re.search(r"instagram\.com/([^/]+)", s)
    if m:
        s = m.group(1)

    return s

def search_duckduckgo_html(query: str, num: int = 5) -> List[Dict]:
    """
    Performs a search on DuckDuckGo and scrapes the HTML for links and titles.
    """
    # Use quote_plus to make the name safe for a URL
    ddg_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    headers = {"User_Agent": "Mozilla/5.0"}

    try: 
        r = requests.get(ddg_url, headers=headers, timeout=15)
        r.raise_for_status()
        html = r.text

        results = []
        
        # This Regex finds result links and titles in the DuckDuckGo HTML
        pattern = re.compile(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', flags=re.S)

        for m in pattern.finditer(html):
            link = m.group(1)
            title = re.sub(r"<.*?>", "", m.group(2)).strip()
            results.append({"link": link, "title": title})
            if len(results) >= num:
                break
        return results
    except Exception as e:
        print(f"Search failed for {query}: {e}")
        return []
    
def pick_best_link(artist_name: str, platform: srt, candidates: List[Dict]) -> str:
    """
    Simple logic to pick the link most likely to be the correct profile
    """
    for item in candidates:
        url = item['link'].lower()
        # If the platform name (e.g., soundcloud) is in the URL, it's a good candidate
        if platform.lower() in url:
            return item['link']
    return ""

def domain_of (url: str) -> str:
    """Extracts the domain from a URL to help categorize links."""
    try:
        from urlib.parse import urlparse
        return (urlparse(url).netloc or "").lower().replace("www.", "")
    except Exception:
        return ""
    
def musicbrainz_lookup_artist(artist_name: str, spotify_link: str) -> dict:
    if not artist_name:
        return {}
    
    try:
        q = quote_plus(f'artist:"{artist_name}"')
        url = f"{MUSICBRAINZ_BASE}/artist?query={q}&fmt=json&limit=8"
        r = requests.get(url, headers=MB_HEADERS, timeout=25)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return {}
    
    artists = data.get("artists") or []
    if not artists:
        return {}
    
    # For now, we take the top match from MusicBrainz
    candidate = artists[0]
    mbid = candidate.get("id")

    try:
        detail_url = f"{MUSICBRAINZ_BASE}/artist/{mbid}?inc=url-rels+isnis&fmt=json"
        dr = requests.get(detail_url, headers=MB_HEADERS, timeout=25)
        dr.raise_for_status()
        detail = dr.json()
    except Exception:
        return {}
    
    links = {}
    for rel in detail.get("relations") or []:
        rel_url = ((rel.get("url") or {}).get("resource")) or ""
        if not rel_url:
            continue
        d = domain_of(rel_url)
        if "spotify.com" in d:
            links["spotify"] = rel_url
        elif "instagram.com" in d:
            links["instagram"] = rel_url
        # ("I'll add other platforms later if needed")

    isni_list = detail.get("isnis") or []
    return {
        "mbid": mbid,
        "name": detail.get("name") or artist_name,
        "isni": isni_list[0] if isni_list else "",
        "links": links,
    }
    

def main():
    parser = argparse.ArgumentParser(description="Artist Social Media Resolver")
    parser.add_argument("input", help="Input .xlsx file")
    parser.add_argument("output", help="Output .xlsx file")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: {args.input} not found.")
        return

    try:
        # Load the Excel file
        df = pd.read_excel(args.input)
        
        # This ensures ' artist_name ' becomes 'artist_name'
        df.columns = [str(col).strip() for col in df.columns]
        print(f"System sees these columns: {list(df.columns)}")

        print("Cleaning data...")
        
        if 'artist_name' in df.columns:
            df['artist_name'] = df['artist_name'].apply(normalize_whitespace)
        
        if 'spotify_link' in df.columns:
            df['spotify_link'] = df['spotify_link'].apply(normalize_spotify_link)
            
        if 'instagram_id' in df.columns:
            df['instagram_id'] = df['instagram_id'].apply(normalize_instagram_id)

        print("Enriching data with MusicBrainz...")
        mbids = []
        isnis = []

        for index, row in df.iterrows():
            artist_name = row.get('artist_name', '')
            spotify_link = row.get('spotify_link' '')
            mb_identity = musicbrainz_lookup_artist(artist_name, spotify_link)
            mbids.append(mb_identity.get("mbid", ""))
            isnis.append(mb_identity.get("isni", ""))

            time.sleep(1.0)

        df['mbid'] = mbids
        df['isni'] = isnis

        # Print the first row to our terminal so we can see the change immediately
        print("\nVerification (First Row Result):")
        print(df.iloc[0].to_dict())

        # Save the result
        df.to_excel(args.output, index=False)
        print(f"\nSuccess! Cleaned data saved to {args.output}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()