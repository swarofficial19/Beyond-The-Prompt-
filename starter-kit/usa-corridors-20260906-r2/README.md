# NYC and Dallas–Fort Worth corridor exports

Portable JSON exports from the active Mongo bundle `usa-corridors-20260906-r2`.
The files are read-only snapshots; applications should not infer a newer release by
directory order. Use `EXPORT_MANIFEST.json` for the pinned release IDs, counts and
SHA-256 checksums.

## Files

- `NYC_CORRIDORS.full.json` — 65 corridor records (60 macro and 5 sub-corridors),
  55 audience segments, 31 café archetypes, 1,860 corridor/archetype scores, 25
  special zones and 60 bounded map-context records.
- `NYC_CORRIDOR_H3_10_OWNERSHIP.json` — all 81,767 exact H3-10 ownership rows plus
  an H3-9 display projection grouped by corridor. H3-10 is the authoritative grain.
- `DALLAS_FORT_WORTH_CORRIDORS.full.json` — 72 corridors, 55 audience segments, 31
  café plus 36 restaurant archetypes, 4,824 corridor/archetype scores, 37 special
  zones, 72 map envelopes and 72 bounded map-context records.
- `EXPORT_MANIFEST.json` — release lineage, record counts, byte sizes and checksums.

## Important geometry distinction

NYC has canonical, non-overlapping H3-10 corridor ownership. Dallas–Fort Worth does
not yet have canonical H3-10 ownership; its exported H3-9 geometry is a named activity
display envelope and must not be treated as a parcel boundary or exact site catchment.

## Rebuilding

Run `v26/scripts/export_corridor_data.py` against the active Mongo bundle. The script
resolves releases through the live bundle pointer and accepts explicit metro IDs; it
does not choose releases from directory order.
