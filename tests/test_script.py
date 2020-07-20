import json
import os
import re
import pytest
import yaml

from jsonschema import validate
from jsonschema.exceptions import ValidationError

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)


schema_name = "script"
schema_file = f"{schema_name}-v1.0.schema.json"
schema_path = os.path.join(root, schema_name, schema_file)


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
        for name in content["buildspecs"].keys():
            with pytest.raises(ValidationError) as excinfo:
                validate(instance=content["buildspecs"][name], schema=loaded)
            print(excinfo.type, excinfo.value)
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
        for name in content["buildspecs"].keys():
            print(content["buildspecs"][name])
            validate(instance=content["buildspecs"][name], schema=loaded)
            print("Testing %s from recipe %s should be valid" % (name, recipe))


def test_script_examples(tmp_path):
    """the script test_organization is responsible for all the schemas
       in the root of the repository, under <schema>/examples.
       A schema specific test is intended to run tests that
       are specific to a schema. In this case, this is the "script"
       folder. Invalid examples should be under ./invalid/script.
    """
    print("Root of testing is %s" % root)
    print("Testing schema %s" % schema_file)
    print("schema_path:", schema_path)
    loaded = load_schema(schema_path)
    assert isinstance(loaded, dict)

    # Assert is named correctly
    print("Getting version of %s" % schema_file)
    match = re.search(
        "%s-v(?P<version>[0-9]{1}[.][0-9]{1})[.]schema[.]json" % schema_name,
        schema_file,
    )
    assert match

    # Ensure we found a version
    assert match.groups()
    version = match["version"]

    # Ensure a version folder exists with invalids
    print("Checking that invalids exist for %s" % schema_file)
    invalids = os.path.join(here, "invalid", schema_name, version)
    valids = os.path.join(here, "valid", schema_name, version)

    assert invalids
    assert valids

    invalid_recipes = os.listdir(invalids)
    valid_recipes = os.listdir(valids)

    assert invalid_recipes
    assert valid_recipes

    check_valid_recipes(valid_recipes, valids, loaded, version)
    check_invalid_recipes(invalid_recipes, invalids, loaded, version)
