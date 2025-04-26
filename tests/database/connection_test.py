import pytest
from app import create_app, db
from app.config import TestingConfig as TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()  # create tables
        yield app
        db.drop_all()  # drop tables after tests


@pytest.fixture
def client(app):
    return app.test_client()


def test_database(app):
    # Example: Add and query a dummy User
    from app.models.tenant import Tenant

    tenant = Tenant(
        name="TestTenant",
        domain="testTenant",
        subdomain="shop",
        schema_name="shop_schema",
        owner_email="tenant@shop.com",
        plan="free"
    )

    db.session.add(tenant)
    db.session.commit()

    queried_tenant = Tenant.query.filter_by(subdomain="shop").first()
    assert queried_tenant is not None
    assert queried_tenant.email == "test@shop.com"
