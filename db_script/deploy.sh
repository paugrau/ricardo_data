#!/bin/bash

## deploy data to RICardo instance
usage()
{
    echo "usage: deploy.sh -o|--output ricardo_directory | -h"
}

config()
{
	echo `cat config.json | python -c "import sys,json; print json.load(sys.stdin)['$1']"`
}

##### Main


case $1 in
    -o | --output )           shift
                            output=$1
                            ;;
    -h | --help )           usage
                            exit
                            ;;
    * )                     usage
                            exit 1
esac
shift


# reading conf
export PYTHONIOENCODING=utf8
sqlite_viz=$(config 'sqlite_viz')
sources_export_filename=$(config 'sources_export_filename')
RICentities_export_filename=$(config 'RICentities_export_filename')
rates_export_filename=$(config 'rates_export_filename')

# cp database
sqlite_output=$output'/api/ricardo_api/'
echo "copying ../sqlite_data/$sqlite_viz  to $sqlite_output"
cp ../sqlite_data/$sqlite_viz $sqlite_output
# cp exports
exports_output=$output'/client/data/'
echo "copying ../db_script/$sources_export_filename  to $exports_output"
cp ../db_script/$sources_export_filename $exports_output
echo "copying ../db_script/$RICentities_export_filename  to $exports_output"
cp ../db_script/$RICentities_export_filename $exports_output
echo "copying ../db_script/$rates_export_filename  to $exports_output"
cp ../csv_data/exchange_rates.csv $exports_output$rates_export_filename
