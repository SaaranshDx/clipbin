# pista
Share text like never befour

## HTTP API

Run the server with `py -m src.main`.

Create a paste:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/pastes -Method Post `
  -ContentType 'application/json' -Body '{"data":"hello","duration":24}'
```

View it with `GET /pastes/<id>`. The duration is specified in hours.

## Cleanup daemon

The server starts the cleanup daemon automatically. Set `PISTA_PASTES_PATH`
to use a different storage directory.
