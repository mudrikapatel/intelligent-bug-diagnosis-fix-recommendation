# ---------------- COMPONENTS ----------------

COMPONENTS = {
    "Payment Gateway": [
        "payment", "checkout", "transaction", "upi",
        "credit card", "debit card", "billing", "refund"
    ],

    "Authentication": [
        "login", "signin", "logout", "password",
        "jwt", "oauth", "authentication"
    ],

    "Shopping Cart": [
        "cart", "basket", "add to cart", "remove item"
    ],

    "Order Management": [
        "order", "shipment", "tracking", "delivery"
    ],

    "Search": [
        "search", "filter", "sort"
    ],

    "Backend API": [
        "api", "endpoint", "request", "response", "json"
    ],

    "Database": [
        "sql", "database", "mysql", "postgres", "query"
    ],

    "Frontend": [
        "button", "page", "ui", "css",
        "html", "react", "angular", "vue"
    ],

    "Notification": [
        "email", "sms", "otp", "notification"
    ]
}


# ---------------- EXCEPTIONS ----------------

EXCEPTIONS = {
    "nullpointerexception": 25,
    "sqlexception": 20,
    "sql": 20,
    "outofmemoryerror": 35,
    "stackoverflowerror": 35,
    "sockettimeoutexception": 15,
    "timeoutexception": 15,
    "ioexception": 10,
    "filenotfoundexception": 5
}


# ---------------- BUSINESS IMPACT ----------------

IMPACT = {
    "production": 30,
    "all users": 25,
    "customers": 20,
    "thousands": 25,
    "payment": 25,
    "checkout": 25,
    "cannot": 20,
    "unable": 20,
    "crash": 30,
    "fatal": 35,
    "blocked": 20,
    "failed": 15,
    "error": 10
}
