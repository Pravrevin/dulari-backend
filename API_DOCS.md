# Dulari Medical Store — API Documentation

**Base URL:** `http://localhost:8000`  
**Content-Type:** `application/json`  
**Auth Header:** `Authorization: Bearer <access_token>` (required on protected routes)

---

## Table of Contents

1. [Authentication](#1-authentication)
   - [Signup](#11-signup)
   - [Login](#12-login)
   - [Logout](#13-logout)
   - [Refresh Token](#14-refresh-token)
   - [Forgot Password](#15-forgot-password)
   - [Reset Password](#16-reset-password)
2. [Profile](#2-profile)
   - [Get Profile](#21-get-profile)
   - [Update Profile](#22-update-profile)
   - [Change Password](#23-change-password)
3. [Products](#3-products)
   - [List Categories](#31-list-categories)
   - [List Products](#32-list-products)
   - [Product Detail](#33-product-detail)
   - [New Launches](#34-new-launches)
   - [Trending Near You](#35-trending-near-you)
   - [In the Spotlight](#36-in-the-spotlight)
4. [Cart](#4-cart)
   - [Get Cart](#41-get-cart)
   - [Add to Cart](#42-add-to-cart)
   - [Update Cart Item](#43-update-cart-item)
   - [Remove Cart Item](#44-remove-cart-item)
5. [Wishlist](#5-wishlist)
   - [Get Wishlist](#51-get-wishlist)
   - [Add to Wishlist](#52-add-to-wishlist)
   - [Remove from Wishlist](#53-remove-from-wishlist)
6. [Orders](#6-orders)
   - [Place Order](#61-place-order)
   - [List Orders](#62-list-orders)
   - [Order Detail](#63-order-detail)
   - [Cancel Order](#64-cancel-order)

---

## 1. Authentication

### 1.1 Signup

**POST** `/api/auth/signup/`

Register a new user. Either `email` or `mobile` is required (both can be provided).

**Request Body:**
```json
{
  "name": "Raj Sharma",
  "email": "raj@example.com",
  "mobile": "9876543210",
  "password": "secret123"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | Yes | Full name |
| `email` | string | One of email/mobile | Valid email address |
| `mobile` | string | One of email/mobile | 10-digit Indian number (starts with 6-9) |
| `password` | string | Yes | Minimum 6 characters |

**Response — 201 Created:**
```json
{
  "message": "Account created successfully.",
  "user": {
    "id": 1,
    "name": "Raj Sharma",
    "email": "raj@example.com",
    "mobile": "9876543210"
  }
}
```

**Response — 400 Bad Request:**
```json
{
  "email": ["user with this email already exists."]
}
```

---

### 1.2 Login

**POST** `/api/auth/login/`

Login using email OR mobile number with password.

**Request Body (via email):**
```json
{
  "email": "raj@example.com",
  "password": "secret123"
}
```

**Request Body (via mobile):**
```json
{
  "mobile": "9876543210",
  "password": "secret123"
}
```

**Response — 200 OK:**
```json
{
  "message": "Login successful.",
  "user": {
    "id": 1,
    "name": "Raj Sharma",
    "email": "raj@example.com",
    "mobile": "9876543210"
  },
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

> Access token expires in **1 day**. Refresh token expires in **30 days**.

**Response — 400 Bad Request:**
```json
{
  "non_field_errors": ["No account found with this email."]
}
```

---

### 1.3 Logout

**POST** `/api/auth/logout/` 🔒

Blacklists the refresh token so it can no longer be used.

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response — 200 OK:**
```json
{
  "message": "Logged out successfully."
}
```

**Response — 400 Bad Request:**
```json
{
  "error": "Invalid or expired token."
}
```

---

### 1.4 Refresh Token

**POST** `/api/auth/token/refresh/`

Get a new access token using the refresh token.

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response — 200 OK:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 1.5 Forgot Password

**POST** `/api/auth/forgot-password/`

Generates a password reset token. In production this token is sent via email/SMS.

**Request Body (via email):**
```json
{
  "email": "raj@example.com"
}
```

**Request Body (via mobile):**
```json
{
  "mobile": "9876543210"
}
```

**Response — 200 OK:**
```json
{
  "message": "Password reset token generated.",
  "reset_token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
  "note": "In production this token is sent via email/SMS. Use it in /reset-password/."
}
```

> Token expires in **15 minutes**.

**Response — 400 Bad Request:**
```json
{
  "non_field_errors": ["No account found."]
}
```

---

### 1.6 Reset Password

**POST** `/api/auth/reset-password/`

Reset password using the token received from forgot-password.

**Request Body:**
```json
{
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
  "new_password": "newSecret456"
}
```

**Response — 200 OK:**
```json
{
  "message": "Password reset successfully. Please login again."
}
```

**Response — 400 Bad Request:**
```json
{
  "token": ["Invalid reset token."]
}
```

---

## 2. Profile

### 2.1 Get Profile

**GET** `/api/auth/profile/` 🔒

**Response — 200 OK:**
```json
{
  "id": 1,
  "name": "Raj Sharma",
  "email": "raj@example.com",
  "mobile": "9876543210",
  "date_joined": "2026-04-10T10:30:00.000000+05:30"
}
```

---

### 2.2 Update Profile

**PATCH** `/api/auth/profile/` 🔒

Send only the fields you want to update.

**Request Body:**
```json
{
  "name": "Raj Kumar Sharma",
  "mobile": "9123456780"
}
```

**Response — 200 OK:**
```json
{
  "message": "Profile updated.",
  "user": {
    "id": 1,
    "name": "Raj Kumar Sharma",
    "email": "raj@example.com",
    "mobile": "9123456780",
    "date_joined": "2026-04-10T10:30:00.000000+05:30"
  }
}
```

**Response — 400 Bad Request:**
```json
{
  "mobile": ["This mobile number is already in use."]
}
```

---

### 2.3 Change Password

**POST** `/api/auth/profile/change-password/` 🔒

**Request Body:**
```json
{
  "old_password": "secret123",
  "new_password": "newSecret456"
}
```

**Response — 200 OK:**
```json
{
  "message": "Password changed successfully. Please login again."
}
```

**Response — 400 Bad Request:**
```json
{
  "old_password": ["Current password is incorrect."]
}
```

---

## 3. Products

### 3.1 List Categories

**GET** `/api/categories/`

**Response — 200 OK:**
```json
[
  {
    "id": 1,
    "name": "Antibiotics",
    "description": "Medicines used to treat bacterial infections"
  },
  {
    "id": 2,
    "name": "Vitamins & Supplements",
    "description": ""
  }
]
```

---

### 3.2 List Products

**GET** `/api/products/`

**Query Parameters:**

| Param | Type | Example | Description |
|---|---|---|---|
| `page` | integer | `?page=2` | Page number (20 items per page) |
| `search` | string | `?search=paracetamol` | Search by name, manufacturer, composition |
| `category_id` | integer | `?category_id=1` | Filter by category |
| `is_new_launch` | boolean | `?is_new_launch=true` | Filter new launches |
| `is_trending_near_you` | boolean | `?is_trending_near_you=true` | Filter trending products |
| `is_in_spotlight` | boolean | `?is_in_spotlight=true` | Filter spotlight products |
| `is_discontinued` | boolean | `?is_discontinued=false` | Filter by discontinued status |
| `ordering` | string | `?ordering=mrp` or `?ordering=-mrp` | Sort by `product_name` or `mrp` |

**Response — 200 OK:**
```json
{
  "count": 500,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [
    {
      "product_id": 101,
      "product_name": "Paracetamol 500mg",
      "mrp": 25.50,
      "is_discontinued": false,
      "manufacturer_name": "Sun Pharma",
      "pack_size_label": "Strip of 10 Tablets",
      "short_composition1": "Paracetamol (500mg)",
      "short_composition2": "",
      "category": {
        "id": 3,
        "name": "Pain Relief",
        "description": ""
      },
      "is_new_launch": false,
      "is_trending_near_you": true,
      "is_in_spotlight": false,
      "images": [
        {
          "id": 1,
          "image": "http://localhost:8000/media/products/paracetamol.jpg",
          "alt_text": "Paracetamol 500mg"
        }
      ]
    }
  ]
}
```

---

### 3.3 Product Detail

**GET** `/api/products/<product_id>/`

**Example:** `GET /api/products/101/`

**Response — 200 OK:**
```json
{
  "product_id": 101,
  "product_name": "Paracetamol 500mg",
  "mrp": 25.50,
  "is_discontinued": false,
  "manufacturer_name": "Sun Pharma",
  "pack_size_label": "Strip of 10 Tablets",
  "short_composition1": "Paracetamol (500mg)",
  "short_composition2": "",
  "category": {
    "id": 3,
    "name": "Pain Relief",
    "description": ""
  },
  "is_new_launch": false,
  "is_trending_near_you": true,
  "is_in_spotlight": false,
  "images": [
    {
      "id": 1,
      "image": "http://localhost:8000/media/products/paracetamol.jpg",
      "alt_text": "Paracetamol 500mg"
    }
  ]
}
```

**Response — 404 Not Found:**
```json
{
  "detail": "Not found."
}
```
hello world def prodyuct heleoe 
---

### 3.4 New Launches

**GET** `/api/products/new-launches/`

Returns all products marked as new launches (no pagination).

**Response — 200 OK:**
```json
[
  {
    "product_id": 205,
    "product_name": "Vitamin D3 60000 IU",
    "mrp": 120.00,
    "is_discontinued": false,
    "manufacturer_name": "Cipla",
    "pack_size_label": "Strip of 4 Capsules",
    "short_composition1": "Cholecalciferol (60000IU)",
    "short_composition2": "",
    "category": { "id": 2, "name": "Vitamins & Supplements", "description": "" },
    "is_new_launch": true,
    "is_trending_near_you": false,
    "is_in_spotlight": false,
    "images": []
  }
]
```

---

### 3.5 Trending Near You

**GET** `/api/products/trending-near-you/`

Returns all products marked as trending (no pagination).

**Response — 200 OK:** *(same structure as New Launches)*

---

### 3.6 In the Spotlight

**GET** `/api/products/in-the-spotlight/`

Returns all products marked as in the spotlight (no pagination).

**Response — 200 OK:** *(same structure as New Launches)*

---

## 4. Cart

### 4.1 Get Cart

**GET** `/api/auth/cart/` 🔒

**Response — 200 OK:**
```json
{
  "count": 2,
  "cart": [
    {
      "id": 1,
      "product": {
        "product_id": 101,
        "product_name": "Paracetamol 500mg",
        "mrp": 25.50,
        "manufacturer_name": "Sun Pharma",
        "pack_size_label": "Strip of 10 Tablets"
      },
      "quantity": 2,
      "added_at": "2026-04-10T11:00:00.000000+05:30"
    },
    {
      "id": 2,
      "product": {
        "product_id": 205,
        "product_name": "Vitamin D3 60000 IU",
        "mrp": 120.00,
        "manufacturer_name": "Cipla",
        "pack_size_label": "Strip of 4 Capsules"
      },
      "quantity": 1,
      "added_at": "2026-04-10T11:05:00.000000+05:30"
    }
  ]
}
```

---

### 4.2 Add to Cart

**POST** `/api/auth/cart/` 🔒

If the product is already in the cart, the quantity is **added** to the existing quantity.

**Request Body:**
```json
{
  "product_id": 101,
  "quantity": 2
}
```

**Response — 201 Created** (new item):
```json
{
  "message": "Added to cart.",
  "item": {
    "id": 1,
    "product": {
      "product_id": 101,
      "product_name": "Paracetamol 500mg",
      "mrp": 25.50,
      "manufacturer_name": "Sun Pharma",
      "pack_size_label": "Strip of 10 Tablets"
    },
    "quantity": 2,
    "added_at": "2026-04-10T11:00:00.000000+05:30"
  }
}
```

**Response — 200 OK** (product already existed, quantity incremented):
```json
{
  "message": "Quantity updated.",
  "item": {
    "id": 1,
    "product": { "product_id": 101, "product_name": "Paracetamol 500mg", "mrp": 25.50, "manufacturer_name": "Sun Pharma", "pack_size_label": "Strip of 10 Tablets" },
    "quantity": 4,
    "added_at": "2026-04-10T11:00:00.000000+05:30"
  }
}
```

**Response — 400 Bad Request:**
```json
{
  "product_id": ["Product not found."]
}
```

---

### 4.3 Update Cart Item

**PATCH** `/api/auth/cart/<id>/` 🔒

Set an exact quantity for a cart item.

**Example:** `PATCH /api/auth/cart/1/`

**Request Body:**
```json
{
  "quantity": 5
}
```

**Response — 200 OK:**
```json
{
  "message": "Quantity updated.",
  "item": {
    "id": 1,
    "product": {
      "product_id": 101,
      "product_name": "Paracetamol 500mg",
      "mrp": 25.50,
      "manufacturer_name": "Sun Pharma",
      "pack_size_label": "Strip of 10 Tablets"
    },
    "quantity": 5,
    "added_at": "2026-04-10T11:00:00.000000+05:30"
  }
}
```

**Response — 404 Not Found:**
```json
{
  "error": "Cart item not found."
}
```

---

### 4.4 Remove Cart Item

**DELETE** `/api/auth/cart/<id>/` 🔒

**Example:** `DELETE /api/auth/cart/1/`

**Response — 200 OK:**
```json
{
  "message": "Item removed from cart."
}
```

**Response — 404 Not Found:**
```json
{
  "error": "Cart item not found."
}
```

---

## 5. Wishlist

### 5.1 Get Wishlist

**GET** `/api/auth/wishlist/` 🔒

**Response — 200 OK:**
```json
{
  "count": 1,
  "wishlist": [
    {
      "id": 1,
      "product": {
        "product_id": 101,
        "product_name": "Paracetamol 500mg",
        "mrp": 25.50,
        "manufacturer_name": "Sun Pharma",
        "pack_size_label": "Strip of 10 Tablets"
      },
      "added_at": "2026-04-10T12:00:00.000000+05:30"
    }
  ]
}
```

---

### 5.2 Add to Wishlist

**POST** `/api/auth/wishlist/` 🔒

**Request Body:**
```json
{
  "product_id": 101
}
```

**Response — 201 Created:**
```json
{
  "message": "Added to wishlist.",
  "item": {
    "id": 1,
    "product": {
      "product_id": 101,
      "product_name": "Paracetamol 500mg",
      "mrp": 25.50,
      "manufacturer_name": "Sun Pharma",
      "pack_size_label": "Strip of 10 Tablets"
    },
    "added_at": "2026-04-10T12:00:00.000000+05:30"
  }
}
```

**Response — 200 OK** (already in wishlist):
```json
{
  "message": "Already in wishlist."
}
```

**Response — 400 Bad Request:**
```json
{
  "product_id": ["Product not found."]
}
```

---

### 5.3 Remove from Wishlist

**DELETE** `/api/auth/wishlist/<id>/` 🔒

**Example:** `DELETE /api/auth/wishlist/1/`

**Response — 200 OK:**
```json
{
  "message": "Removed from wishlist."
}
```

**Response — 404 Not Found:**
```json
{
  "error": "Wishlist item not found."
}
```

---

## 6. Orders

### 6.1 Place Order

**POST** `/api/auth/orders/` 🔒

**Option A — Order from cart** (cart is cleared after order is placed):

```json
{
  "delivery_address": "12, MG Road, Bengaluru, Karnataka - 560001"
}
```

**Option B — Order specific products directly:**

```json
{
  "delivery_address": "12, MG Road, Bengaluru, Karnataka - 560001",
  "products": [
    { "product_id": 101, "quantity": 2 },
    { "product_id": 205, "quantity": 1 }
  ]
}
```

**Response — 201 Created:**
```json
{
  "message": "Order placed successfully.",
  "order": {
    "id": 1,
    "status": "pending",
    "total_amount": "171.00",
    "delivery_address": "12, MG Road, Bengaluru, Karnataka - 560001",
    "items": [
      {
        "id": 1,
        "product": {
          "product_id": 101,
          "product_name": "Paracetamol 500mg",
          "mrp": 25.50,
          "manufacturer_name": "Sun Pharma",
          "pack_size_label": "Strip of 10 Tablets"
        },
        "quantity": 2,
        "price": "25.50"
      },
      {
        "id": 2,
        "product": {
          "product_id": 205,
          "product_name": "Vitamin D3 60000 IU",
          "mrp": 120.00,
          "manufacturer_name": "Cipla",
          "pack_size_label": "Strip of 4 Capsules"
        },
        "quantity": 1,
        "price": "120.00"
      }
    ],
    "created_at": "2026-04-10T14:00:00.000000+05:30",
    "updated_at": "2026-04-10T14:00:00.000000+05:30"
  }
}
```

**Response — 400 Bad Request** (empty cart):
```json
{
  "non_field_errors": ["Cart is empty. Add products to cart first."]
}
```

---

### 6.2 List Orders

**GET** `/api/auth/orders/` 🔒

**Response — 200 OK:**
```json
{
  "count": 2,
  "orders": [
    {
      "id": 2,
      "status": "delivered",
      "total_amount": "51.00",
      "delivery_address": "12, MG Road, Bengaluru, Karnataka - 560001",
      "items": [
        {
          "id": 3,
          "product": {
            "product_id": 101,
            "product_name": "Paracetamol 500mg",
            "mrp": 25.50,
            "manufacturer_name": "Sun Pharma",
            "pack_size_label": "Strip of 10 Tablets"
          },
          "quantity": 2,
          "price": "25.50"
        }
      ],
      "created_at": "2026-04-09T09:00:00.000000+05:30",
      "updated_at": "2026-04-09T18:00:00.000000+05:30"
    },
    {
      "id": 1,
      "status": "pending",
      "total_amount": "171.00",
      "delivery_address": "12, MG Road, Bengaluru, Karnataka - 560001",
      "items": [],
      "created_at": "2026-04-10T14:00:00.000000+05:30",
      "updated_at": "2026-04-10T14:00:00.000000+05:30"
    }
  ]
}
```

> Orders are returned newest first.

---

### 6.3 Order Detail

**GET** `/api/auth/orders/<id>/` 🔒

**Example:** `GET /api/auth/orders/1/`

**Response — 200 OK:**
```json
{
  "id": 1,
  "status": "pending",
  "total_amount": "171.00",
  "delivery_address": "12, MG Road, Bengaluru, Karnataka - 560001",
  "items": [
    {
      "id": 1,
      "product": {
        "product_id": 101,
        "product_name": "Paracetamol 500mg",
        "mrp": 25.50,
        "manufacturer_name": "Sun Pharma",
        "pack_size_label": "Strip of 10 Tablets"
      },
      "quantity": 2,
      "price": "25.50"
    },
    {
      "id": 2,
      "product": {
        "product_id": 205,
        "product_name": "Vitamin D3 60000 IU",
        "mrp": 120.00,
        "manufacturer_name": "Cipla",
        "pack_size_label": "Strip of 4 Capsules"
      },
      "quantity": 1,
      "price": "120.00"
    }
  ],
  "created_at": "2026-04-10T14:00:00.000000+05:30",
  "updated_at": "2026-04-10T14:00:00.000000+05:30"
}
```

**Response — 404 Not Found:**
```json
{
  "error": "Order not found."
}
```

---

### 6.4 Cancel Order

**PATCH** `/api/auth/orders/<id>/` 🔒

Only orders with status `pending` can be cancelled.

**Example:** `PATCH /api/auth/orders/1/`

*(No request body required)*

**Response — 200 OK:**
```json
{
  "message": "Order cancelled.",
  "order": {
    "id": 1,
    "status": "cancelled",
    "total_amount": "171.00",
    "delivery_address": "12, MG Road, Bengaluru, Karnataka - 560001",
    "items": [ "..." ],
    "created_at": "2026-04-10T14:00:00.000000+05:30",
    "updated_at": "2026-04-10T14:10:00.000000+05:30"
  }
}
```

**Response — 400 Bad Request** (non-pending order):
```json
{
  "error": "Cannot cancel an order with status 'delivered'."
}
```

**Response — 404 Not Found:**
```json
{
  "error": "Order not found."
}
```

---

## Order Status Flow

```
pending → confirmed → shipped → delivered
   ↓
cancelled  (only from pending)
```

---

## HTTP Status Code Summary

| Code | Meaning |
|---|---|
| 200 | OK — request succeeded |
| 201 | Created — resource created successfully |
| 400 | Bad Request — validation error or invalid input |
| 401 | Unauthorized — missing or invalid token |
| 404 | Not Found — resource does not exist |
