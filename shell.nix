{ pkgs ? import <nixpkgs> {} }:
let
  venmoClientEnv = pkgs.poetry2nix.mkPoetryEnv {
    projectDir = ./.;
    python = pkgs.python38;
    editablePackageSources = {
      my-app = ./venmo_client;
    };
  };
in
pkgs.mkShell {
  buildInputs = [
    venmoClientEnv
    pkgs.poetry
  ];
}
