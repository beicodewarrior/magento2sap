#!/bin/bash

BASEDIR="/home/sandy.tu/magedst"
SCRIPTDIR="$BASEDIR/astro"
logfile="$SCRIPTDIR/log/magedstsync.log"

product_to_mage(){
  echo "Product master sync start at `date +%Y-%m-%d-%R`" >> $logfile
  /usr/bin/python $SCRIPTDIR/app_dev.py -a productm2mage >> $logfile
  echo "Product master sync complete at `date +%Y-%m-%d-%R`" >> $logfile
  echo "Config product sync start at `date +%Y-%m-%d-%R`" >> $logfile
  /usr/bin/python $SCRIPTDIR/app_dev.py -a configproduct2mage >> $logfile
  echo "Config product sync complete at `date +%Y-%m-%d-%R`" >> $logfile
  echo "Product stock sync start at `date +%Y-%m-%d-%R`" >> $logfile
  /usr/bin/python $SCRIPTDIR/app_dev.py -a stock2mage >> $logfile
  echo "Product stock sync complete at `date +%Y-%m-%d-%R`" >> $logfile
  echo "Product price sync start at `date +%Y-%m-%d-%R`" >> $logfile
  /usr/bin/python $SCRIPTDIR/app_dev.py -a price2mage >> $logfile
  echo "Product price sync complete at `date +%Y-%m-%d-%R`" >> $logfile
  echo "Product tier price sync start at `date +%Y-%m-%d-%R`" >> $logfile
  /usr/bin/python $SCRIPTDIR/app_dev.py -a tierprice2mage >> $logfile
  echo "Product tier price sync complete at `date +%Y-%m-%d-%R`" >> $logfile
}

ship_to_mage(){
  echo "Shipment sync start at `date +%Y-%m-%d-%R`" >> $logfile
  /usr/bin/php $SCRIPTDIR/updateShipment.php dev >> $logfile
  echo "Shipment sync complete at `date +%Y-%m-%d-%R`" >> $logfile
}

case $1 in
productm2mage)
        product_to_mage;;
ship2mage)
        ship_to_mage;;
*)
        echo "Usage: productm2mage, ship2mage";;
esac
