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
          pkgs = nixpkgs.legacyPackages.${system};
          projectSrc = ./.;

          # Use a more recent revision to fetch the latest versions
          # of the Python packages
          machNixWrapper = import mach-nix {
            inherit pkgs python;
            pypiDataRev = "207b45139d020d459c8e2f70409668f1559d3e95";
            pypiDataSha256 = "0w64x47scn0cj854ddnafklljaivv2zigr4zzcvi3b80lfy1ks9f";
          };

          # Build Python environments
          pyenvDev = machNixWrapper.mkPython {
            inherit python;
            requirements = builtins.readFile ./requirements-dev.txt;
          };
          pyenvRun = machNixWrapper.mkPython {
            inherit python;
            requirements = builtins.readFile ./requirements-run.txt;
          };
          python = "python310";
        in {
          devShell = with pkgs; mkShell {
            buildInputs = [
              python310Packages.setuptools
              pyenvDev
              pyenvRun
              terraform
              terraform-providers.aws
            ];
          };
          packages = {
            lintPython = with pkgs; builtins.derivation {
              inherit projectSrc system;
              args = [./builders/python_linter.sh];
              buildInputs = [
                coreutils
                python310Packages.setuptools
                pyenvDev
                pyenvRun
              ];
              builder = "${bash}/bin/bash";
              name = "lint-python-code";
              pythonExecutable = "${pyenvRun}/bin/python";
            };
          };
        }
    );
}
