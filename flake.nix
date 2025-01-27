# see https://dream2nix.dev/guides/pip/
{
  inputs = {
    dream2nix.url = "github:nix-community/dream2nix";
    nixpkgs.follows = "dream2nix/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };
  
  outputs = { self, dream2nix, nixpkgs, flake-utils, ... }:
    {
      overlays.default = final: prev:
        let
          system = prev.stdenv.hostPlatform.system;
        in {
          aruco_generator = dream2nix.lib.evalModules {
            packageSets.nixpkgs = dream2nix.inputs.nixpkgs.legacyPackages.${system};
            modules = [
              ./default.nix
              {
                paths.projectRoot = ./.;
                # can be changed to ".git" or "flake.nix" to get rid of .project-root
                paths.projectRootFile = "flake.nix";
                paths.package = ./.;
              }
            ];
          };
        };
    } //
    (flake-utils.lib.eachDefaultSystem (system:
      let        
        pkgs = import nixpkgs {
          inherit system;
          overlays = [self.overlays.default];
        };
      in {
        packages.default = pkgs.aruco_generator;
      }
    ));
}
