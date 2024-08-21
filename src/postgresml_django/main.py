from django.db import models
from django.db.models import Func, Value, F
from django.db.models.functions import Cast
import pgvector.django
import json


class GenerateEmbedding(Func):
    function = "pgml.embed"
    template = "%(function)s('%(transformer)s', %(expressions)s, '%(parameters)s')"
    allowed_default = False

    def __init__(self, expression, transformer, parameters={}):
        self.transformer = transformer
        self.parameters = parameters
        super().__init__(expression)

    def as_sql(self, compiler, connection, **extra_context):
        extra_context["transformer"] = self.transformer
        extra_context["parameters"] = json.dumps(self.parameters)
        return super().as_sql(compiler, connection, **extra_context)


class Embed(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        update_fields = kwargs.get("update_fields")

        # Check for fields to embed
        for field in self._meta.get_fields():
            if isinstance(field, VectorField):
                if not hasattr(self, field.field_to_embed):
                    raise AttributeError(
                        f"Field to embed does not exist: `{field.field_to_embed}`"
                    )

                # Only embed if it's a new instance, full save, or this field is being updated
                if not self.pk or update_fields is None or field.name in update_fields:
                    value_to_embed = getattr(self, field.field_to_embed)
                    setattr(
                        self,
                        field.name,
                        GenerateEmbedding(
                            Value(value_to_embed),
                            field.transformer,
                            field.transformer_store_parameters,
                        ),
                    )

        super().save(*args, **kwargs)

    @classmethod
    def vector_search(
        cls, field, query_text, distance_function=pgvector.django.CosineDistance
    ):
        # Get the fields
        field_instance = getattr(cls._meta.model, field).field

        # Generate an embedding for the text
        query_embedding = GenerateEmbedding(
            Value(query_text),
            field_instance.transformer,
            field_instance.transformer_recall_parameters,
        )

        # Return the QuerySet
        return cls.objects.annotate(
            distance=distance_function(
                F(field),
                Cast(
                    query_embedding,
                    output_field=VectorField(dimensions=field_instance.dimensions),
                ),
            )
        ).order_by("distance")


class VectorField(pgvector.django.VectorField):
    def __init__(
        self,
        field_to_embed=None,
        dimensions=None,
        transformer=None,
        transformer_store_parameters={},
        transformer_recall_parameters={},
        *args,
        **kwargs,
    ):
        self.field_to_embed = field_to_embed
        self.transformer = transformer
        self.transformer_store_parameters = transformer_store_parameters
        self.transformer_recall_parameters = transformer_recall_parameters
        super().__init__(dimensions=dimensions, *args, **kwargs)
