#!/usr/bin/env python3
"""Print a bookstore inventory report by joining authors to books in MongoDB Atlas."""

import logging
import os
import sys

from pymongo import MongoClient
from pymongo.errors import PyMongoError

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# Credentials come from the environment, not from this file.
MONGODB_ATLAS_URL = os.getenv("MONGODB_ATLAS_URL")
MONGODB_ATLAS_USER = os.getenv("MONGODB_ATLAS_USER")
MONGODB_ATLAS_PWD = os.getenv("MONGODB_ATLAS_PWD")

# Mix loaded authors (Gaiman, Pratchett) with the author added in Case Study 1.
AUTHOR_IDS = ["author_002", "author_003", "author_004"]


def require_credentials() -> None:
    """Exit if any Atlas environment variable is missing."""
    missing = [
        name
        for name, value in (
            ("MONGODB_ATLAS_URL", MONGODB_ATLAS_URL),
            ("MONGODB_ATLAS_USER", MONGODB_ATLAS_USER),
            ("MONGODB_ATLAS_PWD", MONGODB_ATLAS_PWD),
        )
        if not value
    ]
    if missing:
        log.error("Missing environment variables: %s", ", ".join(missing))
        sys.exit(1)


def print_author_report(authors, books, author_ids: list[str]) -> None:
    """Print each author's name and the title/year of books linked by author_ids."""
    author_count = authors.count_documents({"_id": {"$in": author_ids}})
    print(f"Authors: {author_count}")
    print()

    for author_id in author_ids:
        author = authors.find_one({"_id": author_id})
        if author is None:
            log.warning("No author document for %s", author_id)
            continue

        print(author["name"])
        # A book matches when this author's _id appears in author_ids.
        for book in books.find({"author_ids": author["_id"]}):
            print(f"  {book['title']} ({book['published_year']})")
        print()


def main() -> None:
    """Connect to Atlas, print the joined bookstore report, and close the client."""
    require_credentials()

    client = None
    try:
        client = MongoClient(
            MONGODB_ATLAS_URL,
            username=MONGODB_ATLAS_USER,
            password=MONGODB_ATLAS_PWD,
        )
        # Force a round trip so a bad URL or password fails here, not later.
        client.admin.command("ping")
        log.info("Connected to MongoDB Atlas")

        db = client.bookstore
        authors = db.authors
        books = db.books
        print_author_report(authors, books, AUTHOR_IDS)
        sys.stdout.flush()
    except PyMongoError:
        log.exception("Could not query the bookstore database")
        sys.exit(1)
    finally:
        if client is not None:
            client.close()
            log.info("Closed MongoDB client")


if __name__ == "__main__":
    main()
