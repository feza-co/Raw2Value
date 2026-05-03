# Smoke test — 7 endpoint (qa_smoke.sh PowerShell port'u, jq gerektirmez).
$ErrorActionPreference = "Stop"
$BASE = "http://localhost:8000"
$EMAIL = "admin@raw2value.local"
$PASS  = "admin123"

function Show-Pass($name, $extra="") { Write-Host "  PASS  $name $extra" -ForegroundColor Green }
function Show-Fail($name, $err) { Write-Host "  FAIL  $name -> $err" -ForegroundColor Red; exit 1 }

# 1. Health
try { $r = Invoke-RestMethod "$BASE/health"; Show-Pass "/health" "(uptime=$($r.uptime_sec)s)" } catch { Show-Fail "/health" $_ }

# 2. FX (public)
try { $r = Invoke-RestMethod "$BASE/api/fx/current"; Show-Pass "/api/fx/current" "(usd=$($r.usd_try) eur=$($r.eur_try) src=$($r.source))" } catch { Show-Fail "/api/fx/current" $_ }

# 3. Login
try {
    $form = @{ username = $EMAIL; password = $PASS }
    $login = Invoke-RestMethod -Method Post -Uri "$BASE/api/auth/login" -Body $form
    $TOKEN = $login.access_token
    if (-not $TOKEN) { Show-Fail "/api/auth/login" "no access_token" }
    Show-Pass "/api/auth/login" "(token=$($TOKEN.Substring(0,20))...)"
} catch { Show-Fail "/api/auth/login" $_ }

$AUTH = @{ Authorization = "Bearer $TOKEN" }

# 4. Me
try { $r = Invoke-RestMethod -Uri "$BASE/api/auth/me" -Headers $AUTH; Show-Pass "/api/auth/me" "(email=$($r.email) role=$($r.role))" } catch { Show-Fail "/api/auth/me" $_ }

# 5. Analyze
try {
    $body = @{
        raw_material   = "pomza"
        tonnage        = 150
        quality        = "A"
        origin_city    = "Nevşehir"
        target_country = "DE"
        target_city    = "Hamburg"
        transport_mode = "kara"
        priority       = "max_profit"
        input_mode     = "basic"
    } | ConvertTo-Json -Compress
    $r = Invoke-RestMethod -Method Post -Uri "$BASE/api/analyze" -Headers $AUTH -ContentType "application/json" -Body $body
    if (-not $r.recommended_route) { Show-Fail "/api/analyze" "no recommended_route" }
    Show-Pass "/api/analyze" "(route=$($r.recommended_route) profit=$([math]::Round($r.expected_profit_try)) ms=$($r.duration_ms))"
} catch { Show-Fail "/api/analyze" $_ }

# 6. What-if
try {
    $body = @{
        base_payload = @{
            raw_material   = "pomza"
            tonnage        = 150
            quality        = "A"
            origin_city    = "Nevşehir"
            target_country = "DE"
            target_city    = "Hamburg"
            transport_mode = "kara"
            priority       = "max_profit"
            input_mode     = "basic"
        }
        scenarios = @(
            @{ name = "down10"; fx_scenario_pct = -0.10 },
            @{ name = "up10";   fx_scenario_pct =  0.10 }
        )
    } | ConvertTo-Json -Compress -Depth 5
    $r = Invoke-RestMethod -Method Post -Uri "$BASE/api/what-if" -Headers $AUTH -ContentType "application/json" -Body $body
    if ($r.results.Count -ne 2) { Show-Fail "/api/what-if" "expected 2 results got $($r.results.Count)" }
    Show-Pass "/api/what-if" "(2 scenarios; ms=$($r.duration_ms))"
} catch { Show-Fail "/api/what-if" $_ }

# 7. Model evidence (public)
try {
    $r = Invoke-RestMethod "$BASE/api/model-evidence"
    if ($r.profit_regression.best_model -ne "catboost") { Show-Fail "/api/model-evidence" "expected catboost got $($r.profit_regression.best_model)" }
    Show-Pass "/api/model-evidence" "(profit=$($r.profit_regression.best_model) route=$($r.route_classifier.best_model))"
} catch { Show-Fail "/api/model-evidence" $_ }

Write-Host ""
Write-Host "ALL OK (7/7)" -ForegroundColor Green
