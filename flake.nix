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
            shellHook = ''
              export PYTHONPATH="$(pwd)/src:$PYTHONPATH"
              export AWS_ACCESS_KEY_ID="testKey"
              export AWS_SECRET_ACCESS_KEY="secretKey"
              export AWS_DEFAULT_REGION="us-east-1"
              export JWE_ENCRYPTION_KEY='{"k":"ila0UViizq2Aqk7H4Duai-9sYTHbUXkKp0elOFbYTkE","kty":"oct"}'
              export JWT_SIGNING_KEY="c10c5cde58a9e4396b00f824673bebd5cb9686b4f6ceba197f1d4dbf61e585be5ac366d484831fd60114f95093fc4d76c53bc97035e25cfe31eec20f2d0a8527"
              export OAUTH_GOOGLE_CLIENT_ID="960572939057-p40kke46pr4acakcnpil52igbtl875h1.apps.googleusercontent.com"
              export OAUTH_GOOGLE_SECRET="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"
            '';
          };
          apps = {
            default = {
              program = "${self.packages.${system}.api}/bin/vuln-api";
              type = "app";
            };
            deployDynamoDb = {
              program = "${self.packages.${system}.dynamoDb}/bin/dynamodb-local";
              type = "app";
            };
          };
          packages = {
            api = with pkgs; builtins.derivation {
              inherit projectSrc system;
              args = [./builders/api.sh];
              bash = "${bash}";
              buildInputs = [
                coreutils
                "${self.packages.${system}.dynamoDb}"
                gnused
                pyenvRun
              ];
              builder = "${bash}/bin/bash";
              entrypoint = ./builders/api_entrypoint.sh;
              name = "api";
            };
            dynamoDb = with pkgs; builtins.derivation {
              inherit system;
              args = [./builders/dynamodb.sh];
              bash = "${bash}";
              buildInputs = [
                coreutils
                gnused
                lsof
                openjdk_headless
                terraform
                terraform-providers.aws
                unzip
              ];
              builder = "${bash}/bin/bash";
              dynamoDbZip = pkgs.fetchurl {
                url = "https://s3.us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_2022-09-10.zip";
                sha256 = "7ec2f8d538f4b026dacecc944ef68dc5a39878b702c866365f286c8e349d81e1";
              };
              entrypoint = ./builders/dynamodb_entrypoint.sh;
              name = "dynamodb";
              src = ./infra;
            };
            docker = with pkgs; dockerTools.buildLayeredImage {
              name = "vuln-api";
              contents = [ "${self.packages.${system}.api}" ];
              config = {
                Cmd = [ "/bin/vuln-api" ];
              };
            };
            lintPython = with pkgs; builtins.derivation {
              inherit projectSrc system;
              args = [./builders/lint_python.sh];
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
            testPython = with pkgs; builtins.derivation {
              inherit projectSrc system;
              args = [./builders/test_python.sh];
              buildInputs = [
                coreutils
                pyenvDev
                pyenvRun
              ];
              builder = "${bash}/bin/bash";
              name = "test-python-code";
            };
          };
        }
    );
}
