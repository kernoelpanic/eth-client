#!/bin/bash
# 
# Run this to clean the blockchain state and set it back to block 0 (genesis)
#
set -e 
echo ""
echo "!ATTENTION!"
echo ""
echo "Attempting to clean local geth blockchain state"
echo "Press 'y' to continue (any other key to abort)."
echo ""

read -n1 -s -r -p $'Press 'y' to continue ...' key
if ! [[ "$key" = 'y' ]]; then
	# Anything else pressed
  echo "Pressed $key Aborting ..."
  exit 1
fi

echo "Removing blockchain state ..."
echo "Attempt to remove ./geth/datadir/bob/*"
rm -v -I -r ./geth/datadir/bob/[^k]*

echo "Fixing permissions ..."
chmod -R o+w,o+r,o+x ./geth/datadir/
