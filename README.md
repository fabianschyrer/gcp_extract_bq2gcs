# README #

Extract BQ table/views to AVRO formats

### Example Command ###

docker run --rm -v /opt/service-account:/opt/service-account -e "TZ=Asia/Bangkok" -e "GOOGLE_APPLICATION_CREDENTIALS=/opt/service-account/service-account.json" acm.dp.extract.bq.to.gcs "python main.py -t SG_V1_TMNID_MASTER -d staging_temp -p staging -gcs gs://<BUCKET_NAME> -sdate <START_DATE_YYYY-MM-DD> -edate <END_DATE_YYYY-MM-DD> -m daily"

