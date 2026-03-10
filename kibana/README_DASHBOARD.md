# 🚀 DASHBOARD WMDP - GUIDE DE DEMARRAGE RAPIDE

## 📍 Votre Situation Actuelle

✅ **Elasticsearch**: Operational (28 documents)  
✅ **Kibana**: Running (http://localhost:5601)  
✅ **Index Pattern**: Créé (`wmdp-*`)  
✅ **Dashboard vide**: Existe mais sans visualisations  

## ❌ Pourquoi le Dashboard affiche "No Data"?

**La plage de temps est mauvaise!**

```
Les données: 2026-02-16 et 2026-03-02 à 2026-03-05
Kibana affiche: Apr 2025 - Jul 2025 ❌
                 
C'est comme chercher quelque chose demain alors qu'il est aujourd'hui!
```

---

## ✅ FIX IMMÉDIAT (10 secondes)

1. Ouvrir Kibana: http://localhost:5601
2. Aller au Dashboard (si vous y êtes)
3. **Haut droite** → voir "Apr 2025" 
4. **Clic dessus** → sélectionner **"Last 30 days"**
5. **Clic "Update"**
6. ✅ Les données apparaissent!

---

## 📊 Trois Visualisations à Créer

Voici les 3 graphiques clés que vous demandez:

### **1️⃣ Response Behavior Distribution** (Donut Pie)
- **Affiche**: Pourcentage safe vs unsafe vs neutral
- **Champ clé**: `response_behavior.keyword`
- **Utilité**: Voir quelle proportion de réponses est dangereuse

### **2️⃣ Response Count by Model** (Bar Chart)
- **Affiche**: Combien de réponses par modèle (falcon, mistral, llama, etc.)
- **Champ clé**: `model_name.keyword`
- **Utilité**: Comparer le volume de test par modèle

### **3️⃣ Average Latency by Model** (Bar Chart)
- **Affiche**: Temps de réponse moyen par modèle
- **Champ clé**: `latency_ms` (moyenne)
- **Utilité**: Voir quel modèle est le plus rapide/lent

---

## 🎯 Comment Créer les Visualisations

📖 **Voir le guide complet**: [GUIDE_CREATION_ETAPE_PAR_ETAPE.md](GUIDE_CREATION_ETAPE_PAR_ETAPE.md)

Ou voici la version ultra-rapide:

### Rapide (2 min par visualisation):

```
Kibana → Visualize Library → Create visualization

Pour chaque (3x):
1. Choisir type (Pie / Bar)
2. Index: wmdp-*
3. Metrics: Count (ou Average de latency_ms)
4. Buckets: Field = response_behavior.keyword (ou model_name.keyword)
5. Save avec le bon titre
6. Ajouter au dashboard
```

---

## 🔗 Liens Utiles

| Ressource | URL |
|-----------|-----|
| **Kibana Home** | http://localhost:5601 |
| **Visualize** | http://localhost:5601/app/visualize |
| **Dashboards** | http://localhost:5601/app/dashboards |
| **Discover** | http://localhost:5601/app/discover |

---

## 🆘 Troubleshooting Courant

| Problème | Cause | Solution |
|----------|-------|----------|
| "No data / empty" | Mauvaise plage de temps | Change en "Last 30 days" |
| Champs affichent "Empty Fields" | Index pattern mal configuré | Recréer l'index pattern  |
| Visualisation lente | Trop de documents / plage longue | Réduire la période |
| Erreur API | Kibana not responding | Vérifier port 5601 |

---

## 📋 Checklist Finale

Avant présentation/production:

- [ ] 3 visualisations créées
- [ ] Dashboard affiche les données (pas "no data")
- [ ] Plage de temps = "Last 30 days" minimum
- [ ] Chaque visualisation a un titre clair
- [ ] Dispositions bien arranges (pas superposées)
- [ ] Filters/interactions testées
- [ ] Dashboard sauvegardé avec bon nom

---

## 🚀 Prochaines Étapes (Après)

1. **Lancer un pipeline WMDP**:
   ```bash
   cd hackaton_project
   python src/wmdp_pipeline.py --models distilgpt2-local --num-prompts 20
   ```

2. **Observer les données en live** dans le dashboard
3. **Ajouter d'autres visualisations**:
   - Latency timeline
   - Risk level distribution
   - Model comparison table

4. **Créer des alertes** si certains seuils atteints

---

**💡 Besoin d'aide? Regardez les 2 guides détaillés dans le même répertoire!**

- `GUIDE_DASHBOARD_WMDP.md` → Utilisation complète du dashboard
- `GUIDE_CREATION_ETAPE_PAR_ETAPE.md` → Créer les visualisations pas à pas
