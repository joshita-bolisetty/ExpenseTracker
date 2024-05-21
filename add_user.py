import sqlite3
conn = sqlite3.connect("expense_tracker.db")
conn.execute("""
                            create table if not exists User(
                                userid integer primary key autoincrement,
                                username text not null,
                                password text not null
                            )"""
        )
conn.execute(
            """
                            
                            CREATE TABLE IF NOT EXISTS expenses (
                                user TEXT NOT NULL,
                                id INTEGER PRIMARY KEY autoincrement,
                                category TEXT NOT NULL,
                                name TEXT not null,
                                amount REAL NOT NULL,
                                date DATE NOT NULL
                                
                            )
        """
        )
conn.execute(
            "INSERT INTO User (username,password) VALUES (?,?)", ("Admin", "123")
        )
conn.commit()
