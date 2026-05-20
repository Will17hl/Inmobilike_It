from ..repositories.property_repository import PropertyRepository


def build_properties_rows(filters=None):
    qs = PropertyRepository.get_active_properties(filters=filters)
    rows = []
    for prop in qs:
        rows.append([
            str(prop.id),
            prop.title,
            prop.location.city if prop.location else "",
            prop.location.neighborhood if prop.location else "",
            str(prop.price),
        ])
    return rows
