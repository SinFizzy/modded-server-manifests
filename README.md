# modded-server-manifests

Mod lists for the game servers Devin hosts. The [Modded Server Launcher](https://github.com/SinFizzy/modded-server-launcher) reads these files to keep each player's mods matched to the server.

**Players:** you don't need anything here. Use the invite link the host sent you.

## Layout

```
servers/
  <server-id>/
    manifest.json      one per server; the folder name must match server.id
schema/
  manifest.v1.schema.json   rules every manifest must follow
.github/
  workflows/validate.yml    automatic check on every change
  scripts/validate_manifests.py
```

## What's in a manifest

The game, the mod loader, and each mod's exact version, download link on its original site (Thunderstore today, more sites later) and SHA-256 hash. Players' launchers check every downloaded file against that hash. Nothing is re-hosted here. See the [manifest format](https://github.com/SinFizzy/modded-server-launcher/blob/main/docs/manifest-format.md) for every field.

Each server's launcher link points at its file's raw address:

```
https://raw.githubusercontent.com/SinFizzy/modded-server-manifests/main/servers/<server-id>/manifest.json
```

## Adding or changing a server

Use the manifest tool from the code repo so hashes and dates are filled in for you:

```bash
manifest-tool new servers/devins-world/manifest.json --id devins-world --name "Devin's World" --game valheim
manifest-tool add servers/devins-world/manifest.json thunderstore denikson-BepInExPack_Valheim --loader
manifest-tool add servers/devins-world/manifest.json thunderstore Azumatt-ProximityVoiceChat
```

Commit and push. The **Check manifests** action runs on every change and fails if a manifest breaks the rules, so check its result before telling players to update.

## Never put these here

This repo is public. The automatic check looks for these, but don't rely on it:

- Server IP addresses or ports (they go in invite links)
- Passwords, tokens or API keys
- Discord webhook URLs
