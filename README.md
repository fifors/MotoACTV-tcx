# Overview #
Simple Python script that converts the MotoACTV CSV format to TCX. Useful for uploading MotoACTV workout data to sites like [Strava](http://www.strava.com), [Endomondo](http://www.endomondo.com) or [RunKeeper](http://www.runkeeper.com).

# Notes #
The workout data is condensed to a single Lap / Track. Heart-rate information will be included if it exists in the CSV file, but power data is not read. Elevation data may not be correctly handled, but most fitness sites will re-calculate elevation based on the position data.

# Usage #
    ./motoactv_tcx.py -i <CSV file> | tidy -q -i -xml > output.tcx

Note, you can also use the helper script, which will pass commandline options
through to the motoactv\_tcx.py script. It will also autodetect if tidy
is in the path and out put the csv as tcx.

    ./run-moto.sh [f|h|b|p|s <scale>|t <type>] <CSV file>

# Requirements #
* [ElementTree](http://effbot.org/zone/element-index.htm)
