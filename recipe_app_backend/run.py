from app import app

if __name__ == "__main__":
    # Bind to 0.0.0.0 so it is accessible from container port mapping, use port 3001
    app.run(host="0.0.0.0", port=3001, debug=False)
