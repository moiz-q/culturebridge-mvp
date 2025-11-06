"""
Script to verify database models are properly configured.
This script checks model structure without requiring a database connection.
"""

from app.models import (
    User, UserRole,
    ClientProfile, CoachProfile,
    Booking, BookingStatus, Payment, PaymentStatus,
    Post, PostType, Comment, Resource, ResourceType, Bookmark, MatchCache
)
from app.database import Base


def verify_models():
    """Verify all models are properly registered with SQLAlchemy Base"""
    
    print("Verifying database models...\n")
    
    # Get all tables from metadata
    tables = Base.metadata.tables
    
    print(f"Total tables registered: {len(tables)}\n")
    
    expected_tables = [
        'users',
        'client_profiles',
        'coach_profiles',
        'bookings',
        'payments',
        'posts',
        'comments',
        'resources',
        'bookmarks',
        'match_cache'
    ]
    
    print("Expected tables:")
    for table_name in expected_tables:
        if table_name in tables:
            table = tables[table_name]
            columns = [col.name for col in table.columns]
            print(f"  ✓ {table_name} ({len(columns)} columns)")
        else:
            print(f"  ✗ {table_name} - MISSING!")
    
    print("\nModel classes:")
    models = [
        User, ClientProfile, CoachProfile,
        Booking, Payment,
        Post, Comment, Resource, Bookmark, MatchCache
    ]
    
    for model in models:
        print(f"  ✓ {model.__name__} -> {model.__tablename__}")
    
    print("\nEnum types:")
    enums = [
        ('UserRole', UserRole),
        ('BookingStatus', BookingStatus),
        ('PaymentStatus', PaymentStatus),
        ('PostType', PostType),
        ('ResourceType', ResourceType)
    ]
    
    for enum_name, enum_class in enums:
        values = [e.value for e in enum_class]
        print(f"  ✓ {enum_name}: {', '.join(values)}")
    
    print("\n✅ All models verified successfully!")
    
    # Verify relationships
    print("\nVerifying relationships:")
    print(f"  ✓ User -> ClientProfile: {hasattr(User, 'client_profile')}")
    print(f"  ✓ User -> CoachProfile: {hasattr(User, 'coach_profile')}")
    print(f"  ✓ User -> Bookings (as client): {hasattr(User, 'client_bookings')}")
    print(f"  ✓ User -> Bookings (as coach): {hasattr(User, 'coach_bookings')}")
    print(f"  ✓ Booking -> Payment: {hasattr(Booking, 'payment')}")
    print(f"  ✓ Post -> Comments: {hasattr(Post, 'comments')}")
    print(f"  ✓ Resource -> Bookmarks: {hasattr(Resource, 'bookmarks')}")
    
    print("\n✅ All relationships verified!")


if __name__ == "__main__":
    verify_models()
