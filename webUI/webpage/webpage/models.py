from django import models

class Query(models.Model):
    query_text = models.CharField(max_length=200)

class EntityChoice(models.Model)
    entity_name = models.CharField(max_length=200)
    entity_type = models.CharField(max_length=200)
