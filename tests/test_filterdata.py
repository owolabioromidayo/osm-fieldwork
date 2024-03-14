import argparse 
import os
import sys
import logging
import geojson

from io import BytesIO
from geojson import FeatureCollection, dump

from osm_fieldwork.filter_data import FilterData
from osm_rawdata.config import QueryConfig

# find the path of root tests dir
rootdir = os.path.dirname(os.path.abspath(__file__))

os.system("pip install xlrd")

xlsfile = f"{rootdir}/testdata/buildings.xls"
config = QueryConfig(f"{rootdir}/testdata/buidlings.yaml")

def test_init():
    """ Make sure the object initializes."""
    cleaned = FilterData(xlsfile, config)

def test_parse():
    """Test that the parsing method works"""
    cleaned = FilterData()
    title, extract = cleaned.parse(xlsfile, config)
    assert title == "Buildings"
    assert extract == "buildings.geojson"
    assert len(cleaned.tags) != 0
    assert len(cleaned.keep) != 0

def test_cleandata():
    """Ensure that the cleanData method works"""
    cleaned = FilterData()
    cleaned.parse(xlsfile, config)
    new = cleaned.cleanData(f"{rootdir}/testdata/osm_buildings.geojson")

    assert type(new) == FeatureCollection
    print("Done")