# 📚 INDEX DES GUIDES - DASHBOARD KIBANA WMDP

## 🎯 Vous Êtes Ici: Guides de Création du Dashboard

Tous les fichiers ci-dessous sont dans le répertoire **`kibana/`**

---

## 📖 GUIDES - Par Ordre de Lecture

### **1️⃣ COMMENCER ICI** ⭐
📄 **`00_LIRE_D_ABORD.md`**
- Résumé rapide (2 minutes)
- Le problème + la solution
- Plan d'action en 15 minutes
- Status de chaque composant

👉 **Durée**: 2 min | **Difficulté**: ⭐

---

### **2️⃣ GUIDE ÉTAPE PAR ÉTAPE** ⭐⭐
📄 **`GUIDE_CREATION_ETAPE_PAR_ETAPE.md`**
- Instructions détaillées (avec images)
- Créer 3 visualisations
- Configurer le dashboard
- Time-range fix

👉 **Durée**: 20 min read | **Difficulté**: ⭐ (très facile)

---

### **3️⃣ GUIDE COMPLET (Référence)**
📄 **`GUIDE_DASHBOARD_WMDP.md`**
- Utilisation complète du dashboard
- Champs disponibles
- Troubleshooting
- Export/Import
- Prochaines étapes avancées

👉 **Durée**: 10 min read | **Difficulté**: ⭐⭐

---

### **4️⃣ README RAPIDE**
📄 **`README_DASHBOARD.md`**
- Démarrage ultra-rapide
- Checklist finale
- Liens directs
- Troubleshooting courant

👉 **Durée**: 3 min | **Difficulté**: ⭐

---

## 🛠️ FICHIERS TECHNIQUES

### Scripts Python
```
💻 import_wmdp_dashboard.py
   - Script pour importer via API
   - (A essayé, limitations Kibana 8.12)

💻 test_dashboard_readiness.py
   - Diagnostic des composants
   - Vérifie ES, Kibana, indices

💻 GUIDE_DASHBOARD_MANUEL.py
   - Instructions alternatives
```

### Fichiers de Configuration
```
📦 wmdp_dashboard_export.ndjson
   - Export Kibana complet
   - (Pour import via UI Kibana)
```

---

## 🎯 QUELLE APPROCHE?

### ✅ Si vous êtes IMPATIENT (10 min)
1. Lire `00_LIRE_D_ABORD.md` 
2. Fixer la plage de temps
3. Suivre la checklist rapide

### ✅ Si vous voulez APPRENDRE (30 min)
1. Lire `00_LIRE_D_ABORD.md` 
2. Suivre `GUIDE_CREATION_ETAPE_PAR_ETAPE.md` 
3. Explorer `GUIDE_DASHBOARD_WMDP.md` 

### ✅ Si vous êtes un PRO (5 min)
1. Lire `README_DASHBOARD.md` 
2. Créer directement: Visualize → Pie/Bar
3. Ajouter au dashboard

---

## 🔗 LIENS ACCÈS DIRECT

```
🏠 Kibana Home
   http://localhost:5601

📊 Visualize (Créer les visualisations)
   http://localhost:5601/app/visualize

📈 Dashboards (Voir tous les dashboards)
   http://localhost:5601/app/dashboards

🔍 Discover (Explorer les données)
   http://localhost:5601/app/discover

⚙️ Stack Management (Index patterns, settings)
   http://localhost:5601/app/management
```

---

## ⚠️ LE PROBLÈME À RÉSOUDRE

Vous avez vu "No data" sur votre dashboard?

### Cause
```
Données en Elasticsearch  : 2026-03-02 à 2026-03-05
Plage temporelle Kibana   : Apr 2025 - Jul 2025 ❌
                             ↓
                    PAS DE CORRESPONDANCE!
```

### Solution (30 sec)
1. **Haut droite** du dashboard → voir "Apr 18 - Jul 4"
2. **Clic** sur cette sélection
3. Choisir **"Last 30 days"**
4. **Clic "Update"**
5. ✅ Les données s'affichent!

---

## 📊 LES 3 VISUALISATIONS À CRÉER

### **1. Response Behavior Distribution**
```
Type: Pie Chart (Donut)
Champ: response_behavior.keyword
Métrique: Count of records
Affiche: % safe vs unsafe vs neutral
```

### **2. Response Count by Model**
```
Type: Bar Chart (Vertical)
Champ: model_name.keyword
Métrique: Count of records
Affiche: Nombre réponses par modèle
```

### **3. Average Latency by Model**
```
Type: Bar Chart (Vertical)
Champ: latency_ms (Average)
Métrique: Average latency
Affiche: Temps moyen par modèle
```

---

## ✅ CHECKLIST FINALE

Avant de lancer en production:

```
☐ Plage de temps: Last 30 days
☐ Dashboard: Affiche les données (pas "no data")
☐ VIS 1: Response Behavior (Pie/Donut)
☐ VIS 2: Response Count (Bar chart)
☐ VIS 3: Avg Latency (Bar chart)
☐ Layout: Bien arrangé dans la grille
☐ Titles: Clairs et descriptifs
☐ Interactivity: Filters testés
☐ Save: Dashboard sauvegardé avec bon nom
☐ URL: http://localhost:5601/app/dashboards/...
```

---

## 🚀 APRÈS LE DASHBOARD

Une fois créé, vous pouvez:

1. **Ajouter plus de visualisations**
   - Risk distribution
   - Timeline latency
   - Model comparison table

2. **Créer des filtres**
   - Par modèle
   - Par plage de dates
   - Par behaviour

3. **Configurer des alertes**
   - Si % unsafe > threshold
   - Si latency > X ms

4. **Lancer le pipeline WMDP**
   ```bash
   python src/wmdp_pipeline.py --models distilgpt2-local --num-prompts 50
   ```
   Dashboard se met à jour **en temps réel**!

---

## 💬 FAQ

**Q: J'ai une erreur "strict mapping"?**  
A: Normal avec l'API Kibana 8.12. Créer les visualisations via UI (plus facile!)

**Q: Pourquoi "Empty Fields"?**  
A: Plage de temps mauvaise. Change en "Last 30 days".

**Q: Comment exporter le dashboard?**  
A: Stack Mgt → Saved Objects → Search "WMDP" → Exporter

**Q: Peut-on importer un template?**  
A: Oui! Utiliser `wmdp_dashboard_export.ndjson` (Stack Mgt → Import)

---

## 📞 BESOIN D'AIDE?

- **Problème technique?** → Voir `GUIDE_DASHBOARD_WMDP.md` (section Troubleshooting)
- **Pas clair?** → Lire `GUIDE_CREATION_ETAPE_PAR_ETAPE.md` 
- **Questions?** → `README_DASHBOARD.md` a une FAQ

---

## 🎯 RÉSUMÉ

| Étape | Fichier | Durée |
|-------|---------|-------|
| **1. Commencer** | `00_LIRE_D_ABORD.md` | 2 min |
| **2. Créer vizs** | `GUIDE_CREATION_ETAPE_PAR_ETAPE.md` | 15 min |
| **3. Reference** | `GUIDE_DASHBOARD_WMDP.md` | On-demand |

**Total: 20 minutes MAX ✅**

---

**✨ Bon travail! Le dashboard WMDP est à votre portée!**
