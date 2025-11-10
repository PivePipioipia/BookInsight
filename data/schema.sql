DROP TABLE IF EXISTS books;

CREATE TABLE books (
    unique_id TEXT PRIMARY KEY,         -- Từ 'parent_asin'
    title TEXT,                         -- Từ 'title_clean'
    author_name TEXT,
    publisher TEXT,
    publication_year REAL,              -- Dùng REAL vì có giá trị NaN/NULL
    main_category TEXT,                 -- Từ 'main_category_clean'
    categories TEXT,                    -- Từ 'categories_clean'
    book_format TEXT,
    language TEXT,
    page_count REAL,                    -- Dùng REAL vì có giá trị NaN/NULL
    isbn_13 TEXT,
    price REAL,                         -- Từ 'price_temp_clean'
    average_rating REAL,                -- Từ 'average_rating_clean'
    rating_number INTEGER,              -- Từ 'rating_number_clean'
    main_images TEXT,                   -- Link ảnh bìa
    author_avatar TEXT                  -- Link ảnh tác giả
);


CREATE INDEX IF NOT EXISTS idx_author ON books(author_name);
CREATE INDEX IF NOT EXISTS idx_publisher ON books(publisher);
CREATE INDEX IF NOT EXISTS idx_main_category ON books(main_category);
CREATE INDEX IF NOT EXISTS idx_rating ON books(average_rating DESC); -- Sắp xếp giảm dần
CREATE INDEX IF NOT EXISTS idx_price ON books(price);
CREATE INDEX IF NOT EXISTS idx_pub_year ON books(publication_year);