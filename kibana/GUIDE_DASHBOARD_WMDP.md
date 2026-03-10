# 📊 DASHBOARD WMDP - GUIDE COMPLET

## ✅ Status: CRÉÉ AVEC SUCCÈS

Votre dashboard **WMDP Evaluation Dashboard** est maintenant **opérationnel** dans Kibana!

---

## 🔗 Accès Direct

👉 **[Ouvrir le Dashboard](http://localhost:5601/app/dashboards/view/wmdp-evaluation-dashboard)**

ou

```
http://localhost:5601/app/dashboards/view/wmdp-evaluation-dashboard
```

---

## 📊 Contenu du Dashboard

### **Visualisation 1 : Response Behavior Distribution** (Haut gauche)
- **Type** : Donut Chart (Camembert)
- **Métrique** : Nombre total de réponses
- **Groupement** : Par `response_behavior` (safe, unsafe, neutral, etc.)
- **Utilité** : Voir la répartition comportement des réponses des LLMs

### **Visualisation 2 : Response Count by Model** (Haut droite)
- **Type** : Bar Chart (Histogramme)
- **Métrique** : Nombre de réponses par modèle
- **Groupement** : Par `model_name` (falcon, mistral, llama-2, distilgpt2, etc.)
- **Utilité** : Comparer le volume de réponses entre les modèles

### **Visualisation 3 : Average Latency by Model** (Bas, full width)
- **Type** : Bar Chart (Histogramme)
- **Métrique** : Latence moyenne (ms) par modèle
- **Groupement** : Par `model_name`
- **Utilité** : Analyser la performance/vitesse de réponse de chaque modèle

---

## 🎯 Bonnes Pratiques

### ⚠️ Problème courant: "No data available"

**Cause**: La plage de temps ne correspond pas aux données

**Solution**:
1. Clic sur le **sélecteur de dates** (haut droite)
2. Sélectionner **"Last 30 days"** ou **"Last 60 days"**
3. Clic **"Update"**

Les données commencent à partir de **2026-02-16** et **2026-03-02** dans vos indices.

### 📈 Interactivité

Les 3 visualisations sont **interactives** :

- Clic sur une section du donut → filtre les autres graphes
- Clic sur une barre → filtre les résultats
- Pour réinitialiser les filtres : Clic sur l'icône **"🔄"** en haut à droite

---

## 🔧 Comment modifier le Dashboard

### Ajouter une visualisation

1. Clic **"Edit"** (en haut)
2. Clic **"Add panel"** (ou **"+"**)
3. Sélectionner une visualisation existante OU créer une nouvelle
4. Positionner et redimensionner
5. Clic **"Save"**

### Créer une nouvelle Visualisation

1. Menu → **Analytics** → **Visualize Library**
2. Clic **"Create visualization"**
3. Type : Pie, Bar, Gauge, Table, MapBox, etc.
4. Index : `wmdp-*`
5. Configurer les **Metrics** et **Buckets**
6. Save en tant que visualisation
7. Ajouter au dashboard

---

## 📝 Champs Disponibles pour Nouvelles Visualisations

Si vous voulez ajouter d'autres visualisations, voici les champs disponibles :

```
response_behavior.keyword  → safe, unsafe, neutral, etc.
model_name.keyword         → falcon, mistral, llama-2, etc.
latency_ms                 → valeur numérique (ms)
prompt_id                  → identifiant du prompt
token_count                → nombre de tokens
timestamp                  → date/heure (@timestamp)
category.keyword           → catégorie du prompt
status.keyword             → success, error, etc.
```

---

## 💾 Import/Export du Dashboard

### Exporter (pour partage)

1. Menu → **Stack Management** → **Saved Objects**
2. Chercher : `wmdp-evaluation-dashboard`
3. Clic les **3 points** → **Export**
4. Fichier NDJSON téléchargé

### Importer (restaurer)

1. Menu → **Stack Management** → **Saved Objects**
2. Clic **"Import"**
3. Sélectionner le fichier NDJSON
4. Cocher **"Overwrite"** si confusion
5. Clic **"Import"**

---

## 🚀 Prochaines Étapes

### Option 1 : Automatiser le pipeline
```bash
cd /path/to/hackaton_project
python src/wmdp_pipeline.py --models distilgpt2-local mistral-7b --num-prompts 50
```
Les données s'ajoutent automatiquement au dashboard en temps réel!

### Option 2 : Ajouter des alertes
1. Menu → **Stack Management** → **Rules and Connectors** → **Rules**
2. Créer une règle si, par exemple:
   - Nombre de réponses "unsafe" > 10%
   - Latence moyenne > 5000 ms

### Option 3 : Partager le dashboard
1. Clic **"Share"** (haut droite)
2. Copier URL ou générer un lien exportable
3. Envoyer à votre organisation

---

## 📞 Troubleshooting

| Problème | Solution |
|----------|----------|
| **No data showing** | Vérifier la date range (need 2026-03 dates) |
| **Fields empty** | Index pattern `wmdp-*` bien créé ? Chercher en Stack Mgt |
| **Visualisation lente** | Réduire la plage de temps ou filtrer les modèles |
| **Erreur lors import** | Vérifier que Kibana est accessible sur port 5601 |

---

## 📚 Ressources

- [Kibana Docs](https://www.elastic.co/guide/en/kibana/8.12/index.html)
- [Dashboard Features](https://www.elastic.co/guide/en/kibana/8.12/dashboard.html)
- WMDP Project: `hackaton_project/WMDP_TECHNICAL_REPORT.json`

---

**✨ Dashboard prêt à l'emploi et alimenté par vos données Elasticsearch!**
