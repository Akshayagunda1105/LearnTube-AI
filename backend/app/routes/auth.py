from fastapi import APIRouter, HTTPException

from app.schemas.auth import SignupRequest, SignupResponse
from app.database.mongodb import users_collection
from app.models.user import create_user_document
from app.services.auth_service import hash_password


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