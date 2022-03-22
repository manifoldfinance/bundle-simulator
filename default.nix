let
  mach-nix = import (builtins.fetchGit {
    url = "https://github.com/DavHau/mach-nix";
    ref = "refs/tags/3.4.0";
  }) {
    python = "python310";
    pypiDataRev = "ff8a7c89a967ed480864d47b090d373f240421a4";
    pypiDataSha256 = "0qz7hsld0x8lviyzszpq3i29zchwa8nassdna5ccyhl5xh6zkcvi";
  };
in
mach-nix.mkPythonShell {
  requirements = builtins.readFile ./requirements.txt;
}