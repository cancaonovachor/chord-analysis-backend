PROJECT_ID=midi-converter-314311
SECRET_NAME=chord-analysis-sa-key


get-sa:
	gcloud secrets --project=${PROJECT_ID} versions access latest --secret=${SECRET_NAME} > sa-key.json

.PHONY: run-api


