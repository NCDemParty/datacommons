set -x
set -o errexit
#urls=(http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.all.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.fec.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.fec.1990.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.fec.1992.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.fec.1994.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.fec.1996.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.fec.1998.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.fec.2000.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.fec.2002.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.fec.2004.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.fec.2006.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.fec.2008.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.fec.2010.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.nimsp.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.nimsp.1990.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.nimsp.1992.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.nimsp.1994.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.nimsp.1996.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.nimsp.1998.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.nimsp.2000.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.nimsp.2002.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.nimsp.2004.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.nimsp.2006.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.nimsp.2008.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/contributions.nimsp.2010.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110812/lobbying.tar.gz http://datacommons.s3.amazonaws.com/subsets/td-20110906/epa_echo.tgz http://datacommons.s3.amazonaws.com/subsets/td-20110930/faca_records.csv.gz http://datacommons.s3.amazonaws.com/subsets/td-20110419/earmarks.tgz)
urls=(http://datacommons.s3.amazonaws.com/subsets/td-20110419/earmarks.tgz)

for url in ${urls[@]}; do
    wget $url
    BASEFILE=`basename $url`
    gunzip $BASEFILE
    /home/datacommons/virt/bin/python /home/datacommons/lib/python/datacommons/dc_web/manage.py uploadbulk -z ${BASEFILE%.*z}
    rm ${BASEFILE%.*z}
done;
