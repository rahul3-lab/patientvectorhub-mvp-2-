param([string]$QdrantUrl = 'http://localhost:6333')
Invoke-RestMethod -Method Put -Uri "$QdrantUrl/collections/patient_chunks" -ContentType 'application/json' -Body '{"vectors":{"size":128,"distance":"Cosine"}}'
Write-Host 'Created Qdrant patient_chunks collection.'
