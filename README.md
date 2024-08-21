# postgresml-django

postgresml-django is a Python module that integrates PostgresML with Django ORM, enabling automatic in-database embedding of Django models. It simplifies the process of creating and searching vector embeddings for your text data.

## Introduction

This module provides a seamless way to:
- Automatically generate in-databse embeddings for specified fields in your Django models
- Perform vector similarity searches in-database

## Installation

1. Ensure you have [pgml](https://github.com/postgresml/postgresml) installed and configured in your database. The easiest way to do that is to sign up for a free serverless database at [postgresml.org](https://postgresml.org). You can also host it your self.

2. Install the package using pip:

   ```
   pip install postgresml-django
   ```

You are ready to go!

## Usage Examples

### Example 1: Using intfloat/e5-small-v2

This example demonstrates using the `intfloat/e5-small-v2` transformer, which has an embedding size of 384.

```python
from django.db import models
from postgresml_django import VectorField, Embed

class Document(Embed):
    text = models.TextField()
    text_embedding = VectorField(
        field_to_embed="text",
        dimensions=384,
        transformer="intfloat/e5-small-v2"
    )

# Searching
results = Document.vector_search("text_embedding", "some query to search against")
```

### Example 2: Using mixedbread-ai/mxbai-embed-large-v1

This example shows how to use the `mixedbread-ai/mxbai-embed-large-v1` transformer, which has an embedding size of 1024 and requires specific parameters for recall.

```python
from django.db import models
from postgresml_django import VectorField, Embed

class Article(Embed):
    content = models.TextField()
    content_embedding = VectorField(
        field_to_embed="content",
        dimensions=1024,
        transformer="mixedbread-ai/mxbai-embed-large-v1",
        transformer_recall_parameters={
            "prompt": "Represent this sentence for searching relevant passages: "
        }
    )

# Searching
results = Article.vector_search("content_embedding", "some query to search against")
```

Note the differences between the two examples:
1. The `dimensions` parameter is set to 384 for `intfloat/e5-small-v2` and 1024 for `mixedbread-ai/mxbai-embed-large-v1`.
2. The `mixedbread-ai/mxbai-embed-large-v1` transformer requires additional parameters for recall, which are specified in the `transformer_recall_parameters` argument.

Both examples will automatically generate embeddings when instances are saved and allow for vector similarity searches using the `vector_search` method.

## Contributing

We welcome contributions to postgresml-django! Whether it's bug reports, feature requests, documentation improvements, or code contributions, your input is valuable to us. Feel free to open issues or submit pull requests on our GitHub repository.
