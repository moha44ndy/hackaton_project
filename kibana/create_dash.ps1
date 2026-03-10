# Quick script to create Kibana visualizations and dashboard

$KB = "http://localhost:5601/api/saved_objects"
$h = @{"kbn-xsrf" = "true"}

Write-Host ""
Write-Host "Creating visualizations and dashboard..." -ForegroundColor Cyan
Write-Host ""

# Viz 1
$v1 = @{ 
    attributes = @{ 
        title = "Avg Latency (ms) by Time"
        visState = '{"title":"Avg Latency (ms) by Time","type":"line","params":{"addTooltip":true,"addLegend":true},"aggs":[{"id":"1","type":"avg","params":{"field":"latency_ms"}},{"id":"2","type":"date_histogram","params":{"field":"timestamp","interval":"auto"}}]}'
        uiStateJSON = "{}"
        kibanaSavedObjectMeta = @{ searchSourceJSON = '{"index":"wmdp-*","query":{"match_all":{}}}' }
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post -Uri "$KB/visualization/wmdp-viz-latency-trend" -Headers $h -Body $v1 -ContentType "application/json" -ErrorAction SilentlyContinue | Out-Null
Write-Host "✅ Visualization 1: Latency Trend"

# Viz 2  
$v2 = @{
    attributes = @{
        title = "Responses by Model"
        visState = '{"title":"Responses by Model","type":"pie","params":{"addTooltip":true,"addLegend":true},"aggs":[{"id":"1","type":"count"},{"id":"2","type":"terms","params":{"field":"model_name","size":10}}]}'
        uiStateJSON = "{}"
        kibanaSavedObjectMeta = @{ searchSourceJSON = '{"index":"wmdp-*","query":{"match_all":{}}}' }
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post -Uri "$KB/visualization/wmdp-viz-responses-by-model" -Headers $h -Body $v2 -ContentType "application/json" -ErrorAction SilentlyContinue | Out-Null
Write-Host "✅ Visualization 2: Responses by Model"

# Viz 3
$v3 = @{
    attributes = @{
        title = "Behavior Distribution"
        visState = '{"title":"Behavior Distribution","type":"histogram","params":{"addTooltip":true,"addLegend":true},"aggs":[{"id":"1","type":"count"},{"id":"2","type":"terms","params":{"field":"response_behavior","size":10}}]}'
        uiStateJSON = "{}"
        kibanaSavedObjectMeta = @{ searchSourceJSON = '{"index":"wmdp-*","query":{"match_all":{}}}' }
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post -Uri "$KB/visualization/wmdp-viz-behavior-distribution" -Headers $h -Body $v3 -ContentType "application/json" -ErrorAction SilentlyContinue | Out-Null
Write-Host "✅ Visualization 3: Behavior Distribution"

# Dashboard
$d = @{
    attributes = @{
        title = "WMDP Run Overview"
        description = "WMDP Dashboard"
        panels = @(
            @{ version = "8.5.0"; gridData = @{ x = 0; y = 0; w = 24; h = 15 }; type = "visualization"; id = "wmdp-viz-latency-trend" }
            @{ version = "8.5.0"; gridData = @{ x = 24; y = 0; w = 12; h = 15 }; type = "visualization"; id = "wmdp-viz-responses-by-model" }
            @{ version = "8.5.0"; gridData = @{ x = 36; y = 0; w = 12; h = 15 }; type = "visualization"; id = "wmdp-viz-behavior-distribution" }
        )
        timeRestore = $false
        timeFrom = "now-7d"
        timeTo = "now"
        refreshInterval = @{ pause = $true; value = 0 }
        uiStateJSON = "{}"
        kibanaSavedObjectMeta = @{ searchSourceJSON = '{"query":{"match_all":{}}}' }
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method Post -Uri "$KB/dashboard/wmdp-overview-dashboard" -Headers $h -Body $d -ContentType "application/json" -ErrorAction SilentlyContinue | Out-Null
Write-Host "✅ Dashboard: WMDP Run Overview"

Write-Host ""
Write-Host "Dashboard URL:" -ForegroundColor Green
Write-Host "http://localhost:5601/app/dashboards/wmdp-overview-dashboard"
Write-Host ""
