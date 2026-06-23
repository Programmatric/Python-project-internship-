"""
Task 2: API Integration & JSON Handling
Internship Project - Python Fundamentals
Author: [Your Name]
API Used: GitHub Search API (https://api.github.com) — Free, no key required
Description: Fetches repository data, parses JSON, applies filtering/search,
             handles API errors gracefully.
"""

import requests
import json
import time
from datetime import datetime

# ─── Constants ────────────────────────────────────────────────────────────────
BASE_URL = "https://api.github.com/search/repositories"
HEADERS = {
    "User-Agent": "intern-api-project",       # GitHub requires a User-Agent header
    "Accept": "application/vnd.github.v3+json"
}


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: FETCH DATA FROM API
# ══════════════════════════════════════════════════════════════════════════════

def fetch_repositories(query: str, sort: str = "stars", per_page: int = 20) -> list[dict] | None:
    """
    Fetches repositories from GitHub Search API.

    Args:
        query    : Search keyword (e.g. "python machine learning")
        sort     : Sort by 'stars', 'forks', or 'updated'
        per_page : Number of results to fetch (max 100)

    Returns:
        List of repository dicts, or None on failure.
    """
    params = {
        "q": query,
        "sort": sort,
        "order": "desc",
        "per_page": per_page
    }

    print(f"\n[API] Fetching repos for query: '{query}' ...")

    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)

        # ── Check for HTTP errors (4xx, 5xx) ──────────────────
        response.raise_for_status()

        # ── Parse JSON response ───────────────────────────────
        data = response.json()

        # GitHub returns results inside 'items' key
        repos = data.get("items", [])
        total = data.get("total_count", 0)

        print(f"[API] Success! Total matching repos: {total:,} | Fetched: {len(repos)}")
        return repos

    except requests.exceptions.ConnectionError:
        print("[ERROR] No internet connection. Please check your network.")
        return None

    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out after 10 seconds.")
        return None

    except requests.exceptions.HTTPError as e:
        # Handle specific HTTP status codes
        status = response.status_code
        if status == 403:
            print(f"[ERROR] 403 Forbidden — GitHub rate limit hit. Wait 60 seconds.")
        elif status == 422:
            print(f"[ERROR] 422 Unprocessable — Invalid query parameters.")
        elif status == 503:
            print(f"[ERROR] 503 Service Unavailable — GitHub is down.")
        else:
            print(f"[ERROR] HTTP Error {status}: {e}")
        return None

    except requests.exceptions.RequestException as e:
        # Catch-all for any other requests-related error
        print(f"[ERROR] Request failed: {e}")
        return None

    except json.JSONDecodeError:
        print("[ERROR] Failed to parse API response as JSON.")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: PARSE & EXTRACT USEFUL FIELDS FROM JSON
# ══════════════════════════════════════════════════════════════════════════════

def parse_repo(repo: dict) -> dict:
    """
    Extracts only the relevant fields from a raw GitHub repo JSON object.
    Raw API response has 80+ fields — we pick what matters.
    """
    return {
        "name":        repo.get("name", "N/A"),
        "owner":       repo.get("owner", {}).get("login", "N/A"),  # nested JSON access
        "description": repo.get("description") or "No description",
        "language":    repo.get("language") or "Not specified",
        "stars":       repo.get("stargazers_count", 0),
        "forks":       repo.get("forks_count", 0),
        "open_issues": repo.get("open_issues_count", 0),
        "url":         repo.get("html_url", ""),
        "created_at":  repo.get("created_at", "")[:10],  # trim to YYYY-MM-DD
        "updated_at":  repo.get("updated_at", "")[:10],
    }


def parse_all(repos: list[dict]) -> list[dict]:
    """Parses a list of raw repo dicts into clean, reduced dicts."""
    return [parse_repo(r) for r in repos]


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3: FILTERING & SEARCH LOGIC
# ══════════════════════════════════════════════════════════════════════════════

def filter_by_stars(repos: list[dict], min_stars: int) -> list[dict]:
    """Returns repos with star count >= min_stars."""
    return [r for r in repos if r["stars"] >= min_stars]


def filter_by_language(repos: list[dict], language: str) -> list[dict]:
    """Returns repos matching a specific programming language (case-insensitive)."""
    return [r for r in repos if r["language"].lower() == language.lower()]


def search_by_keyword(repos: list[dict], keyword: str) -> list[dict]:
    """
    Searches name + description fields for a keyword (case-insensitive).
    Useful for narrowing results after a broad API fetch.
    """
    keyword = keyword.lower()
    return [
        r for r in repos
        if keyword in r["name"].lower() or keyword in r["description"].lower()
    ]


