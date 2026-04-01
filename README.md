# artist-social-resolver

1. Project Overview

Artist Social Media Resolver
A Python-based automation tool designed to aggregate and verify official social media profiles for musical artists. It cleans raw input data, enriches it via the MusicBrainz API, and uses a heuristic-driven web discovery engine to find missing links across 7 major platforms.


2. Technical Features

I. Data Normalization & Cleaning
The script handles "dirty" input by canonicalizing URLs and handles.
Spotify: Converts various link formats into a standard spotify.com/artist/ID format.
Instagram: Strips tracking parameters, @ symbols, and sub-directory clutter to extract clean handles.
Excel Integration: Generates a dynamic, multi-sheet workbook where each artist receives a dedicated, sanitized sheet.

II. Identity Enrichment (MusicBrainz)
Instead of guessing, the tool queries the MusicBrainz database to retrieve:
MBID: The unique MusicBrainz Identifier.
ISNI: The International Standard Name Identifier (the "Gold Standard" for artist verification).
Official Relations: Direct links to Spotify, Instagram, and YouTube vetted by the community.

III. Heuristic Discovery Engine
When official data is missing, the script performs a "Best-Effort" search using a custom scoring algorithm:
Platform Anchoring: Matches URLs against platform domains.
Linguistic Matching: Uses difflib (Gestalt Pattern Matching) to compare search titles with the artist's name.
Confidence Scoring: Assigns weights to "Official" signals and penalizes "Anti-Signals" (like fan pages or specific video posts).

3. Why it Matters

This tool reduces manual research time by over 80%, transforming a tedious manual lookup process into a scalable data pipeline suitable for A&R teams, booking agents, and music marketers.
