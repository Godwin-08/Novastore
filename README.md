# 🛍️ Novastore — E-Commerce Platform (Python OOP Project)

**Novastore** is a web-based e-commerce application developed using **Python (Object-Oriented Programming)** and **Flask**.  
The project demonstrates how core OOP principles can be applied within a modern web architecture.

---

## 🧬 Object-Oriented Programming Concepts

This project is built on a well-structured object-oriented design, mainly located in  
`novastore/models.py` and `novastore/poo_classes.py`.

- **Encapsulation**: Secure management of user data and product attributes
- **Abstraction**: Real-world entities (User, Product, Order) modeled as Python classes
- **Object Persistence**: SQLAlchemy ORM used to map OOP objects to a relational database
- **Business Logic**: Class methods handling cart validation, stock management, and order total calculation

---

## 🚀 Features

- User management (registration, authentication, sessions)
- Product catalog with category filtering and search
- Dynamic shopping cart system (API-based interactions)
- Order processing and invoice generation
- Admin dashboard with full CRUD operations

---

## 🏗️ Project Structure

```text
novastore/
├── app.py                 # Flask application entry point
├── run.py                 # Application launcher
├── novastore/
│   ├── models.py          # ORM-based OOP models (SQLAlchemy)
│   ├── poo_classes.py     # Core business logic
│   └── routes/            # Flask Blueprints (controllers)
├── templates/             # Jinja2 templates
├── static/                # CSS, JS, assets
└── scripts/               # Database seeding scripts

```
🧰 Tech Stack

- Language: Python 3
- Framework: Flask
- ORM: SQLAlchemy
- Database: SQLite / MySQL
- Frontend: HTML5, CSS3, JavaScript (Jinja2)
```

⚙️ Installation
git clone [https://github.com/Godwin-08/Novastore.git](https://github.com/Godwin-08/Novastore.git)
cd Novastore

# Create and activate virtual environment
python -m venv venv
# Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate

# Install dependencies and launch
pip install -r requirements.txt
python run.py

```

Application available at:
👉 http://127.0.0.1:5000

```
👥 Team

Computer Science & Data Engineering (IID)

- Azeddine Maktou
- Othmane Laaouina
- Godwin Elie Nougbolo
- Mariam M’barki
- Kawtar Mahboub El Idrissi
```
