{ pkgs ? import <nixpkgs> {} }:

pkgs.poetry2nix.mkPoetryPackages {
  projectDir = ./.;
}
