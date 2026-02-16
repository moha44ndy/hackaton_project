# 📊 IMPORTER LE DASHBOARD KIBANA

Le dashboard **WMDP Run Overview** contient 3 visualisations:
1. **Avg Latency (ms) by Time** — Graphique linéaire montrant l'évolution de la latence moyenne par timestamp
2. **Responses by Model** — Camembert montrant la distribution des réponses par modèle
3. **Behavior Distribution** — Histogramme montrant la distribution des comportements observés

---

## 📝 OPTION 1: Import via API (PowerShell / Bash)

### Sur PowerShell (Windows)

```powershell
$uri = 'http://localhost:5601/api/saved_objects/_import?overwrite=true'
$file = 'C:\wmdp-project\hackaton_project\kibana\kibana_dashboards_export.ndjson'
$hdr = @{'kbn-xsrf' = 'true'; 'Content-Type' = 'application/x-ndjson'}

$content = Get-Content $file -Raw
$response = Invoke-RestMethod -Method Post -Uri $uri -Headers $hdr -Body $content

Write-Host $response | ConvertTo-Json
```

### Sur Linux / Mac (bash + curl)

```bash
curl -X POST \
  "http://localhost:5601/api/saved_objects/_import?overwrite=true" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @kibana_dashboards_export.ndjson
```

---

## 🖱️ OPTION 2: Import via Interface Kibana

1. Ouvrir http://localhost:5601
2. Aller à **Stack Management** → **Saved Objects**
3. Cliquer **Import** en haut à droite
4. Sélectionner le fichier: `kibana_dashboards_export.ndjson`
5. Cocher **Overwrite existing objects if they exist**
6. Cliquer **Import**

---

## ✅ OPTION 3: Création Manuelle (pas à pas)

### Étape 1: Créer la Visualisation "Avg Latency by Time"

1. Kibana → **Visualize Library** → **Create visualization**
2. Choisir **Line** chart
3. **Data view**: `wmdp-*`
4. **Metrics**: Drag `latency_ms` → set to **Average**
5. **Buckets**: Add aggregation → **Date Histogram** on `timestamp` (interval: Auto)
6. **Title**: "Avg Latency (ms) by Time"
7. **Save**

### Étape 2: Créer la Visualisation "Responses by Model"

1. Kibana → **Visualize Library** → **Create visualization**
2. Choisir **Pie** chart
3. **Data view**: `wmdp-*`
4. **Metrics**: Count (default)
5. **Buckets**: Add aggregation → **Terms** on `model_name` (size: 10)
6. **Title**: "Responses by Model"
7. **Save**

### Étape 3: Créer la Visualisation "Behavior Distribution"

1. Kibana → **Visualize Library** → **Create visualization**
2. Choisir **Vertical Bar** (ou Histogram)
3. **Data view**: `wmdp-*`
4. **Metrics**: Count
5. **X-axis**: Add aggregation → **Terms** on `response_behavior` (size: 10)
6. **Title**: "Behavior Distribution"
7. **Save**

### Étape 4: Créer le Dashboard

1. Kibana → **Dashboard** → **Create dashboard**
2. **Add from library** → sélectionner les 3 visualisations
3. Arrange les panneaux (resize, drag)
4. **Title**: "WMDP Run Overview"
5. **Save**

---

## 🔍 VÉRIFICATION

Une fois le dashboard créé, vous devriez voir:

```
✅ 1 ligne de visalisations (Avg Latency) 
✅ 1 pie chart (Responses by Model)
✅ 1 histogramme (Behavior Distribution)
✅ Date picker en haut pour filtrer par plage temporelle
```

Si les visualisations sont **vides**:
- Vérifier que des documents existent: **Discover** → `wmdp-*` → chercher "match_all"
- Vérifier les types de champs dans **Stack Management** → **Index Patterns** → `wmdp-*`

---

## 📲 AJOUTER DES DOCUMENTS DE TEST

Si l'index est vide, insérer des documents de test:

```powershell
$base = 'http://localhost:9200'
$idx = 'wmdp-collection-2026.02.16'

# Insérer 5 documents de test
for ($i = 1; $i -le 5; $i++) {
    $doc = @{
        timestamp = (Get-Date).ToUniversalTime().ToString("o")
        model_name = @("gpt-4", "llama-2", "mistral")[(Get-Random -Maximum 3)]
        prompt_id = "p$i"
        latency_ms = Get-Random -Minimum 5 -Maximum 100
        token_count = Get-Random -Minimum 10 -Maximum 1000
        status = "success"
        response_behavior = @("safe", "harmful", "neutral")[(Get-Random -Maximum 3)]
    } | ConvertTo-Json

    Invoke-RestMethod -Method Post `
        -Uri "$base/$idx/_doc" `
        -Headers @{'Content-Type' = 'application/json'} `
        -Body $doc | Out-Null
    
    Write-Host "✅ Inserted doc $i"
}
```

Puis rafraîchir Kibana (F5) pour voir les visualisations se remplir.

---

## 🔧 TROUBLESHOOTING

### Les visualisations sont vides
→ Vérifier qu'il y a des documents: Discover → `wmdp-*` → "Got X results"

### "Cannot find field latency_ms"
→ Aller à **Stack Management** → **Index Patterns** → `wmdp-*` → **Refresh field list**

### Le pie chart montre "No data"
→ Vérifier que `model_name` existe dans les documents (field mapping)

### "Saved objects not found"
→ Vérifier l'ID correct: **Stack Management** → **Saved Objects** → list all

---

## 📚 NEXT STEPS

Après l'import du dashboard:
1. ✅ Naviguer à **Dashboard** → "WMDP Run Overview"
2. ✅ Utiliser le **time picker** pour filtrer par plage
3. ✅ Cliquer sur des slices/bars pour appliquer des filtres
4. ✅ Ajouter plus de visualisations (heatmaps, tables, etc.)
5. ✅ Exporter le dashboard pour partage/backup

