from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
    is_admin = fields.Boolean(dump_only=True)

class ReportSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(max=150))
    description = fields.Str(required=True)
    location = fields.Str(validate=validate.Length(max=200))
    date_of_incident = fields.DateTime(dump_only=True)
    status = fields.Str(dump_only=True)
    is_anonymous = fields.Boolean()
    user_id = fields.Int(dump_only=True)
    author_username = fields.Str(attribute="author.username", dump_only=True)

class NewsArticleSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(max=200))
    content = fields.Str(required=True)
    source = fields.Str(validate=validate.Length(max=100))
    read_more_link = fields.URL(required=False, allow_none=True, relative=False)
    published_date = fields.DateTime(dump_only=True)

class CaseSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(max=150))
    description = fields.Str(required=True)
    status = fields.Str(dump_only=True)
    
class CaseUserSchema(Schema):
    user_id = fields.Int(required=True)
    case_id = fields.Int(dump_only=True)
    role = fields.Str(required=True, validate=validate.Length(max=50))