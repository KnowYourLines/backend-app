from rest_framework import serializers

from lines.models import Script, Line


class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = ["name", "cue", "id", "shouldPlay"]


class ScriptSerializer(serializers.ModelSerializer):
    lines = LineSerializer(many=True)

    class Meta:
        model = Script
        fields = ["scriptName", "writer", "lines"]

    def create(self, validated_data):
        lines_data = validated_data.pop("lines")
        script = Script.objects.create(**validated_data)
        for line in lines_data:
            Line.objects.create(script=script, **line)
        return script
