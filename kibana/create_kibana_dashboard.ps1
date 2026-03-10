# Create Kibana visualizations and dashboard via API

$KibanaAPI = "http://localhost:5601/api/saved_objects"
$hdr = @{"kbn-xsrf" = "true"}

Write-Host "🚀 Creating Kibana visualizations and dashboard..." -ForegroundColor Cyan

# Visualization 1: Avg Latency by Time
Write-Host "`n1️⃣ Creating 'Avg Latency (ms) by Time'..." -ForegroundColor Yellow

$viz1State = @{
    title = "Avg Latency (ms) by Time"
    type = "line"
    params = @{
        addTooltip = $true
        addLegend = $true
        legendPosition = "bottom"
        grid = @{ categoryLines = $false; style = @{ color = "#eee" }}
    }
    aggs = @(
        @{ id = "1"; enabled = $true; type = "avg"; schema = "metric"; params = @{ field = "latency_ms" }}
        @{ id = "2"; enabled = $true; type = "date_histogram"; schema = "segment"; params = @{ field = "timestamp"; interval = "auto" }}
    )
}

$viz1Body = @{
    attributes = @{
        title = "Avg Latency (ms) by Time"
        visState = ($viz1State | ConvertTo-Json -Depth 10)
        uiStateJSON = "{}"
        kibanaSavedObjectMeta = @{
            searchSourceJSON = @{ index = "wmdp-*"; query = @{ match_all = @{} } } | ConvertTo-Json
        }
    }
} | ConvertTo-Json -Depth 10

try {
    $r1 = Invoke-RestMethod -Method Post -Uri "$KibanaAPI/visualization/wmdp-viz-latency-trend" -Headers $hdr -Body $viz1Body -ContentType "application/json" -TimeoutSec 10
    Write-Host "✅ Created: Avg Latency by Time" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

# Visualization 2: Responses by Model
Write-Host "`n2️⃣ Creating 'Responses by Model'..." -ForegroundColor Yellow

$viz2State = @{
    title = "Responses by Model"
    type = "pie"
    params = @{
        addTooltip = $true
        addLegend = $true
        legendPosition = "right"
        isDonut = $false
    }
    aggs = @(
        @{ id = "1"; enabled = $true; type = "count"; schema = "metric"; params = @{} }
        @{ id = "2"; enabled = $true; type = "terms"; schema = "segment"; params = @{ field = "model_name"; size = 10 }}
    )
}

$viz2Body = @{
    attributes = @{
        title = "Responses by Model"
        visState = ($viz2State | ConvertTo-Json -Depth 10)
        uiStateJSON = "{}"
        kibanaSavedObjectMeta = @{
            searchSourceJSON = @{ index = "wmdp-*"; query = @{ match_all = @{} } } | ConvertTo-Json
        }
    }
} | ConvertTo-Json -Depth 10

try {
    $r2 = Invoke-RestMethod -Method Post -Uri "$KibanaAPI/visualization/wmdp-viz-responses-by-model" -Headers $hdr -Body $viz2Body -ContentType "application/json" -TimeoutSec 10
    Write-Host "✅ Created: Responses by Model" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

# Visualization 3: Behavior Distribution
Write-Host "`n3️⃣ Creating 'Behavior Distribution'..." -ForegroundColor Yellow

$viz3State = @{
    title = "Behavior Distribution"
    type = "histogram"
    params = @{
        addTooltip = $true
        addLegend = $true
        legendPosition = "bottom"
    }
    aggs = @(
        @{ id = "1"; enabled = $true; type = "count"; schema = "metric"; params = @{} }
        @{ id = "2"; enabled = $true; type = "terms"; schema = "segment"; params = @{ field = "response_behavior"; size = 10 }}
    )
}

$viz3Body = @{
    attributes = @{
        title = "Behavior Distribution"
        visState = ($viz3State | ConvertTo-Json -Depth 10)
        uiStateJSON = "{}"
        kibanaSavedObjectMeta = @{
            searchSourceJSON = @{ index = "wmdp-*"; query = @{ match_all = @{} } } | ConvertTo-Json
        }
    }
} | ConvertTo-Json -Depth 10

try {
    $r3 = Invoke-RestMethod -Method Post -Uri "$KibanaAPI/visualization/wmdp-viz-behavior-distribution" -Headers $hdr -Body $viz3Body -ContentType "application/json" -TimeoutSec 10
    Write-Host "✅ Created: Behavior Distribution" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

# Create Dashboard
Write-Host "`n📊 Creating Dashboard 'WMDP Run Overview'..." -ForegroundColor Yellow

$dashboardBody = @{
    attributes = @{
        title = "WMDP Run Overview"
        description = "Dashboard for WMDP latency, model distribution, and behavior analysis"
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
        timeFrom = "now-7d"
        timeTo = "now"
        refreshInterval = @{ pause = $true; value = 0 }
        uiStateJSON = "{}"
        kibanaSavedObjectMeta = @{
            searchSourceJSON = @{ query = @{ match_all = @{} } } | ConvertTo-Json
        }
    }
} | ConvertTo-Json -Depth 10

try {
    $rDash = Invoke-RestMethod -Method Post -Uri "$KibanaAPI/dashboard/wmdp-overview-dashboard" -Headers $hdr -Body $dashboardBody -ContentType "application/json" -TimeoutSec 10
    Write-Host "✅ Created: WMDP Run Overview Dashboard" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

Write-Host "`n🎉 Done! Dashboard available at:" -ForegroundColor Cyan
Write-Host "http://localhost:5601/app/dashboards/wmdp-overview-dashboard" -ForegroundColor Green
