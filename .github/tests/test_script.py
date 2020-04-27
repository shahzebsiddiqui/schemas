import json
import os
import re
import pytest
import yaml

from jsonschema import validate
from jsonschema.exceptions import ValidationError

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(here))


def load_schema(path):
    """load a schema from file. We assume a json file
    """
    with open(path, "r") as fd:
        schema = json.loads(fd.read())
    return schema


def load_recipe(path):
    """load a yaml recipe file
    """
    with open(path, "r") as fd:
        content = yaml.load(fd.read(), Loader=yaml.SafeLoader)
    return content


def check_invalid_recipes(recipes, invalids, loaded, version):
    for recipe in recipes:
        assert recipe
        assert re.search("(yml|yaml)$", recipe)
        recipe_path = os.path.join(invalids, recipe)
        content = load_recipe(recipe_path)

        # Ensure version is correct in header
        assert content["version"] == version
        del content["version"]

        # For each section, assume folder type and validate
        for name in content.keys():
            with pytest.raises(ValidationError) as excinfo:
                validate(instance=content[name], schema=loaded)
            print("Testing %s from recipe %s should be invalid" % (name, recipe))


def check_valid_recipes(recipes, valids, loaded, version):
    for recipe in recipes:
        assert recipe
        assert re.search("(yml|yaml)$", recipe)
        recipe_path = os.path.join(valids, recipe)
        content = load_recipe(recipe_path)

        # Ensure version is correct in header
        assert content["version"] == version
        del content["version"]

        # For each section, assume folder type and validate
        for name in content.keys():
            validate(instance=content[name], schema=loaded)
            print("Testing %s from recipe %s should be valid" % (name, recipe))


def test_script_schema(tmp_path):
    """the script test_organization is responsible for all the schemas
       in the root of the repository, under <schema>/examples.
       A schema specific test is intended to run tests that
       are specific to a schema. In this case, this is the "script"
       folder. Invalid examples should be under ./invalid/script.
    """
    print("Root of testing is %s" % root)

    schema_name = "script"
    schema_dir = os.path.abspath(os.path.join(root, schema_name))
    print("Testing schema %s" % schema_name)

    schemas = os.listdir(schema_dir)
    for schema in schemas:
        if schema.endswith("json"):

            # Assert it loads with jsonschema
            schema_file = os.path.join(schema_dir, schema)
            loaded = load_schema(schema_file)

            # Assert is named correctly
            print("Getting version of %s" % schema)
            match = re.search(
                "%s-v(?P<version>[0-9]{1}[.][0-9]{1}[.][0-9]{1})[.]schema[.]json"
                % schema_name,
                schema,
            )
            assert match

            # Ensure we found a version
            assert match.groups()
            version = match["version"]

            # Ensure a version folder exists with invalids
            print("Checking that invalids exist for %s" % schema)
            invalids = os.path.join(here, "invalid", schema_name, version)
            valids = os.path.join(here, "valid", schema_name, version)

            assert os.path.exists(invalids)
            invalid_recipes = os.listdir(invalids)
            valid_recipes = os.listdir(valids)

            assert invalid_recipes
            assert valid_recipes

            check_valid_recipes(valid_recipes, valids, loaded, version)
            check_invalid_recipes(invalid_recipes, invalids, loaded, version)