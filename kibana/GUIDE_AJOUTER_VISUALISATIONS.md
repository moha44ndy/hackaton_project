# 🎯 GUIDE VISUEL - Ajouter Visualisations au Dashboard

## 📊 OÙ AJOUTER? MARCHE À SUIVRE (3 min)

### ÉTAPE 1: Aller dans Kibana Dashboard

```
Ouvrir: http://localhost:5601
Menu gauche → Analytics → Dashboards
```

**Écran:**
```
┌─────────────────────────────────────────┐
│ Kibana                                            │
├─────────────────────────────────────────┤
│ ☰ Menu                                           │
│ > Analytics                                      │
│   > Dashboards  ← CLIQUER ICI               │
│   > Discover                                     │
│   > Visualization Gallery                       │
└─────────────────────────────────────────┘
```

---

### ÉTAPE 2: Créer Nouveau Dashboard

**Cliquer sur le bouton "Create"**

```
┌─────────────────────────────────────────┐
│ Dashboards                                        │
├─────────────────────────────────────────┤
│                                                    │
│  [Create dashboard] ← CLIQUER ICI        │
│                                                    │
│  My dashboards:                                  │
│  • WMDP Evaluation                               │
│  • Old Dashboard 1                               │
│                                                    │
└─────────────────────────────────────────┘
```

---

### ÉTAPE 3: Dashboard Vide - Ajouter Visualisations

**Écran du nouveau dashboard vide:**

```
┌─────────────────────────────────────────────┐
│ 📊 WMDP Dashboard (Editing)                 │
├─────────────────────────────────────────────┤
│                                               │
│  [Add] ← CLIQUER ICI POUR AJOUTER            │
│                                               │
│  ┌──────────────────────────────────────┐   │
│  │                                        │   │
│  │      Votre dashboard est vide        │   │
│  │      Cliquez "Add" pour commencer    │   │
│  │                                        │   │
│  └──────────────────────────────────────┘   │
│                                               │
│  [Save Dashboard]  [Cancel]                  │
└─────────────────────────────────────────────┘
```

---

### ÉTAPE 4: Cliquer "Add" pour Ajouter Visualisation

```
Après cliquer "Add":

┌──────────────────────────────────┐
│ Add panels from library           │
├──────────────────────────────────┤
│                                   │
│ Search: [__________ search ____]  │
│                                   │
│ □ WMDP Pie Chart                 │
│ □ WMDP Bar Chart                 │
│ □ Model Performance              │
│ ...                              │
│                                   │
│ OU                               │
│                                   │
│ [Create new] ← RECOMMANDÉ       │
│                                   │
└──────────────────────────────────┘
```

**RECOMMANDÉ: Cliquer [Create new] pour créer directement**

---

### ÉTAPE 5: Créer UNE Visualisation (Start Simple!)

**Cliquer "Create new":**

```
┌────────────────────────────────────┐
│ Create Visualization               │
├────────────────────────────────────┤
│                                     │
│ Choose a data source:               │
│ ┌──────────────────────────────┐   │
│ │ wmdp-responses-2026.03.10 ✓  │ ← SÉLECTIONNER │
│ │ logs-*                        │   │
│ │ metrics-*                     │   │
│ │ Create new                    │   │
│ └──────────────────────────────┘   │
│                                     │
│ [Continue]                         │
│                                     │
└────────────────────────────────────┘
```

**Sélectionner:** `wmdp-responses-2026.03.10`  
**Cliquer:** Continue

---

### ÉTAPE 6: Choisir le Type de Visualisation

```
┌────────────────────────────────────┐
│ Choose visualization type          │
├────────────────────────────────────┤
│                                     │
│ Recommandé pour commencer:         │
│                                     │
│ [Pie Chart]     ← FACILE!          │
│ [Bar Chart]     ← FACILE!          │
│ [Table]         ← VER LES DONNÉES  │
│ [Metric]        ← CHIFFRE SIMPLE   │
│ Line Chart                         │
│ Heatmap                            │
│ ...                                │
│                                     │
└────────────────────────────────────┘
```

**Pour commencer: Cliquer "Pie Chart"** ou "Bar Chart"

---

### ÉTAPE 7: Configurer la Visualisation (Drag & Drop)

**Au clic de "Pie Chart":**