def sort_repos(repos: list[dict], key: str = "stars", reverse: bool = True) -> list[dict]:
    """Sorts repo list by a given field. Default: descending by stars."""
    return sorted(repos, key=lambda r: r.get(key, 0), reverse=reverse)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4: DISPLAY HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def display_repos(repos: list[dict], title: str = "Results", limit: int = 10):
    """Pretty-prints a list of parsed repos in a table format."""
    print(f"\n{'='*65}")
    print(f"  {title}  ({len(repos)} repos)")
    print(f"{'='*65}")

    if not repos:
        print("  No repositories found for this filter.")
        return

    for i, r in enumerate(repos[:limit], 1):
        print(f"\n  [{i}] {r['owner']}/{r['name']}")
        print(f"       Language : {r['language']}")
        print(f"       Stars    : {r['stars']:,}   Forks: {r['forks']:,}   Issues: {r['open_issues']}")
        print(f"       Updated  : {r['updated_at']}")
        print(f"       Desc     : {r['description'][:80]}...")
        print(f"       URL      : {r['url']}")


def display_summary(repos: list[dict]):
    """Prints aggregated stats — like a mini analytics report."""
    if not repos:
        print("No data to summarize.")
        return

    total_stars  = sum(r["stars"] for r in repos)
    total_forks  = sum(r["forks"] for r in repos)
    avg_stars    = total_stars // len(repos)
    top_repo     = max(repos, key=lambda r: r["stars"])

    # Count repos per language
    lang_count = {}
    for r in repos:
        lang = r["language"]
        lang_count[lang] = lang_count.get(lang, 0) + 1

    top_lang = max(lang_count, key=lang_count.get)

    print(f"\n{'='*65}")
    print(f"  SUMMARY STATISTICS ({len(repos)} repos)")
    print(f"{'='*65}")
    print(f"  Total Stars     : {total_stars:,}")
    print(f"  Total Forks     : {total_forks:,}")
    print(f"  Average Stars   : {avg_stars:,}")
    print(f"  Top Repo        : {top_repo['owner']}/{top_repo['name']} ({top_repo['stars']:,} ⭐)")
    print(f"  Top Language    : {top_lang} ({lang_count[top_lang]} repos)")
    print(f"\n  Language Breakdown:")
    for lang, count in sorted(lang_count.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"    {lang:<20} {bar} ({count})")


def save_to_json(repos: list[dict], filepath: str):
    """Saves parsed repo list to a JSON file for documentation."""
    try:
        with open(filepath, "w") as f:
            json.dump(repos, f, indent=2)
        print(f"\n[SAVED] Output saved to: {filepath}")
    except IOError as e:
        print(f"[ERROR] Could not save JSON: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN — DEMO RUN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "="*65)
    print("  TASK 2: API Integration & JSON Handling")
    print("  API: GitHub Search API | No auth required")
    print("="*65)

    # ── Step 1: Fetch repos for a topic ───────────────────────
    raw_repos = fetch_repositories(query="data analysis python", per_page=30)

    if raw_repos is None:
        print("\n[ABORT] API fetch failed. Cannot continue.")
        return

    # ── Step 2: Parse JSON — extract only needed fields ───────
    print("\n>>> Step 2: Parsing JSON response...")
    repos = parse_all(raw_repos)
    print(f"Parsed {len(repos)} repos. Sample keys: {list(repos[0].keys())}")

    # ── Step 3: Display top 5 raw results ─────────────────────
    display_repos(repos, title="Top Repos by Stars (All Languages)", limit=5)

    # ── Step 4: Filter by minimum stars ───────────────────────
    print("\n>>> Step 4: Filtering repos with 10,000+ stars...")
    popular = filter_by_stars(repos, min_stars=10000)
    display_repos(popular, title="Popular Repos (10k+ Stars)", limit=5)

    # ── Step 5: Filter by language ────────────────────────────
    print("\n>>> Step 5: Filtering Python-only repos...")
    python_repos = filter_by_language(repos, language="Python")
    display_repos(python_repos, title="Python Repos Only", limit=5)

    # ── Step 6: Keyword search in name/description ────────────
    print("\n>>> Step 6: Searching for 'pandas' in name/description...")
    pandas_repos = search_by_keyword(repos, keyword="pandas")
    display_repos(pandas_repos, title="Repos mentioning 'pandas'", limit=5)

    # ── Step 7: Summary stats ─────────────────────────────────
    print("\n>>> Step 7: Summary statistics...")
    display_summary(repos)

    # ── Step 8: Save output to JSON file ──────────────────────
    print("\n>>> Step 8: Saving results to JSON...")
    save_to_json(repos, "github_results.json")

    # ── Step 9: Simulate API error handling ───────────────────
    print("\n>>> Step 9: Testing error handling (bad query)...")
    bad_result = fetch_repositories(query="", per_page=5)
    if bad_result is None:
        print("Error handled gracefully — returned None.")

    print("\n" + "="*65)
    print("  Task 2 Complete!")
    print("="*65 + "\n")


if __name__ == "__main__":
    main()
