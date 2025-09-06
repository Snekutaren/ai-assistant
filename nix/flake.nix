{
  description = "Python 3.11 with PyTorch + ROCm 6.3";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;
            rocmTargets = [ "gfx1201" ];
          };
        };
        rocmLibs = with pkgs.rocmPackages; [
          rocminfo
          rocm-smi
          rocm-runtime
          rocblas
          miopen
          rpp
        ];
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [ pip ]);
        venvPath = "/home/owdious/dev/experimental/.venv";
        buildInputs =
          with pkgs;
          [
            git
            cmake
            ninja
            gcc
            ffmpeg
          ]
          ++ rocmLibs;
      in
      {
        devShells.default = pkgs.mkShell {
          packages = buildInputs ++ [ pythonEnv ];
          env.LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (
            [
              pkgs.python311
              pkgs.stdenv.cc.cc.lib
              pkgs.libz
              pkgs.zstd
              pkgs.portaudio
            ]
            ++ rocmLibs
          );
          #venvPath = "../.venv";
          shellHook = ''
            # Enable ROCm Triton experimental features for faster attention
            export TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1 
            export TORCH_USE_HIP_DSA=1 
            echo "[*] TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=$TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL"
            echo "[*] Entering PyTorch + ROCm 6.3 shell (gfx1201)"
            # Create top-level venv if missing
            if [ ! -d "${venvPath}" ]; then 
              echo "[*] Creating top-level virtual environment at ${venvPath}"
              python3.11 -m venv "${venvPath}" || { echo "[!] Failed to create virtual environment"; exit 1; }
            fi
            # Activate the venv
            if [ -f "${venvPath}/bin/activate" ]; then 
              source "${venvPath}/bin/activate"
            else
              echo "[!] Venv activation script not found"
              exit 1;
            fi 
            # Install PyTorch + ROCm wheels if missing
            if ! python -c 'import torch' &> /dev/null; then
              echo "[*] Installing PyTorch 2.7.1 + ROCm 6.3 wheels..."
              pip install \
                torch==2.7.1 \
                torchvision==0.22.1 \
                torchaudio==2.7.1 \
                --index-url https://download.pytorch.org/whl/rocm6.3 || { echo "[!] Failed to install PyTorch packages"; exit 1; }
            else
              echo "[*] PyTorch already installed"
            fi 
            # Install Python dependencies if missing
            pip install wheel setuptools soundfile numpy aiohttp whisper transformers sentencepiece soundfile websockets scipy librosa TTS[torch]
            pip install git+https://github.com/openai/whisper.git
            echo "[*] Python venv ready"
          '';
        };
      }
    );
}
