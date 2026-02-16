# Pour utiliser elk :

donner les permissions necessaires:
```bash
chmod 644 elk/elasticsearch/config/elasticsearch.yml
chmod 644 elk/kibana/config/kibana.yml
chmod 644 elk/logstash/config/logstash.conf
chmod 755 results/
```

puis on demarre elk :
```bash
cd elk
docker compose -f docker-compose-elk.yml up -d
```

ensuite, il faut attendre un peu, on peut checker regulierement si elasticsearch marche avec 
```bash
curl http://localhost:9200
```

ca doit nous donner un json avec ecrit "you know, for search" en bas
on peut ensuite verifier si kibana marche avec
```bash
curl -I http://localhost:5601
```
et ca donnera HTTP/1.1 302 Found

on accedera ensuite a kibana en ouvrant http://localhost:5601/ sur un navigateur.

on y verra les fichiers stockés dans le dossier results.