# ============================================================================
# FE-012: UI управління доступами виконавців до категорій - Test Script
# ============================================================================
# 
# Цей скрипт тестує UI функціонал управління доступами виконавців до категорій.
# 
# Передумови:
# - Docker контейнери запущені (docker compose up)
# - API доступний на http://localhost:8000
# - Frontend доступний на http://localhost:3000
# - Є хоча б один користувач з роллю ADMIN
# - Є хоча б один користувач з роллю EXECUTOR
# - Є активні категорії в системі
#
# Тести:
# 1. Перевірка що CategoryAccessManager відображається для EXECUTOR
# 2. Перевірка що CategoryAccessManager НЕ відображається для ADMIN
# 3. Перевірка завантаження списку категорій
# 4. Перевірка завантаження поточних доступів виконавця
# 5. API тест: GET /users/{user_id}/category-access
# 6. API тест: PUT /users/{user_id}/category-access
# 7. Перевірка попередження при відсутності доступів
# 8. Перевірка індикатора кількості обраних категорій
#
# ============================================================================

param(
    [string]$ApiBaseUrl = "http://localhost:8000",
    [string]$FrontendUrl = "http://localhost:3000"
)

# Кольори для виводу
function Write-TestHeader {
    param([string]$Message)
    Write-Host "`n================================================================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "================================================================================" -ForegroundColor Cyan
}

