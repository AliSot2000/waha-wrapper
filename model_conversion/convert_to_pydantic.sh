#!/bin/bash

datamodel-codegen --use-union-operator --allow-population-by-field-name --input openapi_formatted.json --input-file-type openapi --output waha-model.py
