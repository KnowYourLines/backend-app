from django.db import models


class Script(models.Model):
    script_name = models.CharField(max_length=100)
    writer = models.CharField(max_length=100)


class Line(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    script = models.ForeignKey(Script, related_name="lines", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cue = models.TextField()
    line_id = models.CharField(max_length=36)
    should_play = models.BooleanField()

    class Meta:
        ordering = ["created"]
