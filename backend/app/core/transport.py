from fastapi_users.authentication import BearerTransport

# The tokenUrl points to the login endpoint that fastapi-users will create.
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
