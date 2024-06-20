from fingerNotes import app, db

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"An error occurred while creating database tables: {e}")


if __name__ == "__main__":
    app.run(debug=True)