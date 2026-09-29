import re


def slugify(text: str) -> str:
    """'Goa Beach Escape!' -> 'goa-beach-escape'"""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "item"


def unique_slug(db, model, base_text: str, exclude_id: int | None = None) -> str:
    """
    Generates a slug from base_text and appends -2, -3, etc. if it collides
    with an existing row - so two packages both called "Goa Getaway" don't
    fight over the same URL.
    """
    base = slugify(base_text)
    slug = base
    counter = 2
    while True:
        query = db.query(model).filter(model.slug == slug)
        if exclude_id is not None:
            query = query.filter(model.id != exclude_id)
        if query.first() is None:
            return slug
        slug = f"{base}-{counter}"
        counter += 1
