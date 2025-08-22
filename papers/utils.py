import re


def normalize_doi(value: str) -> str:
    if not isinstance(value, str):
        return value
    value = value.strip()
    value = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^doi:", "", value, flags=re.IGNORECASE)
    return value.strip()


def travers_inferred(tags, **kwargs):
    visited = kwargs.get("visited", set())
    for tag in tags.all():
        if tag.id in visited:
            return
        visited.add(tag.id)
        yield tag
        yield from travers_inferred(tag.inferred_tags, visited=visited)
