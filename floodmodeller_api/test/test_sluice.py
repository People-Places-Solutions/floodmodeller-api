from floodmodeller_api.units import SLUICE


def test_non_supported_sluice_type_writes():
    unit_block = [
        "SLUICE Sluice with type Water1",
        "VERTICAL",
        "USNODE      DSNODE                 ",
        "     0.700     0.700     1.950     1.050     1.390     5.400",
        "     0.270     1.420     1.000     1.000     0.000     1.000     1.000",
        "         3SECONDS   EXTEND    ",
        "WATER1                             0.000",
        "GATE      1                                                                     ",
        "         3",
        "     0.000     2.200",
        "     3.000     2.200",
        "1.000e+010     2.200",
        "GATE      2                                                                     ",
        "         3",
        "     0.000     2.200",
        "     3.000     2.200",
        "1.000e+010     2.200",
        "GATE      3                                                                     ",
        "         3",
        "     0.000     2.200",
        "     3.000     2.200",
        "1.000e+010     2.200",
    ]
    sluice = SLUICE(unit_block)
    result = sluice._write()
    assert list(map(str.rstrip, result)) == list(map(str.rstrip, unit_block))
