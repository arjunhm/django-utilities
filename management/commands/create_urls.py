from django.core.management.base import BaseCommand
import sys
import os
import re


class Command(BaseCommand):

    help = f"Generates a URL based on the view name"

    def add_arguments(self, parser):
        parser.add_argument("app", nargs="+", type=str)

    def get_views_in_urls_file(self, file):
        """
        Get list of views arleady present in urls.py
        """
        temp = []

        with open(file, "r") as fp:

            for line in fp.readlines():
                line = line.strip()

                if ".as_view()" in line:
                    url_view_name = line.split(".")[1]
                    temp.append(url_view_name)

        return temp

    def get_view_names(self, file):
        """
        Get list of views in a file
        """

        temp = []
        # You can configure the pattern at https://regex101.com/
        pattern = r"class [a-zA-Z]+\(views.[a-zA-Z]+\):"

        with open(file, "r") as fp:

            for line in fp.readlines():
                line = line.strip()

                # If line matches pattern
                if re.match(pattern, line):
                    # Extracts view name i.e,
                    # class MyCustomAPIView(views.APIView) -> MyCustomAPIView
                    view_name = line.split()[1].split("(")[0]
                    temp.append(view_name)

        return temp

    def create_url_list(self):

        url_list = []
        view_dict = {}
        view_suffix = "APIView"

        for file in os.listdir():
            if file.endswith("views.py"):
                view_names = self.get_view_names(file)
                view_dict[file] = view_names

        # ! This shouldn't execute by default
        os.chdir("..")
        if "urls.py" in os.listdir():
            url_view_names = self.get_views_in_urls_file("urls.py")
        else:
            url_view_names = []

        for view_file in view_dict.keys():
            view_names = view_dict.get(view_file)

            for view_name in view_names:

                if view_name in url_view_names:
                    print(f"{view_name} already present in urls.py")
                    continue
                # Remove suffix from view name
                temp = view_name.replace(view_suffix, "")
                url = ""

                """
                Example of what happens in below code
                MyCustomAPIView -> my-custom
                MyOtherCustomAPIView -> my-other-custom
                QAStatusAPIView -> q-a-status
                """
                r = []
                for index, letter in enumerate(temp):
                    # If letter is in upper case and is not the first letter
                    if letter.isupper() and index != 0:
                        # Add hyphen
                        url += "-"

                    # Add lowercase letter
                    url += letter.lower()

                view = f"{view_file.split('.')[0]}.{view_name}.as_view()"
                name = f"api-{url}-view"
                url += "/"

                url_list.append(f"path('{url}',\n     {view},\n     name='{name}'),")

        return url_list

    def handle(self, *args, **kwargs):

        app = kwargs.get("app", [])[0]
        # Switch to app directory
        os.chdir(f"{app}")

        if "views.py" in os.listdir():
            url_list = self.create_url_list()

        elif "views" in os.listdir():
            os.chdir("views")
            url_list = self.create_url_list()

        print("---------------------")
        for url in url_list:
            print(url)
