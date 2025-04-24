# services/tenant_service.py
from app.extensions import db
from app.models.tenant import Tenant
import sqlalchemy as sa
from sqlalchemy import inspect
from flask import current_app
import logging

logger = logging.getLogger(__name__)


def create_tenant(name, domain, subdomain, owner_email, plan='free'):
    """Create a new tenant with its own schema."""
    # Generate schema name (e.g., tenant_1, tenant_2)
    schema_name = f"tenant_{subdomain}"

    # Create the tenant in the public schema
    tenant = Tenant(
        name=name,
        domain=domain,
        subdomain=subdomain,
        schema_name=schema_name,
        owner_email=owner_email,
        plan=plan
    )
    db.session.add(tenant)
    db.session.commit()

    # Create the schema
    try:
        db.session.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
        db.session.commit()

        # Create all tables in the new schema
        # This requires creating a temporary metadata with the schema
        with db.engine.connect() as connection:
            # Create a transaction that can be rolled back
            transaction = connection.begin()
            try:
                # Create all tables in the new schema
                from app.models import Base
                # Set search path for this connection
                connection.execute(sa.text(f'SET search_path TO "{schema_name}"'))

                # Create tables using SQLAlchemy's reflection
                from app import create_app
                app = create_app()
                with app.app_context():
                    # Force models to load to ensure all are registered with metadata
                    from app.models import User, Product, Order
                    inspector = inspect(db.engine)

                    # Create tables one by one
                    for table_name in Base.metadata.tables:
                        if '.' in table_name and table_name.split('.')[0] == schema_name:
                            # Skip if table exists
                            pure_table_name = table_name.split('.')[1]
                            if pure_table_name not in inspector.get_table_names(schema=schema_name):
                                logger.info(f"Creating table {table_name}")
                                table = Base.metadata.tables[table_name]
                                table.create(bind=connection, checkfirst=True)

                transaction.commit()
                logger.info(f"Successfully created schema and tables for {schema_name}")
            except Exception as e:
                transaction.rollback()
                logger.error(f"Error creating schema tables: {str(e)}")
                raise
    except Exception as e:
        logger.error(f"Failed to create tenant schema: {str(e)}")
        # Clean up the tenant record if schema creation fails
        db.session.delete(tenant)
        db.session.commit()
        raise

    return tenant


def get_tenant_by_domain(domain):
    """Get tenant by domain name."""
    return Tenant.query.filter_by(domain=domain, is_active=True).first()


def get_tenant_by_subdomain(subdomain):
    """Get tenant by subdomain."""
    return Tenant.query.filter_by(subdomain=subdomain, is_active=True).first()


def deactivate_tenant(tenant_id):
    """Deactivate a tenant."""
    tenant = Tenant.query.get(tenant_id)
    if tenant:
        tenant.is_active = False
        db.session.commit()
        return True
    return False


def delete_tenant(tenant_id, hard_delete=False):
    """Delete a tenant.

    Args:
        tenant_id: ID of the tenant to delete
        hard_delete: If True, drop the schema. If False, just mark as inactive.
    """
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return False

    if hard_delete:
        try:
            # Drop the schema
            db.session.execute(sa.text(f'DROP SCHEMA IF EXISTS "{tenant.schema_name}" CASCADE'))
            # Delete the tenant record
            db.session.delete(tenant)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete tenant: {str(e)}")
            raise
    else:
        # Soft delete - just mark as inactive
        tenant.is_active = False
        db.session.commit()

    return True
