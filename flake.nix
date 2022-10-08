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
            inherit pkgs python;
            pypiDataRev = "207b45139d020d459c8e2f70409668f1559d3e95";
            pypiDataSha256 = "0w64x47scn0cj854ddnafklljaivv2zigr4zzcvi3b80lfy1ks9f";
          };
          pkgs = nixpkgs.legacyPackages.${system};
          pyenv-dev = mach-nix-wrapper.mkPython {
            inherit python;
            requirements = builtins.readFile ./requirements-dev.txt;
          };
          pyenv-run = mach-nix-wrapper.mkPython {
            inherit python;
            requirements = builtins.readFile ./requirements-run.txt;
          };
          python = "python310";
        in {
          devShell = pkgs.mkShell {
            buildInputs = with pkgs; [
              pyenv-dev
              pyenv-run
            ];
            shellHook =
              ''
                export MYPY_PYTHON=${pyenv-run}/bin/python
              '';
          };
        }
    );
}
