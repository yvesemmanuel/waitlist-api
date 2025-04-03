"""
Base model.
"""

from sqlalchemy import inspect
from sqlalchemy.orm import declarative_base
from typing import List, Dict, Any, Set, Optional

from app.config import settings


SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL


class BaseDict:
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Base:
    def to_dict(
        self,
        exclude: Optional[List[str]] = None,
        include: Optional[List[str]] = None,
        include_relationships: bool = False,
        nested_level: int = 0,
        max_nested_level: int = 1,
        visited: Optional[Set[int]] = None,
    ) -> Dict[str, Any]:
        """
        Convert model instance to dictionary excluding SQLAlchemy internal attributes.

        Parameters:
        -----------
        exclude: List[str]
            List of field names to exclude from the result
        include: List[str]
            List of field names to include in the result (if provided, only these fields will be included)
        include_relationships: bool
            Whether to include relationship fields
        nested_level: int
            Current nesting level for relationship processing
        max_nested_level: int
            Maximum nesting level for relationships to prevent circular references
        visited: Set[int]
            Set of object ids already processed to prevent circular references

        Returns:
        --------
        dict: Dictionary with model's column names and values
        """
        if visited is None:
            visited = set()

        obj_id = id(self)
        if obj_id in visited:
            return {"id": getattr(self, "id", None)}
        visited.add(obj_id)

        exclude = exclude or []
        mapper = inspect(self.__class__)

        columns = {column.key for column in mapper.columns if column.key not in exclude}

        if include:
            columns = {col for col in columns if col in include}

        result = {column: getattr(self, column) for column in columns}

        if include_relationships and nested_level < max_nested_level:
            for relationship in mapper.relationships:
                if relationship.key in exclude:
                    continue

                if include and relationship.key not in include:
                    continue

                related_obj = getattr(self, relationship.key)

                if related_obj is not None:
                    if hasattr(related_obj, "__iter__") and not isinstance(
                        related_obj, (str, bytes)
                    ):
                        result[relationship.key] = [
                            item.to_dict(
                                exclude=exclude,
                                include=include,
                                include_relationships=include_relationships,
                                nested_level=nested_level + 1,
                                max_nested_level=max_nested_level,
                                visited=visited,
                            )
                            if hasattr(item, "to_dict")
                            else str(item)
                            for item in related_obj
                        ]
                    else:
                        result[relationship.key] = (
                            related_obj.to_dict(
                                exclude=exclude,
                                include=include,
                                include_relationships=include_relationships,
                                nested_level=nested_level + 1,
                                max_nested_level=max_nested_level,
                                visited=visited,
                            )
                            if hasattr(related_obj, "to_dict")
                            else str(related_obj)
                        )

        return result


Base = declarative_base(cls=Base)
