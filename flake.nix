{
  inputs = {
    nixpkgs.url = "github:NickCao/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let pkgs = import nixpkgs { inherit system; }; in {
          packages.default = with pkgs.python3Packages; buildPythonApplication {
            name = "ruyi-ng";
            src = self;

            format = "pyproject";

            nativeBuildInputs = [ poetry-core ];
            propagatedBuildInputs = [ click ];
          };
        }
      );
}
