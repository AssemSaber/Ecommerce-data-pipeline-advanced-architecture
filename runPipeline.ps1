

$ErrorActionPreference = "Stop"



$ROOT = "H:\Atos"

$PYTHON = "$ROOT\Ecommerce\sourceAPIs\venv\Scripts\python.exe"

$VENV = "$ROOT\Ecommerce\sourceAPIs\venv\Scripts\activate"

$BRONZE_PATH = "$ROOT\Ecommerce\Bronze"
$SILVER_PATH = "$ROOT\Ecommerce\Silver"
$GOLD_PATH   = "$ROOT\Ecommerce\Gold"
$API_PATH    = "$ROOT\Ecommerce\sourceAPIs\API"


# ------------------------------------------
# Tables + Scripts
# ------------------------------------------

$BRONZE_SCRIPTS = @(
    @{ Table = "customers";   Script = "customers.py" },
    @{ Table = "orders";      Script = "orders.py" },
    @{ Table = "payments";    Script = "payments.py" },
    @{ Table = "reviews";     Script = "reviews.py" }
    @{ Table = "sellers"; Script = "sellers.py" },
    @{ Table = "products"; Script = "products.py" },
    @{ Table = "order_items"; Script = "order_items.py" }
)

$SILVER_SCRIPTS = @(
    @{ Table = "customers";   Script = "customers.py" },
    @{ Table = "orders";      Script = "orders.py" },
    @{ Table = "payments";    Script = "payments.py" },
    @{ Table = "reviews";     Script = "reviews.py" }
    @{ Table = "sellers"; Script = "sellers.py" },
    @{ Table = "products"; Script = "products.py" },
    @{ Table = "order_items"; Script = "order_items.py" }
)

$GOLD_SCRIPTS = @(
    @{ Table = "dim_customers"; Script = "customers.py" },
    @{ Table = "dim_products";  Script = "products.py" },
    @{ Table = "dim_sellers";   Script = "sellers.py" },
    @{ Table = "dim_status_payments";   Script = "status_payments.py" },
    @{ Table = "fact_orders";   Script = "orders.py" }
)


# ==========================================
# 1. Activate Virtual Environment
# ==========================================

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Activating Virtual Environment..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

& $VENV


# ==========================================
# 2. Run APIs First
# ==========================================

Write-Host ""
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "STEP 1 - Running APIs" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow

Write-Host "[API] Starting Payments API..." -ForegroundColor Green

Start-Process $PYTHON `
    -ArgumentList "-m uvicorn main:app --host 127.0.0.1 --port 8000" `
    -WorkingDirectory $API_PATH `
    -NoNewWindow
Write-Host "[API] Main API finished." -ForegroundColor Green




# ==========================================
# 3. Bronze
# ==========================================

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "STEP 2 - BRONZE LAYER" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan


foreach ($item in $BRONZE_SCRIPTS) {

    Write-Host ""
    Write-Host "[BRONZE] Loading table: $($item.Table)" -ForegroundColor Green
    Write-Host "[BRONZE] Script: $($item.Script)" -ForegroundColor Gray

    python "$BRONZE_PATH\$($item.Script)"

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Bronze script failed: $($item.Script)" -ForegroundColor Red
        exit 1
    }

    Write-Host "[BRONZE] $($item.Table) completed successfully." -ForegroundColor Green
}


# ==========================================
# 4. Silver
# ==========================================

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "STEP 3 - SILVER LAYER" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan


foreach ($item in $SILVER_SCRIPTS) {

    Write-Host ""
    Write-Host "[SILVER] Processing table: $($item.Table)" -ForegroundColor Green
    Write-Host "[SILVER] Script: $($item.Script)" -ForegroundColor Gray

    python "$SILVER_PATH\$($item.Script)"

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Silver script failed: $($item.Script)" -ForegroundColor Red
        exit 1
    }

    Write-Host "[SILVER] $($item.Table) completed successfully." -ForegroundColor Green
}


# ==========================================
# 5. Gold
# ==========================================

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "STEP 4 - GOLD LAYER" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan


foreach ($item in $GOLD_SCRIPTS) {

    Write-Host ""
    Write-Host "[GOLD] Processing table: $($item.Table)" -ForegroundColor Green
    Write-Host "[GOLD] Script: $($item.Script)" -ForegroundColor Gray

    python "$GOLD_PATH\$($item.Script)"

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Gold script failed: $($item.Script)" -ForegroundColor Red
        exit 1
    }

    Write-Host "[GOLD] $($item.Table) completed successfully." -ForegroundColor Green
}


# ==========================================
# Pipeline Finished
# ==========================================

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "PIPELINE COMPLETED SUCCESSFULLY" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green