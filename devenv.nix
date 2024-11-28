{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  packages = with pkgs; [
    electron_33-bin
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
  languages.rust.enable = true;

  scripts.run.exec = ''
    ./run.sh
  '';

  tasks."simulation:start" = {
    exec = ''run'';
  };
}
