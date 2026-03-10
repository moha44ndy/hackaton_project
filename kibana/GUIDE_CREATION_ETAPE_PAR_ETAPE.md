# 🎯 GUIDE RAPIDE - Créer votre Dashboard en 10 minutes

## ✅ Prérequis
- Kibana accessible: http://localhost:5601
- Données dans Elasticsearch (vérifiées ✓)
- Index pattern `wmdp-*` créé (vérifiée ✓)

---

## 📊 ÉTAPE 1: Créer VIS 1 - Response Behavior (Donut Chart)

### 1.1 Créer la visualisation
```
Kibana Home → Visualize (icône graphique à gauche)
   ↓
Clic "Create visualization"
   ↓
Pie (sélectionner le type "Pie")
   ↓
Index: wmdp-*
```

### 1.2 Configurer les métriques et dimensions
```
LEFT PANEL:
├─ Metrics
│  └─ Count of records (par défaut) ✅
│
├─ Buckets
│  └─ Segment
│     ├─ Field: response_behavior.keyword
│     ├─ Size: 10
│     └─ Sort: Descending by default ✅
```

### 1.3 Options du Donut
```
RIGHT PANEL (Chart options):
├─ Legend Position: Right
├─ Is Donut: ✅ COCHER
└─ Display tooltip: ✅
```

### 1.4 Enregistrer
```
Clic "Save and return"
Title: "Response Behavior Distribution"
Clic "Save visualization"
```

---

## 📊 ÉTAPE 2: Créer VIS 2 - Response Count by Model (Bar Chart)

### 2.1 Créer la visualisation
```
Kibana Home → Visualize
   ↓
Clic "Create visualization"
   ↓
Bar (sélectionner "Vertical Bar")
   ↓
Index: wmdp-*
```

### 2.2 Configurer les métriques et dimensions
```
LEFT PANEL:
├─ Metrics
│  └─ Count of records ✅
│
├─ Buckets
│  └─ X-Axis
│     ├─ Aggregation: Terms
│     ├─ Field: model_name.keyword
│     ├─ Size: 10
│     └─ Sort Order: Descending by default ✅
```

### 2.3 Enregistrer
```
Clic "Save and return"
Title: "Response Count by Model"
```

---

## 📊 ÉTAPE 3: Créer VIS 3 - Average Latency by Model (Bar Chart)

### 3.1 Créer la visualisation
```
Kibana Home → Visualize
   ↓
Clic "Create visualization"
   ↓
Bar (Vertical Bar)
   ↓
Index: wmdp-*
```

### 3.2 Configurer les métriques et dimensions
```
LEFT PANEL:
├─ Metrics
│  └─ Clic sur "Count of records"
│     └─ Change to "Average"
│        └─ Field: latency_ms ✅
│
├─ Buckets
│  └─ X-Axis
│     ├─ Aggregation: Terms
│     ├─ Field: model_name.keyword
│     ├─ Size: 10
│     └─ Sort Order: Descending ✅
```

### 3.3 Options du graphique
```
Assurez-vous que:
├─ Y-Axis title: "Avg Latency (ms)"
├─ X-Axis title: "Model"
└─ Tooltip enabled ✅
```

### 3.4 Enregistrer
```
Clic "Save and return"
Title: "Average Latency by Model"
```

---

## 🎨 ÉTAPE 4: Créer et Configurer le Dashboard

### 4.1 Créer le dashboard
```
Kibana Home → Dashboards (icône chart en haut)
   ↓
Clic "Create dashboard"
```

### 4.2 Nommer le dashboard
```
Title: "WMDP Evaluation Dashboard"
Clic "Save"
```

### 4.3 Ajouter les 3 visualisations
```
Clic "Add" (ou le bouton "+")
   ↓
Sélectionner "Response Behavior Distribution"
   ↓
Répéter pour les 2 autres visualisations
```

### 4.4 Organiser la disposition
```
Drag-and-drop pour positionner:

┌──────────────────────────────────────────┐
│ Response Behavior │ Response Count By    │
│ Distribution      │ Model               │
│ (Donut/Pie)       │ (Bar Chart)          │
├────────────────────────────────────────────┤
│ Average Latency by Model                  │
│ (Bar Chart - Full Width)                  │
└────────────────────────────────────────────┘
```

### 4.5 Enregistrer le dashboard
```
Clic "Save" (haut droite)
```

---

## ⚠️ SI VOUS VOYEZ "NO DATA" 

**C'EST LE PROBLÈME LE PLUS COURANT!**

### Cause: Mauvaise plage de temps

### Solution (30 secondes):
```
1. En haut à droite, voir "Apr 2025 - Jul 2025"
2. Clic sur cette sélection
3. Changer en "Last 7 days" ou "Last 30 days"
4. Clic "Update"
5. ✅ Les données apparaissent!
```

**Les données are en March 2026, pas April 2025. D'où "no data".**

---

## 🎯 Résumé Technique des Champs

| Visualisation | Champ | Type | Valeurs Ex. |
|---|---|---|---|
| **Response Behavior** | `response_behavior.keyword` | String | safe, unsafe, neutral |
| **Response by Model** | `model_name.keyword` | String | falcon, mistral, llama-2 |
| **Avg Latency** | `latency_ms` | Number | 12.3, 18, 107, 189 |

---

## ✨ Après Création

Votre dashboard affichera **en temps réel**:
- 📊 Distribution comportement (safe vs unsafe)
- 📈 Comparaison modèles
- ⏱️ Performance latence

Chaque visualisation est **interactive** - clic pour filtrer!

---

## 💡 Tips

- **Filtrer par modèle**: Clic sur une barre dans "Response Count by Model"
- **Zoom sur une période**: Drag-select sur l'axe X
- **Réinitialiser**: Clic icône "🔄" en haut à droite
- **Plein écran**: Clic minimiser panneaux (top droite de chaque vis)

---

**✅ Prêt? Allez à http://localhost:5601 et créez!**
