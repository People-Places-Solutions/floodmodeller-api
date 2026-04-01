LATEST_SCHEMA_VERSION = '7.3'

SCHEMA_ORIGIN = r"https://www.floodmodeller.com"
SCHEMA_URI_TPL = r"http://schema.floodmodeller.com/{0}/2d.xsd"
SCHEMA_LOCATION_TPL = rf"{SCHEMA_ORIGIN} {SCHEMA_URI_TPL}"
DEFAULT_SCHEMA_LOCATION = SCHEMA_URI_TPL.format(LATEST_SCHEMA_VERSION)

DEFAULT_NAMESPACE = r"https://www.floodmodeller.com"
XSI_NAMESPACE = r"http://www.w3.org/2001/XMLSchema-instance"
XSI_SCHEMA_LOCATION_KEY = f"{{{XSI_NAMESPACE}}}schemaLocation"
