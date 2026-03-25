import pandas as pd
import argparse
import os
import re

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