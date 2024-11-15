{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  # https://devenv.sh/basics/
  env.GREET = "devenv";

  # https://devenv.sh/packages/
  packages = with pkgs; [
    git
    nushell
    parallel
  ];

  languages.python = {
    enable = true;
    version = "3.12";
    poetry = {
      enable = true;
      install = {
        enable = true;
        installRootPackage = true;
      };
      activate.enable = true;
    };
  };

  scripts.run.exec = ''
    ./run.sh
  '';
}
