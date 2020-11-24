from django.db import models


class Script(models.Model):
    script_name = models.CharField(max_length=100)
    writer = models.CharField(max_length=100)
    owner = models.ForeignKey(
        "auth.User", related_name="scripts", on_delete=models.CASCADE
    )


class Line(models.Model):
    script = models.ForeignKey(Script, related_name="lines", on_delete=models.CASCADE)
    order = models.IntegerField()
    name = models.CharField(max_length=100)
    cue = models.TextField(blank=True)
    line_id = models.CharField(max_length=36)
    should_play = models.BooleanField()
    uploaded = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]
