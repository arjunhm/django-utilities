from django.core.management.base import BaseCommand
import sys
import os
import re


class Command(BaseCommand):
    help = f"Generates a URL based on the view name"

    def add_arguments(self, parser):
        parser.add_argument('app', nargs='+', type=str)

    def get_model_details(self, file):

        temp_list = []
        fields = []
        models = []
        model_counter = -1

        with open(file, 'r') as fp:

            lines = fp.readlines()

            for line in lines:
                line = line.strip()

                if line.endswith("(models.Model):"):
                    model_name = line.split()[1].split("(")[0]
                    models.append(model_name)
                    if model_counter >= 0:
                        temp = {
                            "model": models[model_counter],
                            "fields": fields
                        }
                        temp_list.append(temp)
                    model_counter += 1
                    fields = []

                if "= models." in line:
                    field_name = line.split("=")[0].strip()
                    fields.append(field_name)

        temp = {
            "model": models[model_counter],
            "fields": fields
        }
        temp_list.append(temp)

        return temp_list

    def create_serializer(self, model):
        model_name = model.get("model")
        string = f"class {model_name}Serializer(serializers.ModelSerializer):\n"
        string += f"\n"
        string += f"    class Meta:\n"
        string += f"\tmodel = {model_name}\n"
        string += f"\tfields = '__all__'\n\n"

        print(string)

    def handle(self, *args, **kwargs):

        app = kwargs.get("app", [])[0]
        # Switch to app directory
        os.chdir(f"{app}")
        print(os.getcwd())

        if "models.py" in os.listdir():
            model_details = self.get_model_details("models.py")
            # print(model_details)

        for model in model_details:
            self.create_serializer(model)
