DATALOADER_DOMAIN_TARGET=User
MOCK_DOMAIN_TARGET=item.go
MIGRATE_FILE=initialize

get-sa:
	gcloud secrets --project=midi-converter-314311 versions access latest --secret=chord-analysis-sa-key > sa-key.json

.PHONY: run-api


