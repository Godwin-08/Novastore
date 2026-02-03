from novastore import create_app

# Backwards-compatible app instance for imports
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)