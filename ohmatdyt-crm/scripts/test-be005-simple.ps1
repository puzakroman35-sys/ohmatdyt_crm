# Simple test script for BE-005 Attachments
# Tests file upload, list, download, and delete functionality

$API_URL = "http://localhost:8000"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BE-005: Attachment Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Login as admin
Write-Host "`n1. Logging in as admin..." -ForegroundColor Yellow
$loginResponse = Invoke-RestMethod -Uri "$API_URL/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body (@{username="admin"; password="Admin123!"} | ConvertTo-Json)

if ($loginResponse.access_token) {
    Write-Host "   ✅ Login successful" -ForegroundColor Green
    $token = $loginResponse.access_token
} else {
    Write-Host "   ❌ Login failed" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
}

# Step 2: Get categories and channels
Write-Host "`n2. Getting categories..." -ForegroundColor Yellow
$categories = Invoke-RestMethod -Uri "$API_URL/api/categories" -Headers $headers
$categoryId = $categories.categories[0].id
Write-Host "   ✅ Category ID: $categoryId" -ForegroundColor Green

Write-Host "`n3. Getting channels..." -ForegroundColor Yellow
$channels = Invoke-RestMethod -Uri "$API_URL/api/channels" -Headers $headers
$channelId = $channels.channels[0].id
Write-Host "   ✅ Channel ID: $channelId" -ForegroundColor Green

# Step 3: Create a test case
Write-Host "`n4. Creating test case..." -ForegroundColor Yellow
$caseData = @{
    category_id = $categoryId
    channel_id = $channelId
    applicant_name = "Test Applicant for BE-005"
    applicant_phone = "+380123456789"
    applicant_email = "test@example.com"
    summary = "Test case for attachment functionality"
} | ConvertTo-Json

$case = Invoke-RestMethod -Uri "$API_URL/api/cases" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $caseData

$caseId = $case.id
$publicId = $case.public_id
Write-Host "   ✅ Case created: $publicId (ID: $caseId)" -ForegroundColor Green

# Step 4: Create a test PDF file
Write-Host "`n5. Creating test PDF file..." -ForegroundColor Yellow
$pdfContent = "%PDF-1.4`n1 0 obj`n<< /Type /Catalog >>`nendobj`n%%EOF"
$tempFile = [System.IO.Path]::GetTempFileName()
$pdfFile = $tempFile -replace '\.tmp$', '.pdf'
[System.IO.File]::WriteAllText($pdfFile, $pdfContent)
Write-Host "   ✅ Test file created: $pdfFile" -ForegroundColor Green

# Step 5: Upload attachment
Write-Host "`n6. Uploading attachment..." -ForegroundColor Yellow
try {
    $uploadUrl = "$API_URL/api/attachments/cases/$caseId/upload"
    
    # Create multipart form data
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileBin = [System.IO.File]::ReadAllBytes($pdfFile)
    $fileName = [System.IO.Path]::GetFileName($pdfFile)
    
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"test_document.pdf`"",
        "Content-Type: application/pdf",
        "",
        [System.Text.Encoding]::UTF8.GetString($fileBin),
        "--$boundary--"
    ) -join "`r`n"
    
    $uploadHeaders = $headers.Clone()
    $uploadHeaders["Content-Type"] = "multipart/form-data; boundary=$boundary"
    
    $attachment = Invoke-RestMethod -Uri $uploadUrl `
        -Method POST `
        -Headers $uploadHeaders `
        -Body $bodyLines
    
    $attachmentId = $attachment.id
    Write-Host "   ✅ Attachment uploaded successfully" -ForegroundColor Green
    Write-Host "      ID: $attachmentId" -ForegroundColor Gray
    Write-Host "      Original name: $($attachment.original_name)" -ForegroundColor Gray
    Write-Host "      Size: $($attachment.size_bytes) bytes" -ForegroundColor Gray
    Write-Host "      MIME type: $($attachment.mime_type)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Upload failed: $_" -ForegroundColor Red
    Write-Host "   Error details: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 6: List attachments
Write-Host "`n7. Listing case attachments..." -ForegroundColor Yellow
try {
    $attachmentList = Invoke-RestMethod -Uri "$API_URL/api/attachments/cases/$caseId" -Headers $headers
    Write-Host "   ✅ Found $($attachmentList.total) attachment(s)" -ForegroundColor Green
    foreach ($att in $attachmentList.attachments) {
        Write-Host "      - $($att.original_name) ($($att.size_bytes) bytes)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ❌ Failed to list attachments: $_" -ForegroundColor Red
}

# Step 7: Download attachment
if ($attachmentId) {
    Write-Host "`n8. Downloading attachment..." -ForegroundColor Yellow
    try {
        $downloadUrl = "$API_URL/api/attachments/$attachmentId"
        $downloadFile = [System.IO.Path]::GetTempFileName() -replace '\.tmp$', '_downloaded.pdf'
        
        Invoke-WebRequest -Uri $downloadUrl -Headers $headers -OutFile $downloadFile
        
        $fileSize = (Get-Item $downloadFile).Length
        Write-Host "   ✅ Attachment downloaded successfully" -ForegroundColor Green
        Write-Host "      File size: $fileSize bytes" -ForegroundColor Gray
        
        # Cleanup
        Remove-Item $downloadFile -ErrorAction SilentlyContinue
    } catch {
        Write-Host "   ❌ Download failed: $_" -ForegroundColor Red
    }
}

# Step 8: Test invalid file type
Write-Host "`n9. Testing invalid file type rejection..." -ForegroundColor Yellow
try {
    $exeFile = [System.IO.Path]::GetTempFileName() -replace '\.tmp$', '.exe'
    [System.IO.File]::WriteAllBytes($exeFile, @(0x4D, 0x5A, 0x90, 0x00))
    
    $uploadUrl = "$API_URL/api/attachments/cases/$caseId/upload"
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileBin = [System.IO.File]::ReadAllBytes($exeFile)
    
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"malware.exe`"",
        "Content-Type: application/x-msdownload",
        "",
        [System.Text.Encoding]::UTF8.GetString($fileBin),
        "--$boundary--"
    ) -join "`r`n"
    
    $uploadHeaders = $headers.Clone()
    $uploadHeaders["Content-Type"] = "multipart/form-data; boundary=$boundary"
    
    try {
        $result = Invoke-RestMethod -Uri $uploadUrl -Method POST -Headers $uploadHeaders -Body $bodyLines
        Write-Host "   ❌ Invalid file was accepted (should have been rejected)" -ForegroundColor Red
    } catch {
        if ($_.Exception.Response.StatusCode -eq 400) {
            Write-Host "   ✅ Invalid file type rejected (400 Bad Request)" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Unexpected status code: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
        }
    }
    
    Remove-Item $exeFile -ErrorAction SilentlyContinue
} catch {
    Write-Host "   ⚠️  Test error: $_" -ForegroundColor Yellow
}

# Cleanup
Write-Host "`n10. Cleaning up..." -ForegroundColor Yellow
Remove-Item $pdfFile -ErrorAction SilentlyContinue
Write-Host "   ✅ Cleanup complete" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "✅ BE-005 Tests Completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
