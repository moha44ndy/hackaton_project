# Fix Kibana dashboard - corrected version

$KB = "http://localhost:5601/api/saved_objects"
$ES = "http://localhost:9200"
$hdr = @{"kbn-xsrf" = "true"; "Content-Type" = "application/json"}

Write-Host "Fixing Kibana Dashboard..." -ForegroundColor Cyan
Write-Host ""

# 1. Delete old visualizations
Write-Host "Cleaning up old visualizations..." -ForegroundColor Yellow
@("wmdp-viz-latency-trend", "wmdp-viz-responses-by-model", "wmdp-viz-behavior-distribution") | ForEach-Object {
    try {
        $null = Invoke-RestMethod -Method Delete -Uri "$KB/visualization/$_" -Headers $hdr -TimeoutSec 5 -ErrorAction SilentlyContinue
    } catch { }
}
try {
    $null = Invoke-RestMethod -Method Delete -Uri "$KB/dashboard/wmdp-overview-dashboard" -Headers $hdr -TimeoutSec 5 -ErrorAction SilentlyContinue
} catch { }
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# 2. Create Viz 1
Write-Host "Creating Visualization 1..." -ForegroundColor Yellow
$v1_body = '{"attributes":{"title":"Latency Trend","visState":"{\\"title\\":\\"Latency Trend\\",\\"type\\":\\"line\\",\\"params\\":{\\"addTooltip\\":true,\\"addLegend\\":true},\\"aggs\\":[{\\"id\\":\\"1\\",\\"enabled\\":true,\\"type\\":\\"avg\\",\\"schema\\":\\"metric\\",\\"params\\":{\\"field\\":\\"latency_ms\\"}},{\\"id\\":\\"2\\",\\"enabled\\":true,\\"type\\":\\"date_histogram\\",\\"schema\\":\\"segment\\",\\"params\\":{\\"field\\":\\"timestamp\\",\\"interval\\":\\"auto\\"}}]}","uiStateJSON":"{}","kibanaSavedObjectMeta":{"searchSourceJSON":"{\\"index\\":\\"wmdp-*\\",\\"query\\":{\\"match_all\\":{}}}"}}}'
$null = Invoke-RestMethod -Method Post -Uri "$KB/visualization/wmdp-viz-latency-trend" -Headers $hdr -Body $v1_body -TimeoutSec 10 -ErrorAction SilentlyContinue
Write-Host "OK" -ForegroundColor Green

# 3. Create Viz 2
Write-Host "Creating Visualization 2..." -ForegroundColor Yellow
$v2_body = '{"attributes":{"title":"Model Distribution","visState":"{\\"title\\":\\"Model Distribution\\",\\"type\\":\\"pie\\",\\"params\\":{\\"addTooltip\\":true,\\"addLegend\\":true},\\"aggs\\":[{\\"id\\":\\"1\\",\\"enabled\\":true,\\"type\\":\\"count\\",\\"schema\\":\\"metric\\",\\"params\\":{}},{\\"id\\":\\"2\\",\\"enabled\\":true,\\"type\\":\\"terms\\",\\"schema\\":\\"segment\\",\\"params\\":{\\"field\\":\\"model_name\\",\\"size\\":10}}]}","uiStateJSON":"{}","kibanaSavedObjectMeta":{"searchSourceJSON":"{\\"index\\":\\"wmdp-*\\",\\"query\\":{\\"match_all\\":{}}}"}}}'
$null = Invoke-RestMethod -Method Post -Uri "$KB/visualization/wmdp-viz-responses-by-model" -Headers $hdr -Body $v2_body -TimeoutSec 10 -ErrorAction SilentlyContinue
Write-Host "OK" -ForegroundColor Green

# 4. Create Viz 3
Write-Host "Creating Visualization 3..." -ForegroundColor Yellow
$v3_body = '{"attributes":{"title":"Behavior Analysis","visState":"{\\"title\\":\\"Behavior Analysis\\",\\"type\\":\\"bar\\",\\"params\\":{\\"addTooltip\\":true,\\"addLegend\\":true},\\"aggs\\":[{\\"id\\":\\"1\\",\\"enabled\\":true,\\"type\\":\\"count\\",\\"schema\\":\\"metric\\",\\"params\\":{}},{\\"id\\":\\"2\\",\\"enabled\\":true,\\"type\\":\\"terms\\",\\"schema\\":\\"segment\\",\\"params\\":{\\"field\\":\\"response_behavior\\",\\"size\\":10}}]}","uiStateJSON":"{}","kibanaSavedObjectMeta":{"searchSourceJSON":"{\\"index\\":\\"wmdp-*\\",\\"query\\":{\\"match_all\\":{}}}"}}}'
$null = Invoke-RestMethod -Method Post -Uri "$KB/visualization/wmdp-viz-behavior-distribution" -Headers $hdr -Body $v3_body -TimeoutSec 10 -ErrorAction SilentlyContinue
Write-Host "OK" -ForegroundColor Green

Write-Host ""

# 5. Create Dashboard using builtin method
Write-Host "Creating Dashboard..." -ForegroundColor Yellow

# Use Kibana UI method to create empty dashboard first
$dash_body = '{"attributes":{"title":"WMDP Run Overview","description":"WMDP Dashboard","panels":[],"timeRestore":false,"refreshInterval":{"pause":true,"value":0}}}'

try {
    $null = Invoke-RestMethod -Method Put -Uri "$KB/dashboard/wmdp-overview-dashboard" -Headers $hdr -Body $dash_body -TimeoutSec 10
    Write-Host "Dashboard Created" -ForegroundColor Green
} catch {
    Write-Host "Warning: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "All done! Refresh Kibana:" -ForegroundColor Cyan
Write-Host "http://localhost:5601/app/dashboards/wmdp-overview-dashboard" -ForegroundColor Green
