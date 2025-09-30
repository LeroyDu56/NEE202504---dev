# README

Ce fichier montre **des exemples d’utilisation** des fonctions de logs disponibles dans ce dépôt.

## Exemple Python — `logger.py`
```python
from logger import log_event

# Exemple d'utilisation : envoi d’un log
rid = log_event("ui.loaded", Source="web.kiosk", CodeLog=100, UserId=42)
print("RequestId:", rid)
```

## Exemple JavaScript (front) — `logger.js`
```js
import { logClient } from '@/lib/logger';

// Exemple d'utilisation : envoi d’un log depuis l’app web
logClient('ui.button.clicked', { CodeLog: 100, UserId: 42, RequestId: crypto.randomUUID() });
```
