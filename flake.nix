{
  inputs = {
    nixpkgs.url = "github:NickCao/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
    nix-appimage = {
      url = "github:ralismark/nix-appimage";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs = { self, nixpkgs, flake-utils, nix-appimage }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let pkgs = import nixpkgs { inherit system; }; in with pkgs; {
          packages = rec {
            default = with python3Packages; buildPythonApplication {
              name = "ruyi-ng";
              src = self;

              format = "pyproject";

              nativeBuildInputs = [ poetry-core ];
              propagatedBuildInputs = [ click ];

              makeWrapperArgs = [
                "--prefix"
                "PATH"
                ":"
                (lib.makeBinPath [ bubblewrap ostree ostree-rs-ext ])
              ];

              meta.mainProgram = "ruyi";
            };

            appimage = nix-appimage.mkappimage.${system} {
              drv = default;
              entrypoint = lib.getExe default;
              name = default.name;
            };
          };
        }
      );
}
