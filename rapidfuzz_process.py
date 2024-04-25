import sqlite3
from rapidfuzz import fuzz, process

def find_similar_quotes(db_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Fetch all quotes from the database
    cursor.execute("SELECT quote FROM Quotes")
    quotes = [row[0] for row in cursor.fetchall()]

    # Find and print similar quotes
    for i, quote in enumerate(quotes):
        print(f"Quote {i+1}: {quote}")
        similar_quotes = process.extract(quote, quotes, scorer=fuzz.token_sort_ratio)
        similar_quotes = [q for q in similar_quotes if q[1] >= 70]
        if len(similar_quotes) > 1:
            print("Similar quotes:")
            for sq in similar_quotes:
                if sq[0] != quote:
                    print(f"- {sq[0]}")
        print()

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    find_similar_quotes("quotes_data.db")  # Replace with your database file name

