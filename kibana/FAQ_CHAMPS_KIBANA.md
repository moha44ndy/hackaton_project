# 🎯 RÉPONSE RAPIDE - Quoi Ajouter Dans Kibana

## ❓ Question 1: response_behavior OU response.keyword?

**Réponse:** ❌ **IGNORE LES DEUX** pour commencer!

- `response_behavior` = pas dans nos données (glitch)
- `response.keyword` = le TEXTE brut (trop pour une pie chart)

**À LA PLACE:** Utilise ces champs:
- ✅ `risk_level.keyword` ← **MEILLEUR POUR PIE CHART**
- ✅ `category` ← (biology/chemistry/engineering/general)
- ✅ `model_name.keyword` ← (quel modèle)

---

## ❓ Question 2: Qu'est-ce que je mets en Horizontal? En Vertical?

**ÇA DÉPEND DU TYPE DE GRAPHE:**

### Si c'est une **PIE CHART** 🥧
```
Ignore "Horizontal" et "Vertical"

Tu vois plutôt:
├─ Slice by ← DRAG ICI: risk_level.keyword
└─ Size by  ← Laisse vide (auto)
```

### Si c'est une **BAR CHART** 📊
```
Horizontal axis ← DRAG: model_name.keyword (ou category)
Vertical axis   ← Auto (count)
```

---

## ❓ Question 3: Quel CHAMP j'ajoute en PREMIER?

### 🥇 **RECOMMANDÉ (5 secondes):**

**Ajoute `risk_level.keyword` en premier**

```
┌──────────────────────────────────┐
│ Pie Chart (ou Bar Chart)         │
├──────────────────────────────────┤
│                                   │
│ Slice by:                         │
│ ┌──────────────────────────────┐ │
│ │ + Add or drag field          │ │
│ │   ↑                          │ │  ← DRAG DEPUIS LA GAUCHE
│ │   À LA GAUCHE:               │ │
│ │   • risk_level.keyword ← ICI │ │
│ └──────────────────────────────┘ │
│                                   │
└──────────────────────────────────┘
```

**Résultat:** Pie chart qui montre:
- Safe: 40%
- Unsafe: 30%
- Neutral: 25%
- Uncertain: 5%

---

## 📋 CHAMPS À UTILISER (PAS CONFUS!)

| Champ | Type | Utilité | ✅/❌ |
|-------|------|---------|------|
| `risk_level.keyword` | Pie/Bar | Distribution risque | ✅✅✅ |
| `category` | Pie/Bar | Par domaine (bio/chem) | ✅✅ |
| `model_name.keyword` | Bar | Par modèle LLM | ✅✅ |
| `response_length` | Metric | Longueur moyenne | ✅ |
| `latency_ms` | Metric | Temps moyen | ✅ |
| **response_behavior** | ❌ | N'existe pas | ❌❌❌ |
| **response.keyword** | ❌ | Trop de texte | ❌ |

---

## 🚀 PROCÉDURE EXACTE (Copy-Paste)

### **Pour une PIE CHART:**

1. **Cliquer sur "Pie Chart"** ✓
2. **Sélectionner data:** `wmdp-responses-2026.03.10` ✓ Continue
3. **Après écran de config:**
   ```
   Slice by: [+ Add field]
   ↓
   Drag depuis la gauche: risk_level.keyword
   ↓
   [Save]
   ```

### **Pour une BAR CHART:**

1. **Cliquer sur "Bar Chart"** ✓
2. **Sélectionner data:** `wmdp-responses-2026.03.10` ✓ Continue
3. **Après écran de config:**
   ```
   Horizontal axis: [+ Add field]
   ↓
   Drag: model_name.keyword OU category
   ↓
   Vertical axis: Auto (count) - laisse vide
   ↓
   [Save]
   ```

---

## 🎯 RÉSUMÉ SIMPLE

| Question | Réponse |
|----------|---------|
| Quel champ en premier? | **risk_level.keyword** |
| Horizontal ou Vertical? | Dépend du type → **Voir tableau ci-dessus** |
| response_behavior? | **IGNORE** ❌ |

---

## 💡 COMMENÇONS SIMPLE (La Plus Facile):

**Fais une PIE CHART avec `risk_level.keyword`**
→ 30 secondes
→ Tu veras les % safe/unsafe/etc
→ Tu sauras comment ça marche!

Puis ajoute d'autres! 🚀