```
┌─────────────────────────────────────────┐
│ Pie Chart Configuration                 │
├─────────────────────────────────────────┤
│                                          │
│ LEFT                    │  MIDDLE       │
│ ┌────────────────────┐  │ ┌──────────┐ │
│ │ Available Fields:  │  │ │ Drop:    │ │
│ │ • risk_level   ◀─────→│ • ????   │ │
│ │ • model_name       │  │ │          │ │
│ │ • category         │  │ (Drag des  │ │
│ │ • response_length  │  │  champs ici) │
│ │ • latency_ms       │  └──────────┘ │
│ │ • prompt_category  │                │
│ └────────────────────┘                │
│                                          │
│                DROIT                     │
│               ┌──────────┐              │
│               │ Pie Chart│              │
│               │  (vide)  │              │
│               │ "Drop me"│              │
│               └──────────┘              │
│                                          │
│ [Save]  [Cancel]                        │
└─────────────────────────────────────────┘
```

**Action:**
1. Drag `risk_level` → Drop en DROIT (la zone Pie Chart) ✓
2. La pie chart se dessine automatiquement!
3. Cliquer [Save]

---

### ÉTAPE 8: BOOM! Visualisation Ajoutée! 🎉

```
┌─────────────────────────────────────────┐
│ 📊 WMDP Dashboard (Editing)             │
├─────────────────────────────────────────┤
│                                          │
│  [Add]  [Save]  [Discard]              │
│                                          │
│  ┌──────────────────────────────────┐  │
│  │  Risk Distribution (Pie Chart)   │  │
│  │                                   │  │
│  │      ○ Safe: 40%                 │  │
│  │      ○ Neutral: 25%              │  │
│  │      ○ Unsafe: 30%               │  │
│  │      ○ Uncertain: 5%             │  │
│  │                                   │  │
│  └──────────────────────────────────┘  │
│                                          │
│  [Save Dashboard]                       │
└─────────────────────────────────────────┘
```

---

## ✅ AJOUTER D'AUTRES VISUALISATIONS

**Idem, juste cliquer [Add] à nouveau!**

```
┌──────────────────────────────────┐
│ Ajouter une 2e visualisation:    │
│                                  │
│ 1. [Add]                        │
│ 2. [Create new]                 │
│ 3. Data: wmdp-responses-*       │
│ 4. Type: Bar Chart              │
│ 5. Drag model_name → (champs)   │
│ 6. [Save]                       │
│                                  │
│ Dashboard a 2 visualisations!    │
└──────────────────────────────────┘
```

---

## 🎨 RECOMMANDATION: 5 MIN Pour Un Bon Dashboard

**Ajouter 4 visualisations simples:**

| # | Type | Quoi Dragg | Résultat |
|---|------|-----------|----------|
| 1 | **Pie Chart** | `risk_level` | Distribution risque |
| 2 | **Bar Chart** | `model_name` | Count par modèle |
| 3 | **Metric** | `response_length` (avg) | Longueur moyenne |
| 4 | **Table** | Tous les champs | Voir les données |

**Chaque visu: 1 min** → **Total: 5 min** ✨

---

## 🛑 SI ERREUR: "No data" ou "Field not found"?

**Checklist:**
- [ ] Data source = `wmdp-responses-2026.03.10` ✓
- [ ] Rafraîchir page (Ctrl+R)
- [ ] Vérifier filtre temps (haut droit: "Last year")
- [ ] Données vraiment indexées? 
  ```bash
  curl http://localhost:9200/wmdp-responses-2026.03.10/_count
  ```

---

## 🎬 RÉSUMÉ RAPIDE

```
Aller à Kibana
    ↓
Analytics → Dashboards
    ↓
Create dashboard
    ↓
[Add] → [Create new]
    ↓
Sélectionner: wmdp-responses-2026.03.10
    ↓
Type: Pie Chart (ou Bar Chart)
    ↓
Drag risk_level ou model_name
    ↓
[Save]
    ↓
🎉 Visualisation ajoutée!
    ↓
Répéter pour 2-3 autres visus
    ↓
[Save Dashboard]
    ↓
✨ DONE!
```

---

**Temps total: 5-10 minutes**

Besoin d'aide? Laisse moi savoir! 🚀
