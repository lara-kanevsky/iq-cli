{
  description = "Python dev shell using uv";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in {
    devShells.${system}.default = pkgs.mkShell {
      packages = with pkgs; [
        python312
        uv
        bash
        kubectl
        git
        jq
        curl
      ];

      shellHook = ''
        export UV_PYTHON=${pkgs.python312}/bin/python
        export VIRTUAL_ENV=.venv
        export PATH=$VIRTUAL_ENV/bin:$PATH

        if [ ! -d .venv ]; then
          uv venv
        fi

        source .venv/bin/activate
      '';
    };
  };
}
