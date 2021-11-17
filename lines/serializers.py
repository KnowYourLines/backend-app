from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from lines.helpers import presigned_download_url
from lines.models import Script, Line


class UploadSerializer(serializers.Serializer):
    s3_request = serializers.JSONField()


class UploadParamSerializer(serializers.Serializer):
    object_name = serializers.CharField()


class LineSerializer(serializers.ModelSerializer):
    download_url = serializers.URLField(read_only=True)

    class Meta:
        model = Line
        fields = [
            "name",
            "cue",
            "line_id",
            "should_play",
            "order",
            "download_url",
            "uploaded",
        ]

    def to_representation(self, instance):
        instance.download_url = presigned_download_url(instance.line_id)
        return super().to_representation(instance)


class ScriptSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    lines = LineSerializer(many=True)

    class Meta:
        model = Script
        fields = ["id", "script_name", "owner", "lines"]

    def create(self, validated_data):
        lines_data = validated_data.pop("lines")
        script = Script.objects.create(**validated_data)
        new_lines = [Line(script=script, **line) for line in lines_data]
        Line.objects.bulk_create(new_lines, ignore_conflicts=True)
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
            Line.objects.update_or_create(
                script=instance,
                line_id=line.get("line_id"),
                defaults={
                    "name": line.get("name"),
                    "cue": line.get("cue"),
                    "order": line.get("order"),
                    "should_play": line.get("should_play"),
                    "uploaded": line.get("uploaded"),
                },
            )
        instance.save()
        return instance
