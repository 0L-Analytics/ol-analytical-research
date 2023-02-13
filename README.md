# ol-analytical-research

### Dump a docker postgres db to a file
```bash
docker exec -t <container> pg_dumpall -c -U <user> | gzip > ./path/dump_all.gz
```
### Restore a backup to a docker postgres db
```bash
gunzip < ./path/dump_all.gz | docker exec -i <container> psql -U <user> -d <database>
```