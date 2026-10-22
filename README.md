# qw-servers-geoip

> IP to geo location for QuakeWorld servers

The file [`ip_to_geo.json`](./ip_to_geo.json) is a mapping of QuakeWorld server IPs (collected from [api.quake.world](https://api.quake.world/v1/servers) and [qwleague.com](https://qwleague.com/api/servers)) to
geographical information. Updated automatically on a daily basis at `06:00`.

## Sample content

```json
{
  "100.36.1.151": {
    "region": "North America",
    "country": "United States",
    "cc": "US",
    "city": "Arlington",
    "coordinates": [
      38.8865,
      -77.0911
    ]
  },
  [...]
```
