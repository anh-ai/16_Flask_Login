from os.path import dirname

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
import os

class ConfigManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.yaml = YAML()
        self.yaml.indent(sequence=4, offset=2)
        self.yaml.preserve_quotes = True
        self.data = {}
        self.modified = False  # new variable to track if data has been modified
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                # self.data = self.yaml.load(f) or {}
                # self.data = self.yaml.load(f) or self.yaml.constructor.CommentedMap()
                self.data = self.yaml.load(f) or CommentedMap()

    def _write_to_file(self):
        if self.modified:
            os.makedirs(dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                self.yaml.dump(self.data, f)
            self.modified = False

    def create_section(self, section_name, comment=None):
        if section_name not in self.data:
            self.data[section_name] = {}
            if comment:
                try:
                    self.data.yaml_add_eol_comment(comment, section_name)
                except:
                    pass
            self.modified = True  # set modified flag to True
            self._write_to_file()
            return True
        return False

    def set_key(self, section_name, key, value, comment=None):
        if section_name not in self.data:
            self.create_section(section_name)
        if key not in self.data[section_name]:
            self.data[section_name][key] = value
            self.modified = True  # set modified flag to True
            try:
                self.data[section_name].yaml_add_eol_comment(comment=comment, key=key)
            except AttributeError:
                pass
        else:
            self.data[section_name][key] = value
            if comment:
                try:
                    self.data[section_name].yaml_add_eol_comment(comment=comment, key=key)
                except:
                    pass
            self.modified = True  # set modified flag to True

        self._write_to_file()

    def get_key(self, section_name, key):
        if section_name not in self.data or key not in self.data[section_name]:
            return None
        return self.data[section_name][key]

    def delete_key(self, section_name, key):
        if section_name in self.data and key in self.data[section_name]:
            del self.data[section_name][key]
            self.modified = True  # set modified flag to True
            self._write_to_file()

    def delete_section(self, section_name):
        if section_name in self.data:
            del self.data[section_name]
            self.modified = True  # set modified flag to True
            self._write_to_file()

    def update_key_comment(self, section_name, key, comment):
        if section_name in self.data and key in self.data[section_name]:
            try:
                self.data[section_name].yaml_add_eol_comment(comment=comment, key=key)
            except AttributeError:
                pass
            self.modified = True  # set modified flag to True
            self._write_to_file()

    def get_section(self, section_name):
        if section_name in self.data:
            return self.data[section_name]
        return None

    def add_key_if_not_exists(self, section_name, key, value, comment=None):
        if section_name not in self.data:
            self.create_section(section_name)
        if key not in self.data[section_name]:
            self.data[section_name][key] = value
            if comment:
                try:
                    self.data.yaml_add_eol_comment(comment, key)
                except:
                    pass

            self.modified = True  # set modified flag to True
        self._write_to_file()


if __name__ == "__main__":
    import os
    os.chdir(r'G:\AI-Projects\Label-Checking')
    # from config import ConfigManager

    # create an instance of the ConfigManager class with the name of your YAML file
    config = ConfigManager("AI_Data/config/config.yaml")
    # create a section and add some keys
    config.create_section("database")
    config.set_key("database", "host", "localhost", comment="Không có gì cả nhá")
    config.set_key("database", "host2", "localhost2", comment="Không có gì cả nhá2")
    config.set_key("database", "host3", "myuser", comment="Không biết cái gì mà lại cứ làm")
    config.set_key("database", "port", 5432)
    config.update_key_comment("database", "port", "Không biếy  bieest thees nafo")
    config.set_key("database", "password", "mypassword")
    config.set_key("database", "password4", "mypassword")

    # get all keys of the database section as a dictionary
    db_config = config.get_section("database")

    # print the dictionary
    print(db_config)  # Output: {'host': 'localhost', 'port': 5432, 'username': 'myuser', 'password': 'mypassword'}

    config.create_section("database1")
    config.set_key("database1", "host", "localhost")

    config.create_section("database")
    # config.set_key("database1", "host", {"ta1":"localhost2", "ta2":123,3:345, 4:456,5:"aksldfjsdf"})
    # config.set_key("database1", "host2", ["localhost2", 123,345, 456,"aksldfjsdf"])
    # config.set_key("database1", "host3", ("localhost2", 123,345, 456,"aksldfjsdf"))
    # config.set_key("database1", "host4", set(["localhost2", 123,345, 456,"aksldfjsdf"]))

    # update a key
    config.set_key("database1", "port", 5432)

    # read a key
    host = config.get_key("database1", "host")
    port2 = config.get_key("database", "host2")
    print(host)  # Output: 5432
    print(port2)  # Output: 5432

    # delete a key
    config.delete_key("database3", "port")

    # delete a section
    config.delete_section("database3")
