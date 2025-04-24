# You would typically put these in a file like `app/schemas/pydantic_models.py`
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any # Dict and Any for attributes field
from datetime import datetime
from decimal import Decimal

# --- Forward Declarations (if needed for circular references) ---
# If Product refers to ProductCategory and ProductCategory refers back,
# sometimes you need forward declarations. For these simple cases, it might not be strictly needed yet,
# but it's good practice for complex relationships. Let's include a basic one for Product.
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from .pydantic_models import ProductResponse


# --- Nested Pydantic Models ---

# For nested user info within ProductReview (assuming you have a User model and want limited info)
# Reusing/adapting from our previous chat!
class UserNestedResponse(BaseModel):
    profile_pic_url: str = 'none'
    first_name: str
    last_name: Optional[str] = None

    class Config:
        from_attributes = True


# For ProductImage within Product
class ProductImageResponse(BaseModel):
    id: int
    image_url: str
    order: int = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# For ProductCategory within Product
class ProductCategoryResponse(BaseModel):
    id: int
    name: str
    category_image: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# For ProductReview within Product
class ProductReviewResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    user: Optional[UserNestedResponse] = None # Nested User Pydantic model!

    class Config:
        from_attributes = True


# --- Main Pydantic Models ---

# For your Product model
class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None # Include if you want the ID, or rely on nested category
    price: Decimal # Use Decimal for accurate prices!
    stock_quantity: int
    weight: Decimal # Use Decimal for weight too
    is_available: bool = True
    is_featured: bool = False
    is_popular: bool = False
    tags: List[str] = [] # ARRAY(db.String) maps to List[str]
    attributes: Optional[Dict[str, Any]] = None # JSONB maps to dict, Any means any value type

    # Properties you want to include in the serialized output
    average_rating: float

    # Relationships represented by nested Pydantic models!
    category: Optional[ProductCategoryResponse] = None # Nested ProductCategory model (Optional because category_id is nullable)
    images: List[ProductImageResponse] = [] # List of nested image models
    reviews: List[ProductReviewResponse] = [] # List of nested review models (if you load them)

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


    class Config:
        from_attributes = True # Allows Pydantic to read from SQLAlchemy attributes
        # Optional: how to handle Decimal when exporting to JSON (as string or float)
        # json_encoders = {Decimal: float} # Encode Decimal as float (be careful with precision!)
        # OR keep as Decimal and let your JSON encoder handle it (e.g. Flask's jsonify)


# For your FeaturedProduct model
# Often, you'd serialize the FeaturedProduct *with* its associated Product details
class FeaturedProductResponse(BaseModel):
    product_id: int
    from_date: datetime
    to_date: datetime

    # Include the computed property
    is_active: bool

    # Relationship: Nested Product model
    product: Optional[ProductResponse] = None # Include the product details

    class Config:
        from_attributes = True


# For your ProductCategory model (if you need to serialize categories directly)
class ProductCategoryDetailResponse(BaseModel):
    id: int
    name: str
    category_image: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    # If you want to list products under a category when serializing the category
    # products: List[ProductResponse] = [] # Be careful: this can load many products!

    class Config:
        from_attributes = True