"""
Hält die Converter-Klasse, die zum Serialisieren der Daten dient.
Created on 24.03.2023
"""
import cattrs.preconf.json

__author__ = "jasper"

converter = cattrs.preconf.json.make_converter()