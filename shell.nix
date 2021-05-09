{ pkgs ? import <nixpkgs> {} }:
with pkgs;
let
  beancount = pkgs.callPackage ../beancount/beancount.nix {
    pythonPackages = python38Packages;
  };
  finance_dl = pkgs.callPackage ../finance-dl/finance_dl.nix {
    pythonPackages = python38Packages;
  };
  beancount_import = pkgs.callPackage ../beancount-import/beancount_import.nix {
    pythonPackages = python38Packages;
  };
  venmo_client = pkgs.callPackage ../venmo-client/venmo_client.nix {
    pythonPackages = python38Packages;
  };
in
  (python38.withPackages (ps: with ps;[
    beancount
    venmo_client
    finance_dl
    beautifulsoup4
    beancount_import
    click
    atomicwrites
    pytest
    ofxclient
    lxml
    jsonschema
    numpy
    pandas
  ])).env
