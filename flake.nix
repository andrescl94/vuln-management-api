{
  description = "REST API useful for keeping track of security vulnerabilities in a system and their treatment status";

  inputs = {
    flake-utils.url = github:numtide/flake-utils;
    mach-nix.url = github:DavHau/mach-nix;
    nixpkgs.url = github:NixOS/nixpkgs/nixos-22.05;
  };

  outputs = { self, flake-utils, mach-nix, nixpkgs }:
    flake-utils.lib.eachDefaultSystem (
      system:
        let
          mach-nix-wrapper = import mach-nix {
            inherit pkgs;
            pypiDataRev = "207b45139d020d459c8e2f70409668f1559d3e95";
            pypiDataSha256 = "0w64x47scn0cj854ddnafklljaivv2zigr4zzcvi3b80lfy1ks9f"; 
            python = "python310";
          };
          pkgs = nixpkgs.legacyPackages.${system};
          pyenv = mach-nix-wrapper.mkPython {
            python = "python310";
            requirements = builtins.readFile ./requirements.txt;
          };
        in {
          devShell = pkgs.mkShell {
            buildInputs = with pkgs; [pyenv];
          };
        }
    );
}
