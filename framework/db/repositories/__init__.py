"""Database repository layer — table-specific data access and validation."""
from framework.db.repositories.users_repository import UsersRepository
from framework.db.repositories.products_repository import ProductsRepository
from framework.db.repositories.categories_repository import CategoriesRepository
from framework.db.repositories.orders_repository import OrdersRepository

__all__ = ["UsersRepository", "ProductsRepository", "CategoriesRepository", "OrdersRepository"]
