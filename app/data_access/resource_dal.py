"""
Resource Data Access Layer
Campus Resource Hub - AiDD 2025 Capstone

CRUD operations for Resource model with search and filtering.
"""

from app import db
from app.models import Resource

class ResourceDAL:
    """Data Access Layer for Resource operations."""
    
    @staticmethod
    def create_resource(owner_id, title, description, category, location, 
                       capacity=None, images=None, availability_rules=None, 
                       requires_approval=False):
        """Create a new resource."""
        resource = Resource(
            owner_id=owner_id,
            title=title,
            description=description,
            category=category,
            location=location,
            capacity=capacity,
            images=images,
            availability_rules=availability_rules,
            requires_approval=requires_approval,
            status='draft'
        )
        db.session.add(resource)
        db.session.commit()
        return resource
    
    @staticmethod
    def get_resource_by_id(resource_id):
        """Get resource by ID."""
        return Resource.query.get(resource_id)
    
    @staticmethod
    def get_all_resources(status='published'):
        """Get all resources with a specific status."""
        return Resource.query.filter_by(status=status).all()
    
    @staticmethod
    def get_resources_by_owner(owner_id):
        """Get all resources owned by a user."""
        return Resource.query.filter_by(owner_id=owner_id).all()
    
    @staticmethod
    def search_resources(query, category=None, location=None, status='published'):
        """Search resources by title, description, category, or location."""
        filters = [Resource.status == status]
        
        if query:
            filters.append(
                db.or_(
                    Resource.title.ilike(f'%{query}%'),
                    Resource.description.ilike(f'%{query}%')
                )
            )
        
        if category:
            filters.append(Resource.category == category)
        
        if location:
            filters.append(Resource.location.ilike(f'%{location}%'))
        
        return Resource.query.filter(db.and_(*filters)).all()
    
    @staticmethod
    def get_resources_by_category(category, status='published'):
        """Get all resources in a category."""
        return Resource.query.filter_by(category=category, status=status).all()
    
    @staticmethod
    def update_resource(resource_id, **kwargs):
        """Update resource fields."""
        resource = Resource.query.get(resource_id)
        if not resource:
            return None
        
        for key, value in kwargs.items():
            if hasattr(resource, key):
                setattr(resource, key, value)
        
        db.session.commit()
        return resource
    
    @staticmethod
    def publish_resource(resource_id):
        """Publish a draft resource."""
        resource = Resource.query.get(resource_id)
        if not resource:
            return None
        
        resource.status = 'published'
        db.session.commit()
        return resource
    
    @staticmethod
    def archive_resource(resource_id):
        """Archive a resource."""
        resource = Resource.query.get(resource_id)
        if not resource:
            return None
        
        resource.status = 'archived'
        db.session.commit()
        return resource
    
    @staticmethod
    def delete_resource(resource_id):
        """Delete a resource."""
        resource = Resource.query.get(resource_id)
        if not resource:
            return False
        
        db.session.delete(resource)
        db.session.commit()
        return True
    
    @staticmethod
    def check_availability(resource_id, start_time, end_time):
        """Check if resource is available for given time slot."""
        resource = Resource.query.get(resource_id)
        if not resource:
            return False
        
        return resource.is_available(start_time, end_time)
