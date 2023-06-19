{
  inputs = {
    nixpkgs.url = "github:NickCao/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let pkgs = import nixpkgs { inherit system; }; in with pkgs; {
          packages.default = with python3Packages; buildPythonApplication {
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
          };
        }
      );
}
