import json


def format_openapi_json(input_file: str = "openapi.json", output_file: str = "openapi_formatted.json"):
    """
    Load the openapi.json file and format it to be more readable.
    :param input_file:
    :return:
    """
    with open(input_file, "r") as file:
        data = file.read()

    content = json.loads(data)

    with open(output_file, "w") as file:
        json.dump(content, file, indent=4, sort_keys=True)

    print("Done formatting openapi.json to openapi_formatted.json")


if __name__ == "__main__":
    format_openapi_json()
