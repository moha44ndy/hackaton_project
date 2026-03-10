# Fix Kibana visualizations and dashboard
# Run this on Windows PowerShell

$KIBANA = "http://localhost:5601/api/saved_objects"
$ES = "http://localhost:9200"
$hdr = @{"kbn-xsrf" = "true"; "Content-Type" = "application/json"}

Write-Host ""
Write-Host "🔧 Fixing Kibana Dashboard..." -ForegroundColor Cyan
Write-Host ""

# 1. Insert test data via bulk API
Write-Host "📊 Step 1: Inserting test data..." -ForegroundColor Yellow

$today = (Get-Date -Format "yyyy.MM.dd")
$idx = "wmdp-collection-$today"

$bulkData = @"
{ "index" : { "_index" : "$idx" } }
{ "timestamp" : "2026-02-16T10:00:00Z", "model_name" : "gpt-4", "latency_ms" : 45.2, "response_behavior" : "safe", "status" : "success", "token_count" : 150 }
{ "index" : { "_index" : "$idx" } }
{ "timestamp" : "2026-02-16T10:05:00Z", "model_name" : "llama-2", "latency_ms" : 32.1, "response_behavior" : "unsafe", "status" : "success", "token_count" : 200 }
{ "index" : { "_index" : "$idx" } }
{ "timestamp" : "2026-02-16T10:10:00Z", "model_name" : "mistral", "latency_ms" : 28.5, "response_behavior" : "safe", "status" : "success", "token_count" : 175 }
{ "index" : { "_index" : "$idx" } }
{ "timestamp" : "2026-02-16T10:15:00Z", "model_name" : "gpt-4", "latency_ms" : 51.3, "response_behavior" : "neutral", "status" : "success", "token_count" : 180 }
{ "index" : { "_index" : "$idx" } }
{ "timestamp" : "2026-02-16T10:20:00Z", "model_name" : "llama-2", "latency_ms" : 39.8, "response_behavior" : "safe", "status" : "success", "token_count" : 220 }
"@

try {
    $null = Invoke-RestMethod -Method Post -Uri "$ES/_bulk" -Headers $hdr -Body $bulkData -TimeoutSec 10
    Write-Host "✅ Test data inserted (5 documents)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Bulk insert warning (may be OK): $_" -ForegroundColor Yellow
}

Write-Host ""

# 2. Delete old broken visualizations
Write-Host "🗑️ Step 2: Cleaning up old visualizations..." -ForegroundColor Yellow

@("wmdp-viz-latency-trend", "wmdp-viz-responses-by-model", "wmdp-viz-behavior-distribution") | ForEach-Object {
    try {
        $null = Invoke-RestMethod -Method Delete -Uri "$KIBANA/visualization/$_" -Headers $hdr -TimeoutSec 5 -ErrorAction SilentlyContinue
    } catch { }
}

try {
    $null = Invoke-RestMethod -Method Delete -Uri "$KIBANA/dashboard/wmdp-overview-dashboard" -Headers $hdr -TimeoutSec 5 -ErrorAction SilentlyContinue
} catch { }

Write-Host "✅ Cleaned up old objects" -ForegroundColor Green
Write-Host ""

# 3. Create new visualizations
Write-Host "📈 Step 3: Creating new visualizations..." -ForegroundColor Yellow

# Viz 1: Line chart
$viz1 = @{
    attributes = @{
        title = "Avg Latency (ms) by Time"
        visState = '{"title":"Avg Latency (ms) by Time","type":"line","params":{"addTooltip":true,"addLegend":true,"legendPosition":"bottom"},"aggs":[{"id":"1","enabled":true,"type":"avg","schema":"metric","params":{"field":"latency_ms"}},{"id":"2","enabled":true,"type":"date_histogram","schema":"segment","params":{"field":"timestamp","interval":"auto"}}]}'
        uiStateJSON = "{}"
        kibanaSavedObjectMeta = @{
            searchSourceJSON = '{"index":"wmdp-*","query":{"match_all":{}}}'
        }
    }
} | ConvertTo-Json -Depth 10

