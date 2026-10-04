{
  description = "323 Colonial website development tools";

  # Enter with nix develop; run npm test or node .pi/skills/impeccable/scripts/detect.mjs.
  # Update dependencies with npm install --package-lock-only --ignore-scripts,
  # then re-enter nix develop to refresh the Nix-managed node_modules links.

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { nixpkgs, ... }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
    in
    {
      devShells = nixpkgs.lib.genAttrs systems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          nodejs = pkgs.nodejs_24;
        in
        {
          default = pkgs.mkShell {
            packages = [ nodejs pkgs.importNpmLock.hooks.linkNodeModulesHook ];
            # ESM imports ignore NODE_PATH: link locked packages into node_modules.
            npmDeps = pkgs.importNpmLock.buildNodeModules {
              inherit nodejs;
              npmRoot = ./.;
              derivationArgs.npmFlags = [ "--ignore-scripts" ];
            };
          };
        });
    };
}
