from .models import maintable, ksuit, registry, manufacturer, terminal_model,type_cabinet, service_wg
from rest_framework import serializers

def fix_encoding(value):
	if not isinstance(value, str):
		return value
	try:
		return value.encode('latin1').decode('utf-8')
	except Exception:
		return value

class maintableSerializer(serializers.ModelSerializer):
	do_name = serializers.StringRelatedField(read_only=True)
	class Meta:
		model = maintable
		fields = ['callidentifier', 'do_name', 'starttime', 'ksuit_name', 'originator', 'numberdigits', 'dialstring', 'destination', 'duration', 'callsignaling', 'conference', 'orig_ipaddress', 'dest_ipaddress']

	def to_representation(self, instance):
		data = super().to_representation(instance)
		data['conference'] = fix_encoding(data['conference'])
		return data


class registrySerializerForEndpoint(serializers.ModelSerializer):
	id_manufacturer = serializers.StringRelatedField(read_only=True)
	id_model = serializers.StringRelatedField(read_only=True)
	id_type_cabinet = serializers.StringRelatedField(read_only=True)
	class Meta:
		model = registry
#		fields = ['id_manufacturer','id_model','serial_number', 'id_type_cabinet','site','software_version']
		fields = '__all__'

class endpointSerializer(serializers.ModelSerializer):
	reg_ip = registrySerializerForEndpoint(read_only=True)
	class Meta:
		model = ksuit
		fields = '__all__'

class registrySerializerForExportEndpoint(serializers.ModelSerializer):
	id_manufacturer = serializers.StringRelatedField(read_only=True)
	id_model = serializers.StringRelatedField(read_only=True)
	id_type_cabinet = serializers.StringRelatedField(read_only=True)
	class Meta:
		model = registry
		fields = ['id_manufacturer','id_model','serial_number', 'id_type_cabinet','site','software_version']
#		fields = '__all__'

class ExportEndpointSerializer(serializers.ModelSerializer):
	reg_ip = registrySerializerForExportEndpoint(read_only=True)
	class Meta:
		model = ksuit
		fields = '__all__'

class registrySerializerForEditEndpoint(serializers.ModelSerializer):
	id_manufacturer = serializers.StringRelatedField(read_only=True)
	id_model = serializers.StringRelatedField(read_only=True)
	id_type_cabinet = serializers.StringRelatedField(read_only=True)
	class Meta:
		model = registry
#		fields = ['id_manufacturer','id_model','serial_number', 'id_type_cabinet','site','software_version']
		fields = '__all__'

class EditEndpointSerializer(serializers.ModelSerializer):
	reg_ip = registrySerializerForEditEndpoint(read_only=True)
	class Meta:
		model = ksuit
		fields = '__all__'
