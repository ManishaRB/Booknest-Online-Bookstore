"""
Task 1: Calling a real books API (Open Library)

get_books(subject, page) calls the Open Library search API with requests and
returns a list of book dicts:

    {"title": ..., "author": ..., "first_publish_year": ..., "rating": ...}

Robustness:
  * the request has a timeout (15 seconds)
  * the call is wrapped in try/except, so a failed call never crashes the script
  * if the API cannot be reached, we fall back to offline_books.json

Install once:  pip install requests
Run:           python 01_get_books.py
"""

import json
import os

import requests

BASE = "https://openlibrary.org/search.json"
FIELDS = "title,author_name,first_publish_year,ratings_average,edition_count"
HEADERS = {"User-Agent": "booknest-demo"}
OFFLINE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "offline_books.json")


def clean_book(doc):
    """Turn one raw API record into a tidy dict.
    .get() is used everywhere because some books are missing some fields."""
    authors = doc.get("author_name") or []
    rating = doc.get("ratings_average")
    return {
        "title": doc.get("title", "Unknown title"),
        "author": ", ".join(authors) if authors else "Unknown author",
        "first_publish_year": doc.get("first_publish_year"),
        "rating": round(rating, 2) if isinstance(rating, (int, float)) else None,
    }


def load_offline_books():
    """Local sample, in the same shape the API returns."""
    try:
        with open(OFFLINE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def get_books(subject, page=1, limit=10):
    """Return a list of book dicts for one page of results.

    Never raises: on any failure it prints a friendly note and falls back
    to the offline sample.
    """
    url = f"{BASE}?q={subject}&page={page}&limit={limit}&fields={FIELDS}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()          # turn HTTP 4xx/5xx into an error
        docs = response.json().get("docs", [])
        return [clean_book(d) for d in docs]
    except Exception as err:
        print(f"(API call failed: {type(err).__name__}. Using offline sample.)")
        return [clean_book(d) for d in load_offline_books()[:limit]]


def main():
    subject = "python"
    books = get_books(subject, page=1)

    print(f"Found {len(books)} books for '{subject}' (page 1):\n")
    # Printing few books as mentioned in the task description
    for b in books[:10]:
        print(f"{b['title']:<42} | {b['author']:<28} | "
              f"{b['first_publish_year']} | rating {b['rating']}")


if __name__ == "__main__":
    main()