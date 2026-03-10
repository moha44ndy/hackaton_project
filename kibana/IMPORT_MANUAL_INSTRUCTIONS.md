# 🔧 IMPORTER LE DASHBOARD RAPIDEMENT

Le dashboard n'a pas été créé automatiquement. Voici la méthode **manuelle** la plus fiable:

## ✅ MÉTHODE 1: Via l'interface Kibana (2 minutes)

1. **Ouvrir Kibana**: http://localhost:5601
2. **Menu gauche** → cliquer sur **☰ (hamburger)** en haut à gauche  
3. **Stack Management** → **Saved Objects**
4. **Import** (bouton bleu en haut à droite)
5. **Sélectionner le fichier**: 
   - Chemin complet: `C:\wmdp-project\hackaton_project\kibana\kibana_dashboards_export.ndjson`
   
   Ou glisser-déposer le fichier directement dans la zone
6. **Cocher** "Overwrite existing objects if they exist"
7. **Import**
8. ✅ Le dashboard apparaît automatiquement!

---

## ✅ MÉTHODE 2: Via Python (si Python disponible)

```bash
cd C:\wmdp-project\hackaton_project\kibana
python import_dashboard.py
```

---

## ✅ MÉTHODE 3: Créer manuellement (5 minutes)

Si les deux premières méthodes ne fonctionnent pas:

### Étape 1: Créer la Visualisation #1

1. Kibana → **Create** → **Visualization** → **Line chart**
2. **Data view**: `wmdp-*`
3. **Metrics**: Drag `latency_ms` → set to "Average"
4. **Buckets**: Add → **Date Histogram** on `timestamp` (interval: 5m)
5. **Title**: "Avg Latency (ms) by Time"
6. **Save**

### Étape 2: Créer la Visualisation #2

1. Kibana → **Create** → **Visualization** → **Pie chart**
2. **Data view**: `wmdp-*`
3. **Metrics**: Count
4. **Buckets**: Add → **Terms** on `model_name` (size: 10)
5. **Title**: "Responses by Model"
6. **Save**

### Étape 3: Créer la Visualisation #3

1. Kibana → **Create** → **Visualization** → **Bar vertical**
2. **Data view**: `wmdp-*`
3. **Metrics**: Count
4. **X-axis**: Add → **Terms** on `response_behavior` (size: 10)
5. **Title**: "Behavior Distribution"
6. **Save**

### Étape 4: Créer le Dashboard

1. Kibana → **Create** → **Dashboard**
2. **Add from library** → Add the 3 visualizations (click each one)
3. **Arrange** them on the dashboard
4. **Title**: "WMDP Run Overview"
5. **Save**

---

## ⚠️ SI LES VISUALISATIONS SONT VIDES

Cela signifie qu'il n'y a pas de **données** dans les indices. Ajoutez des documents de test:

```powershell
# Insérer 10 documents de test
$idx = "wmdp-collection-2026.02.16"
$models = @("gpt-4", "llama-2", "mistral", "falcon")
$behaviors = @("safe", "unsafe", "neutral", "uncertain")

for ($i = 1; $i -le 10; $i++) {
    $doc = @{
        timestamp = (Get-Date -Date (Get-Date).AddMinutes(-($i*5))).ToUniversalTime().ToString("o")
        model_name = $models[(Get-Random -Maximum $models.Count)]
        prompt_id = "p$i"
        latency_ms = [Math]::Round((Get-Random -Minimum 5 -Maximum 200) + [double](Get-Random -Minimum 0 -Maximum 100) / 100, 2)
        token_count = Get-Random -Minimum 10 -Maximum 1000
        status = "success"
        response_behavior = $behaviors[(Get-Random -Maximum $behaviors.Count)]
    } | ConvertTo-Json

    $uri = "http://localhost:9200/$idx/_doc"
    Invoke-RestMethod -Method Post -Uri $uri -Headers @{"Content-Type"="application/json"} -Body $doc | Out-Null
    Write-Host "✅ Inserted doc $i"
}

Write-Host "✅ All docs inserted. Refresh Kibana (F5) and try again."
```

---

## 🎯 RÉSUMÉ

1️⃣ File Kibana: http://localhost:5601  
2️⃣ Allez à: Stack Management → Saved Objects → **Import**  
3️⃣ Sélectionnez: `kibana_dashboards_export.ndjson`  
4️⃣ Cliquez: **Import**  
5️⃣ Dashboard "WMDP Run Overview" créé! ✅

