param([ValidateSet('status','create','delete')][string]$Action = 'status')
Write-Host "Hugging Face endpoint action requested: $Action. Configure provider credentials before production use."
