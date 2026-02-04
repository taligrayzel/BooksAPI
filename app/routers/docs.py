"""Swagger / OpenAPI documentation endpoints."""
from flask import Blueprint, jsonify, render_template_string


docs_bp = Blueprint("docs", __name__)


OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Books API",
        "version": "1.0.0",
        "description": "API for managing books and authors.",
    },
    "paths": {
        "/books": {
            "get": {
                "summary": "List books",
                "description": "Retrieve all books, optionally filtered by author.",
                "parameters": [
                    {
                        "name": "author_id",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "integer"},
                        "description": "Filter by author id",
                    }
                ],
                "responses": {
                    "200": {
                        "description": "A list of books",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Book"},
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Invalid query parameter",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            },
            "post": {
                "summary": "Create book",
                "description": "Create a new book (requires authentication).",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/BookCreate"}
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "Book created",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "id": {"type": "integer"},
                                        "message": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Validation error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "409": {
                        "description": "Conflict",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            },
        },
        "/books/{book_id}": {
            "get": {
                "summary": "Get book by ID",
                "parameters": [
                    {
                        "name": "book_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Book found",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        **{
                                            k: v
                                            for k, v in {
                                                "id": {"type": "integer"},
                                                "title": {"type": "string"},
                                                "author_id": {"type": "integer"},
                                                "isbn": {"type": "string"},
                                                "published_year": {"type": "integer"},
                                                "genres": {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                                "created_at": {"type": "string"},
                                            }.items()
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "404": {
                        "description": "Book not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            },
            "put": {
                "summary": "Update book",
                "description": "Update an existing book (requires authentication).",
                "parameters": [
                    {
                        "name": "book_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/BookUpdate"}
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Book updated",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "message": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Validation error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "404": {
                        "description": "Book not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            },
            "delete": {
                "summary": "Delete book",
                "description": "Delete a book (requires authentication).",
                "parameters": [
                    {
                        "name": "book_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Book deleted",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "message": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "403": {
                        "description": "Forbidden",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "404": {
                        "description": "Book not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            },
        },
        "/authors": {
            "post": {
                "summary": "Create author",
                "description": "Create a new author (requires authentication).",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AuthorCreate"}
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "Author created",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "id": {"type": "integer"},
                                        "message": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Validation error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "401": {
                        "description": "Unauthorized",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "409": {
                        "description": "Conflict",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            }
        },
        "/authors/{author_id}/books": {
            "get": {
                "summary": "Get books for author",
                "parameters": [
                    {
                        "name": "author_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Author and their books",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "author": {
                                            "$ref": "#/components/schemas/Author"
                                        },
                                        "books": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/Book"},
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "404": {
                        "description": "Author or books not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            }
        },
        "/register": {
            "post": {
                "summary": "Register user",
                "description": "Create a new user account.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/RegisterRequest"}
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "User created",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "id": {"type": "integer"},
                                        "message": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Validation error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "409": {
                        "description": "User already exists",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            }
        },
        "/auth/login": {
            "post": {
                "summary": "Login",
                "description": "Authenticate user and obtain an access token.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/LoginRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Authenticated",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/Token",
                                }
                            }
                        },
                    },
                    "400": {
                        "description": "Validation error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "401": {
                        "description": "Invalid password",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "404": {
                        "description": "User not found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            }
        },
    },
    "components": {
        "schemas": {
            "Book": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "title": {"type": "string"},
                    "author_id": {"type": "integer"},
                    "isbn": {"type": "string", "nullable": True},
                    "published_year": {"type": "integer", "nullable": True},
                    "genres": {
                        "type": "array",
                        "items": {"type": "string"},
                        "nullable": True,
                    },
                    "created_at": {"type": "string", "format": "date-time", "nullable": True},
                },
                "required": ["id", "title", "author_id"],
            },
            "BookCreate": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "title": {"type": "string"},
                    "author_id": {"type": "integer"},
                    "isbn": {"type": "string"},
                    "published_year": {"type": "integer"},
                    "genres": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["id", "title", "author_id"],
            },
            "BookUpdate": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "author_id": {"type": "integer"},
                    "isbn": {"type": "string"},
                    "published_year": {"type": "integer"},
                    "genres": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                },
            },
            "Author": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "bio": {"type": "string", "nullable": True},
                    "country": {"type": "string", "nullable": True},
                },
                "required": ["id", "name"],
            },
            "AuthorCreate": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "bio": {"type": "string"},
                    "country": {"type": "string"},
                },
                "required": ["id", "name"],
            },
            "RegisterRequest": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"},
                },
                "required": ["username", "password"],
            },
            "LoginRequest": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "password": {"type": "string"},
                },
                "required": ["username", "password"],
            },
            "Token": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string"},
                },
                "required": ["access_token"],
            },
        }
    },
}


SWAGGER_UI_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Books API - Swagger UI</title>
    <link
      rel="stylesheet"
      href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"
    />
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.onload = () => {
        window.ui = SwaggerUIBundle({
          url: "{{ spec_url }}",
          dom_id: "#swagger-ui",
        });
      };
    </script>
  </body>
</html>
"""


@docs_bp.route("/openapi.json")
def openapi_json():
    return jsonify(OPENAPI_SPEC)


@docs_bp.route("/docs")
def swagger_ui():
    return render_template_string(SWAGGER_UI_HTML, spec_url="/openapi.json")
