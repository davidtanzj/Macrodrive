from db import connect_database

RENAMES = {
    "Bonds & Markets": "Fixed Income & Credit",
    "General Macro & Markets": "Macro & Markets",
}

def main():
    connection = connect_database()
    cursor = connection.cursor()

    try:
        for old_name, new_name in RENAMES.items():
            cursor.execute(
                "SELECT id FROM categories WHERE name = ?",
                (old_name,)
            )
            old_row = cursor.fetchone()

            if not old_row:
                print(f"Not found: {old_name}")
                continue

            cursor.execute(
                "SELECT id FROM categories WHERE name = ?",
                (new_name,)
            )
            new_row = cursor.fetchone()

            if new_row:
                old_id = old_row[0]
                new_id = new_row[0]

                # Merge any links safely if the new category already exists.
                cursor.execute("""
                    INSERT INTO article_categories (article_id, category_id, score)
                    SELECT article_id, ?, score
                    FROM article_categories
                    WHERE category_id = ?
                    ON CONFLICT(article_id, category_id)
                    DO UPDATE SET score = MAX(score, excluded.score)
                """, (new_id, old_id))

                cursor.execute(
                    "DELETE FROM article_categories WHERE category_id = ?",
                    (old_id,)
                )
                cursor.execute(
                    "DELETE FROM categories WHERE id = ?",
                    (old_id,)
                )
                print(f"Merged: {old_name} -> {new_name}")
            else:
                cursor.execute(
                    "UPDATE categories SET name = ? WHERE name = ?",
                    (new_name, old_name)
                )
                print(f"Renamed: {old_name} -> {new_name}")

        connection.commit()
        print("Category rename migration complete.")

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

if __name__ == "__main__":
    main()
