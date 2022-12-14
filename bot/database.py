import sqlite3


def create_db():
    database = sqlite3.connect('wallpapers.db')
    cursor = database.cursor()
    cursor.executescript('''  
    CREATE TABLE IF NOT EXISTS categories(
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name VARCHAR(20) UNIQUE
    );
    CREATE TABLE IF NOT EXISTS images(
        image_id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_link TEXT UNIQUE,
        category_id INTEGER REFERENCES categories(category_id) 
    );
    ''')
    database.commit()
    database.close()


# create_db()

def insert_or_ignore(true_name):
    database = sqlite3.connect('wallpapers.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT OR IGNORE INTO categories(category_name) VALUES (?)
    ''', (true_name,))
    database.commit()

    cursor.execute('''
    SELECT category_id FROM categories WHERE category_name = ?
    ''', (true_name,))
    category_id = cursor.fetchone()[0]
    database.close()
    return category_id


def save_to_db(image_link, category_id):
    database = sqlite3.connect('wallpapers.db')
    cursor = database.cursor()
    cursor.execute('''
    INSERT OR IGNORE INTO images(image_link, category_id) VALUES (?, ?);
    ''', (image_link, category_id))
    database.commit()
    database.close()

