from .strings import to_camel


class ORMConfig:
    orm_mode = True
    alias_generator = to_camel
    allow_population_by_field_name = True
