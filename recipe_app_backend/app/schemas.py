"""
Marshmallow schemas for validating and serializing request and response payloads.
"""
from marshmallow import Schema, fields, validate, ValidationError, validates_schema


class PaginationQuerySchema(Schema):
    page = fields.Integer(load_default=1, metadata={"description": "Page number (1-indexed)"})
    page_size = fields.Integer(load_default=10, metadata={"description": "Page size (1-100)"})
    q = fields.String(load_default=None, allow_none=True, metadata={"description": "Search query across title and ingredients"})
    ingredient = fields.String(load_default=None, allow_none=True, metadata={"description": "Filter by ingredient"})

    @validates_schema
    def validate_pagination(self, data, **kwargs):
        page = data.get("page", 1)
        page_size = data.get("page_size", 10)
        if page < 1:
            raise ValidationError("page must be >= 1", field_name="page")
        if page_size < 1 or page_size > 100:
            raise ValidationError("page_size must be between 1 and 100", field_name="page_size")


class RecipeBaseSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=200))
    description = fields.String(load_default="", validate=validate.Length(max=2000))
    ingredients = fields.List(fields.String(), required=True)
    instructions = fields.String(load_default="", validate=validate.Length(max=10000))
    tags = fields.List(fields.String(), load_default=list)


class RecipeCreateSchema(RecipeBaseSchema):
    pass


class RecipeUpdateSchema(Schema):
    title = fields.String(validate=validate.Length(min=1, max=200))
    description = fields.String(validate=validate.Length(max=2000))
    ingredients = fields.List(fields.String())
    instructions = fields.String(validate=validate.Length(max=10000))
    tags = fields.List(fields.String())


class RecipeSchema(RecipeBaseSchema):
    id = fields.Integer(required=True)
    created_at = fields.Integer()
    updated_at = fields.Integer()


class AuthLoginSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=1, max=100))
    password = fields.String(required=True, load_only=True)


class AuthTokenSchema(Schema):
    token = fields.String(required=True)
    user = fields.Dict()
