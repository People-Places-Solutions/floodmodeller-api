import re

version_re = re.compile(r"http(?:s)?:\/\/schema\.floodmodeller\.com\/([0-9\.]+)\/2d\.xsd")

float_re = re.compile(r"^[0-9]+\.[0-9]+$")

int_re = re.compile(r"^[0-9]+$")
