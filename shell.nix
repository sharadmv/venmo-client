{ pkgs ? import <nixpkgs> {} }:
let
  pythonEnv = pkgs.poetry2nix.mkPoetryEnv {
    projectDir = ./.;
    python = pkgs.python39;
  };
in
pkgs.mkShell {
  buildInputs = with pkgs; [
    pythonEnv
    python3Packages.poetry
  ];
}
