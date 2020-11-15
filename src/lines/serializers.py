from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from lines.models import Script, Line


class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = ["name", "cue", "line_id", "should_play"]


class ScriptSerializer(serializers.ModelSerializer):
    lines = LineSerializer(many=True)

    class Meta:
        model = Script
        fields = ["script_name", "writer", "lines"]

    def create(self, validated_data):
        lines_data = validated_data.pop("lines")
        script = Script.objects.create(**validated_data)
        for line in lines_data:
            Line.objects.create(script=script, **line)
        return script

    def update(self, instance, validated_data):
        lines = validated_data.pop("lines")
        all_stored_line_ids = [
            line.line_id for line in Line.objects.filter(script=instance)
        ]
        line_ids = [line.get("line_id") for line in lines]
        for extra_id in set(all_stored_line_ids) - set(line_ids):
            Line.objects.filter(line_id=extra_id).delete()
        for line in lines:
            try:
                current_line = Line.objects.get(
                    script=instance, line_id=line.get("line_id")
                )
                current_line.name = line.get("name")
                current_line.cue = line.get("cue")
                current_line.should_play = line.get("should_play")
                current_line.save()
            except ObjectDoesNotExist:
                Line.objects.create(script=instance, **line)
        for field in validated_data.keys():
            setattr(instance, field, validated_data.get(field))
        instance.save()
        return instance
