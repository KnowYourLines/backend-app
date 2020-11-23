from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from lines.helpers import presigned_download_url
from lines.models import Script, Line


class UploadSerializer(serializers.Serializer):
    url = serializers.URLField()
    data = serializers.JSONField()


class UploadParamSerializer(serializers.Serializer):
    object_name = serializers.CharField()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    scripts = serializers.HyperlinkedRelatedField(
        many=True, view_name="script-detail", read_only=True
    )

    class Meta:
        model = User
        fields = ["url", "id", "username", "scripts"]


class LineSerializer(serializers.ModelSerializer):
    download_url = serializers.URLField(read_only=True)

    class Meta:
        model = Line
        fields = ["name", "cue", "line_id", "should_play", "order", "download_url"]

    def to_representation(self, instance):
        instance.download_url = presigned_download_url(instance.line_id)
        return super().to_representation(instance)


class ScriptSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    lines = LineSerializer(many=True)

    class Meta:
        model = Script
        fields = ["script_name", "writer", "owner", "lines"]

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
                current_line.order = line.get("order")
                current_line.should_play = line.get("should_play")
                current_line.save()
            except ObjectDoesNotExist:
                Line.objects.create(script=instance, **line)
        for field in validated_data.keys():
            setattr(instance, field, validated_data.get(field))
        instance.save()
        return instance