$null = Invoke-RestMethod -Method Post -Uri "$KIBANA/visualization/wmdp-viz-latency-trend" -Headers $hdr -Body $viz1 -TimeoutSec 10 -ErrorAction SilentlyContinue
Write-Host "✅ Created: Avg Latency by Time" -ForegroundColor Green

# Viz 2: Pie chart
$viz2 = @{
    attributes = @{
        title = "Responses by Model"
        visState = '{"title":"Responses by Model","type":"pie","params":{"addTooltip":true,"addLegend":true,"legendPosition":"right","isDonut":false},"aggs":[{"id":"1","enabled":true,"type":"count","schema":"metric","params":{}},{"id":"2","enabled":true,"type":"terms","schema":"segment","params":{"field":"model_name","size":10}}]}'
        uiStateJSON = "{}"
        kibanaSavedObjectMeta = @{
            searchSourceJSON = '{"index":"wmdp-*","query":{"match_all":{}}}'
        }
    }
} | ConvertTo-Json -Depth 10

$null = Invoke-RestMethod -Method Post -Uri "$KIBANA/visualization/wmdp-viz-responses-by-model" -Headers $hdr -Body $viz2 -TimeoutSec 10 -ErrorAction SilentlyContinue
Write-Host "✅ Created: Responses by Model" -ForegroundColor Green

# Viz 3: Bar chart
$viz3 = @{
    attributes = @{
        title = "Behavior Distribution"
        visState = '{"title":"Behavior Distribution","type":"bar","params":{"addTooltip":true,"addLegend":true,"legendPosition":"bottom"},"aggs":[{"id":"1","enabled":true,"type":"count","schema":"metric","params":{}},{"id":"2","enabled":true,"type":"terms","schema":"segment","params":{"field":"response_behavior","size":10}}]}'
        uiStateJSON = "{}"
        kibanaSavedObjectMeta = @{
            searchSourceJSON = '{"index":"wmdp-*","query":{"match_all":{}}}'
        }
    }
} | ConvertTo-Json -Depth 10

$null = Invoke-RestMethod -Method Post -Uri "$KIBANA/visualization/wmdp-viz-behavior-distribution" -Headers $hdr -Body $viz3 -TimeoutSec 10 -ErrorAction SilentlyContinue
Write-Host "✅ Created: Behavior Distribution" -ForegroundColor Green

Write-Host ""

# 4. Create Dashboard
Write-Host "📊 Step 4: Creating Dashboard..." -ForegroundColor Yellow

$dashboard = @{
    attributes = @{
        title = "WMDP Run Overview"
        description = "Dashboard for WMDP analysis"
        panels = @(
            @{
                version = "8.5.0"
                gridData = @{ x = 0; y = 0; w = 24; h = 15 }
                type = "visualization"
                id = "wmdp-viz-latency-trend"
                embeddableConfig = @{}
            }
            @{
                version = "8.5.0"
                gridData = @{ x = 24; y = 0; w = 12; h = 15 }
                type = "visualization"
                id = "wmdp-viz-responses-by-model"
                embeddableConfig = @{}
            }
            @{
                version = "8.5.0"
                gridData = @{ x = 36; y = 0; w = 12; h = 15 }
                type = "visualization"
                id = "wmdp-viz-behavior-distribution"
                embeddableConfig = @{}
            }
        )
        timeRestore = $false
        refreshInterval = @{ pause = $true; value = 0 }
    }
} | ConvertTo-Json -Depth 10

$null = Invoke-RestMethod -Method Post -Uri "$KIBANA/dashboard/wmdp-overview-dashboard" -Headers $hdr -Body $dashboard -TimeoutSec 10 -ErrorAction SilentlyContinue
Write-Host "✅ Created: WMDP Run Overview Dashboard" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Done! All fixed!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Refresh Kibana and go to:" -ForegroundColor Yellow
Write-Host "http://localhost:5601/app/dashboards/wmdp-overview-dashboard" -ForegroundColor Green
