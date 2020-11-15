from django.db import models


class Script(models.Model):
    scriptName = models.CharField(max_length=100)
    writer = models.CharField(max_length=100)


class Line(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    script = models.ForeignKey(Script, related_name="lines", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cue = models.TextField()
    id = models.CharField(max_length=36, primary_key=True)
    shouldPlay = models.BooleanField()

    class Meta:
        ordering = ["created"]
