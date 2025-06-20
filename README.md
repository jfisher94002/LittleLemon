# LittleLemon

## Overview

The Little Lemon API is a Django REST Framework-based backend system designed to streamline restaurant operations. It provides endpoints for managing user roles, menu items, orders, and carts. This API ensures secure role-based access for Customers, Delivery Crew, Managers, and Admins, supporting essential features such as authentication, filtering, sorting, and throttling.

Coursera backend API final project - LittleLemon API
Endpoints provided:
1. User registration and token generation endpoints
2. Category and menu-items endpoints
3. User group management endpoints
4. Cart management endpoints
5. Order management endpoints

## Installation and Setup

#### Prerequisites:

1- Python 3.9+

2- Django 5.1+

3- Django REST Framework

# Activate virtual environment using pipenv

pipenv shell

pipenv install

pipenv install django-extensions

pipenv install djoser

pipenv install djangorestframework

pipenv install djangorestframework.authtoken

2- Install dependencies:

    pip install -r requirements.txt

python3 manage.py makemigrations

python3 manage.py migrate

4- Create a superuser for admin access:

    python manage.py createsuperuser

```sh
Current Users
```

```sh
superuser: 
Jonathan
lemon@123


http://localhost:8000/admin
C1, 5a3edf91008911cffd13270d8e9a38cd97d93317
D1, f24405b9a98e2367a76eef5b34a0d673f47f7135
M1, f8e9a5fb1510970036c2426b6e2d4f894f9593a7
C1, c1@littlelemon.com, lemon@123
D1, d1@littlelemon.com, lemon@123
M1, m1@littlellemon.com, lemon@123
C2, c2@littlelemon.com, lemon@123
C2: f9932c0cda75f7148c3c158cbc4a3a5a66952ae7


```

The API routes are working the same as described in https://www.coursera.org/learn/apis/supplement/Ig5me/project-structure-and-api-routes

5- Start the development server:

    python manage.py runserver

**API Endpoints**

Authentication and User Management

| Endpoint                         | Method | Role  | Description                     |
|----------------------------------|--------|-------|---------------------------------|
| `/api/users/<id>/groups/`          | POST   | Admin | Assign a user to a group        |
| `/api/users/<id>/groups/ `        | DELETE | Admin | Remove a user from a group      |
| `/api/groups/manager/users/`       | GET    | Admin | List all managers               |
| `/api/groups/delivery-crew/users/` | GET    | Admin | List all delivery crew members  |

---

Menu Management

| Endpoint                | Method        | Role     | Description                  |
|-------------------------|---------------|----------|------------------------------|
| `/api/menu-items/`      | GET           | Public   | List all menu items.         |
| `/api/menu-items/`      | POST          | Manager  | Add a new menu item.         |
| `/api/menu-items/<id>/` | GET           | Public   | Retrieve a menu item by ID.  |
| `/api/menu-items/<id>/` | PUT, DELETE   | Manager  | Update or delete a menu item.|
Features:
Filtering and Sorting: Filter by title, price, category, or featured status.

GET /api/menu-items/?category=Beverages&ordering=-price

---

Cart Operations

| Endpoint                                   | Method | Role      | Description                  |
|-------------------------------------------|--------|-----------|------------------------------|
| `/api/users/<id>/cart/menu-item/<menu_id>/`   | POST   | Customer  | Add a menu item to the cart. |
| `/api/users/<id>/cart/menu-item/`             | GET    | Customer  | View all items in the cart.  |
| `/api/users/<id>/cart/`                       | DELETE | Customer  | Clear all items in the cart. |


NOTES

I had some trouble with the POST /api/menu-items call. It took awhile to get the body json correct. Here is what worked for me:

{

    "title": "Spaghetti Carbonara",
    
    "description": "Classic Italian pasta dish with eggs, cheese, pancetta, and pepper.",
    
    "price": 12.99,
	
    "inventory": 100,
    
    "category": {
			
            "category_id": 1
	
    }

}

http://127.0.0.1:8000/api/menu-items/?search=vanilla


Updated with github workflow for building with each PR
