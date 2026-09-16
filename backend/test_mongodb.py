from app.database.mongodb import check_mongodb_connection


if check_mongodb_connection():
    print("MongoDB connection successful!")