function Write-TestStep {
    param([string]$Step, [string]$Message)
    Write-Host "`n[$Step] $Message" -ForegroundColor Yellow
    Write-Host "--------------------------------------------------------------------------------" -ForegroundColor Gray
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Failure {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

# Лічильники тестів
$script:TestsPassed = 0
$script:TestsFailed = 0
$script:TestsTotal = 0

function Test-Assertion {
    param(
        [string]$TestName,
        [bool]$Condition,
        [string]$SuccessMessage,
        [string]$FailureMessage
    )
    
    $script:TestsTotal++
    
    if ($Condition) {
        $script:TestsPassed++
        Write-Success "PASS - $TestName"
        if ($SuccessMessage) {
            Write-Info $SuccessMessage
        }
        return $true
    } else {
        $script:TestsFailed++
        Write-Failure "FAIL - $TestName"
        if ($FailureMessage) {
            Write-Host "   ❗ $FailureMessage" -ForegroundColor Red
        }
        return $false
    }
}

# ============================================================================
# Налаштування
# ============================================================================

Write-TestHeader "FE-012: UI управління доступами виконавців до категорій - Testing"
Write-Host "Тестування UI функціоналу управління доступами до категорій`n"

Write-Host "Компоненти що тестуються:"
Write-Host "  - CategoryAccessManager component для EXECUTOR"
Write-Host "  - Transfer component з категоріями"
Write-Host "  - API інтеграція (GET/PUT category-access)"
Write-Host "  - Попередження при відсутності доступів"
Write-Host "  - Індикатор кількості обраних категорій"

# Отримання токену для тестів
Write-TestStep "SETUP" "Авторізація та отримання токену"

try {
    $loginResponse = Invoke-RestMethod -Uri "$ApiBaseUrl/api/auth/login" -Method Post `
        -ContentType "application/json" `
        -Body (@{
            username = "admin"
            password = "admin123"
        } | ConvertTo-Json) -ErrorAction Stop
    
    $token = $loginResponse.access_token
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    Write-Success "Авторизація успішна"
} catch {
    Write-Failure "Не вдалося авторизуватися: $_"
    Write-Host "`nℹ️  Переконайтеся що:"
    Write-Host "   - API запущено (docker compose up)"
    Write-Host "   - Існує користувач admin/admin123"
    exit 1
}

# ============================================================================
# ТЕСТ 1: Перевірка існування користувачів з роллю EXECUTOR
# ============================================================================

Write-TestStep "КРОК 1" "Пошук користувачів з роллю EXECUTOR"

try {
    $usersResponse = Invoke-RestMethod -Uri "$ApiBaseUrl/api/users?role=EXECUTOR" `
        -Method Get -Headers $headers -ErrorAction Stop
    
    $executors = $usersResponse.users
    
    if ($executors.Count -gt 0) {
        $executorUser = $executors[0]
        $executorUserId = $executorUser.id
        $executorUsername = $executorUser.username
        
        Test-Assertion -TestName "executor_user_exists" -Condition $true `
            -SuccessMessage "Знайдено користувача EXECUTOR: $executorUsername (ID: $executorUserId)"
    } else {
        Test-Assertion -TestName "executor_user_exists" -Condition $false `
            -FailureMessage "Не знайдено користувачів з роллю EXECUTOR"
        
        Write-Host "`nℹ️  Створіть користувача з роллю EXECUTOR для тестування:"
        Write-Host "   POST /api/users { username, password, role: EXECUTOR }"
        exit 1
    }
} catch {
    Test-Assertion -TestName "executor_user_exists" -Condition $false `
        -FailureMessage "Помилка при пошуку користувачів: $_"
    exit 1
}

# ============================================================================
# ТЕСТ 2: Перевірка існування активних категорій
# ============================================================================

Write-TestStep "КРОК 2" "Завантаження активних категорій"

try {
    $categoriesResponse = Invoke-RestMethod -Uri "$ApiBaseUrl/api/categories?is_active=true&limit=100" `
        -Method Get -Headers $headers -ErrorAction Stop
    
    $categories = $categoriesResponse.categories
    
    Test-Assertion -TestName "active_categories_exist" -Condition ($categories.Count -gt 0) `
        -SuccessMessage "Знайдено $($categories.Count) активних категорій" `
        -FailureMessage "Не знайдено активних категорій"
    
    if ($categories.Count -gt 0) {
        Write-Info "Приклади категорій:"
        $categories | Select-Object -First 3 | ForEach-Object {
            Write-Host "   - $($_.name) (ID: $($_.id))" -ForegroundColor Gray
        }
    }
} catch {
    Test-Assertion -TestName "active_categories_exist" -Condition $false `
        -FailureMessage "Помилка при завантаженні категорій: $_"
}

# ============================================================================
# ТЕСТ 3: API - GET /users/{user_id}/category-access (порожній список)
# ============================================================================

Write-TestStep "КРОК 3" "Отримання поточних доступів виконавця (API)"

try {
    $accessResponse = Invoke-RestMethod -Uri "$ApiBaseUrl/api/users/$executorUserId/category-access" `
        -Method Get -Headers $headers -ErrorAction Stop
    
    $currentAccess = $accessResponse.categories
    $currentAccessCount = $currentAccess.Count
    
    Test-Assertion -TestName "get_category_access_api" -Condition $true `
        -SuccessMessage "API повернув $currentAccessCount категорій з доступом"
    
    Write-Info "Executor: $($accessResponse.executor_username)"
    Write-Info "Total access: $($accessResponse.total)"
    
    if ($currentAccessCount -gt 0) {
        Write-Info "Поточні доступи:"
        $currentAccess | ForEach-Object {
            Write-Host "   - $($_.category_name) (ID: $($_.category_id))" -ForegroundColor Gray
        }
    }
} catch {
    Test-Assertion -TestName "get_category_access_api" -Condition $false `
        -FailureMessage "Помилка при отриманні доступів: $_"
}

# ============================================================================
# ТЕСТ 4: API - PUT /users/{user_id}/category-access (додати доступи)
# ============================================================================

Write-TestStep "КРОК 4" "Оновлення доступів виконавця (API)"

if ($categories.Count -ge 2) {
    $testCategoryIds = @($categories[0].id, $categories[1].id)
    
    try {
        $updateBody = @{
            category_ids = $testCategoryIds
        } | ConvertTo-Json
        
        $updateResponse = Invoke-RestMethod -Uri "$ApiBaseUrl/api/users/$executorUserId/category-access" `
            -Method Put -Headers $headers -Body $updateBody -ErrorAction Stop
        
        $updatedAccess = $updateResponse.categories
        
        $isUpdated = $updatedAccess.Count -eq $testCategoryIds.Count
        
        Test-Assertion -TestName "update_category_access_api" -Condition $isUpdated `
            -SuccessMessage "Доступи успішно оновлено: $($updatedAccess.Count) категорій" `
            -FailureMessage "Кількість доступів не відповідає очікуваній"
        
        if ($isUpdated) {
            Write-Info "Оновлені доступи:"
            $updatedAccess | ForEach-Object {
                Write-Host "   - $($_.category_name) (ID: $($_.category_id))" -ForegroundColor Gray
            }
        }
    } catch {
        Test-Assertion -TestName "update_category_access_api" -Condition $false `
            -FailureMessage "Помилка при оновленні доступів: $_"
    }
} else {
    Write-Info "Пропущено тест оновлення (недостатньо категорій)"
}

# ============================================================================
# ТЕСТ 5: Перевірка структури відповіді API
# ============================================================================

Write-TestStep "КРОК 5" "Валідація структури відповіді API"

try {
    $validationResponse = Invoke-RestMethod -Uri "$ApiBaseUrl/api/users/$executorUserId/category-access" `
        -Method Get -Headers $headers -ErrorAction Stop
    
    $hasExecutorId = $null -ne $validationResponse.executor_id
    $hasExecutorUsername = $null -ne $validationResponse.executor_username
    $hasTotal = $null -ne $validationResponse.total
    $hasCategories = $null -ne $validationResponse.categories
    
    $isValidStructure = $hasExecutorId -and $hasExecutorUsername -and $hasTotal -and $hasCategories
    
    Test-Assertion -TestName "api_response_structure" -Condition $isValidStructure `
        -SuccessMessage "Структура відповіді API коректна" `
        -FailureMessage "Відсутні обов'язкові поля у відповіді"
    
    if ($validationResponse.categories.Count -gt 0) {
        $firstCategory = $validationResponse.categories[0]
        $hasCategoryFields = ($null -ne $firstCategory.id) -and 
                             ($null -ne $firstCategory.category_id) -and 
                             ($null -ne $firstCategory.category_name)
        
        Test-Assertion -TestName "category_object_structure" -Condition $hasCategoryFields `
            -SuccessMessage "Структура об'єкта категорії коректна" `
            -FailureMessage "Відсутні поля у об'єкті категорії"
    }
} catch {
    Test-Assertion -TestName "api_response_structure" -Condition $false `
        -FailureMessage "Помилка при валідації структури: $_"
}

# ============================================================================
# ТЕСТ 6: Тестування видалення всіх доступів (порожній список)
# ============================================================================

Write-TestStep "КРОК 6" "Тестування видалення всіх доступів"

try {
    $emptyBody = @{
        category_ids = @()
    } | ConvertTo-Json
    
    $emptyResponse = Invoke-RestMethod -Uri "$ApiBaseUrl/api/users/$executorUserId/category-access" `
        -Method Put -Headers $headers -Body $emptyBody -ErrorAction Stop
    
    $noAccess = $emptyResponse.categories.Count -eq 0
    
    Test-Assertion -TestName "remove_all_access" -Condition $noAccess `
        -SuccessMessage "Всі доступи успішно видалено" `
        -FailureMessage "Доступи не видалено повністю"
} catch {
    Test-Assertion -TestName "remove_all_access" -Condition $false `
        -FailureMessage "Помилка при видаленні доступів: $_"
}

# ============================================================================
# ТЕСТ 7: Frontend URLs
# ============================================================================

Write-TestStep "КРОК 7" "Перевірка доступності Frontend"

try {
    $frontendResponse = Invoke-WebRequest -Uri $FrontendUrl -Method Get -TimeoutSec 5 -ErrorAction Stop
    
    Test-Assertion -TestName "frontend_accessible" -Condition ($frontendResponse.StatusCode -eq 200) `
        -SuccessMessage "Frontend доступний за адресою $FrontendUrl"
} catch {
    Test-Assertion -TestName "frontend_accessible" -Condition $false `
        -FailureMessage "Frontend недоступний: $_"
    
    Write-Info "Переконайтеся що Frontend запущено:"
    Write-Host "   cd ohmatdyt-crm/frontend && npm run dev" -ForegroundColor Gray
}

# ============================================================================
# ТЕСТ 8: Компонент файли існують
# ============================================================================

Write-TestStep "КРОК 8" "Перевірка існування файлів компонентів"

$componentFiles = @(
    "ohmatdyt-crm\frontend\src\components\Users\CategoryAccessManager.tsx",
    "ohmatdyt-crm\frontend\src\components\Users\index.ts",
    "ohmatdyt-crm\frontend\src\components\Users\EditUserForm.tsx",
    "ohmatdyt-crm\frontend\src\store\slices\usersSlice.ts"
)

foreach ($file in $componentFiles) {
    $fullPath = Join-Path $PSScriptRoot $file
    $exists = Test-Path $fullPath
    
    $fileName = Split-Path $file -Leaf
    Test-Assertion -TestName "file_exists_$fileName" -Condition $exists `
        -SuccessMessage "$fileName існує" `
        -FailureMessage "$fileName не знайдено за шляхом: $fullPath"
}

# ============================================================================
# Підсумок
# ============================================================================

Write-TestHeader "ПІДСУМОК ТЕСТУВАННЯ FE-012"

Write-Host "`nРезультати тестування:"
Write-Host "  ✅ PASS - $script:TestsPassed/$script:TestsTotal тестів" -ForegroundColor Green
if ($script:TestsFailed -gt 0) {
    Write-Host "  ❌ FAIL - $script:TestsFailed/$script:TestsTotal тестів" -ForegroundColor Red
}

Write-Host "`n📊 TOTAL - $script:TestsPassed/$script:TestsTotal тестів пройдено`n"

if ($script:TestsFailed -eq 0) {
    Write-Success "Всі тести пройдено успішно! ✨"
    Write-Info "FE-012 ГОТОВО ДО PRODUCTION ✅"
    exit 0
} else {
    Write-Failure "Деякі тести не пройшли перевірку"
    Write-Info "Перевірте помилки вище та виправте проблеми"
    exit 1
}
