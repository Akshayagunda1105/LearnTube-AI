from fastapi import APIRouter, HTTPException

from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    LoginResponse
)
from app.database.mongodb import users_collection
from app.models.user import create_user_document
from app.services.auth_service import hash_password, verify_password
from app.services.jwt_service import create_access_token


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post("/signup", response_model=SignupResponse)
def signup(request: SignupRequest):
    # Check whether the email already exists
    existing_user = users_collection.find_one({
        "email": request.email
    })

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered"
        )

    # Hash the password
    password_hash = hash_password(request.password)

    # Create the user document
    user_document = create_user_document(
        name=request.name,
        email=request.email,
        password_hash=password_hash
    )

    # Insert into MongoDB
    result = users_collection.insert_one(user_document)

    # Return only safe user information
    return SignupResponse(
        id=str(result.inserted_id),
        name=user_document["name"],
        email=user_document["email"]
    )


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    # Find the user by email
    user = users_collection.find_one({
        "email": request.email
    })

    # Do not reveal whether the email exists
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify the password
    password_is_valid = verify_password(
        request.password,
        user["password_hash"]
    )

    if not password_is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT access token
    access_token = create_access_token(
        str(user["_id"])
    )

    # Return token and safe user information
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=SignupResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"]
        )
    )