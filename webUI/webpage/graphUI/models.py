from django.db import models

class GraphQuery(models.Model):
    query_text = models.CharField(max_length=200)
    distance = models.IntegerField(default=1)
    def __str__(self):
        return self.query_text
