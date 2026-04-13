$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false
$xl.DisplayAlerts = $false
$wb = $xl.Workbooks.Open('C:\Users\Administrator\ClaudeProjects\SalesCostValidator\EMEA ThinkNB Costing and pricing ZS 20250702.xlsx')
$sheets = $wb.Sheets | ForEach-Object { $_.Name }
Write-Output ("SHEETS: " + ($sheets -join " | "))
foreach ($sn in @("Pricing with sales costs", "LSUMP_Data", "Upsell standard costs", "Base")) {
    Write-Output ""
    Write-Output "======= $sn ======="
    $ws = $wb.Sheets.Item($sn)
    for ($r = 1; $r -le 60; $r++) {
        $cells = @()
        for ($c = 1; $c -le 18; $c++) { $cells += $ws.Cells($r,$c).Text }
        $line = $cells -join " | "
        if ($line.Trim().Replace("|","").Trim() -ne "") { Write-Output $line }
    }
}
$wb.Close($false)
$xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
