from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import json

@dataclass
class ColorPalette:
    """Color palette data model"""
    id: str
    website_id: str
    colors: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'website_id': self.website_id,
            'colors': self.colors,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            website_id=data['website_id'],
            colors=data['colors'],
            created_at=datetime.fromisoformat(data['created_at'])
        )

@dataclass
class Website:
    """Website data model"""
    id: str
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    local_image: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    award: Optional[str] = None
    palette_id: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'local_image': self.local_image,
            'tags': self.tags,
            'award': self.award,
            'palette_id': self.palette_id,
            'scraped_at': self.scraped_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            url=data['url'],
            title=data.get('title'),
            description=data.get('description'),
            image_url=data.get('image_url'),
            local_image=data.get('local_image'),
            tags=data.get('tags', []),
            award=data.get('award'),
            palette_id=data.get('palette_id'),
            scraped_at=datetime.fromisoformat(data['scraped_at']) if 'scraped_at' in data else datetime.now()
        )
