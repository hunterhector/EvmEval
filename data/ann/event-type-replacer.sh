#!/bin/bash
# Replaces old event types with new event types in brat annotation files.
# Note that the command below replaces only the first occurrence in each line
# because sometimes strings can be exactly the same as old types), so it
# doesn't use the 'g' option in the sed command.

cat event-type-map.txt | while read -r line; do set -- $line; find . -name "*.ann" -type f | xargs sed -i.backup "s/	$1/	$2/" ; done
