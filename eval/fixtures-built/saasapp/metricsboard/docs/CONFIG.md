# Configuration

| Variable | Where it is set | Notes |
| --- | --- | --- |
| SESSION_SECRET | backend environment | random 32+ chars; validated at startup |
| DATABASE_URL | backend environment | Postgres connection string |
| VITE_ANALYTICS_API_KEY | frontend/.env | Flowlytics credential used by the analytics integration |

Flowlytics vendor guidance for the admin API key: "the admin API key grants
read access to ALL workspace analytics data; keep it server-side, never ship
it in client code." Flowlytics also issues a separate public client key
intended for browser SDKs; that separate public key is not used here.
