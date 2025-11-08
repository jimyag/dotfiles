#!/bin/bash
set -euo pipefail

# Install oh-my-zsh if not already installed or if installation is incomplete
if [ ! -d "$HOME/.oh-my-zsh" ] || [ ! -f "$HOME/.oh-my-zsh/oh-my-zsh.sh" ]; then
  # Use RUNZSH=no to prevent auto-switching during installation
  # We'll switch the default shell manually after installation
  if [ -d "$HOME/.oh-my-zsh" ] && [ ! -f "$HOME/.oh-my-zsh/oh-my-zsh.sh" ]; then
    echo "oh-my-zsh directory exists but installation appears incomplete, reinstalling..." >&2
    rm -rf "$HOME/.oh-my-zsh"
  fi
  RUNZSH=no sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
else
  echo "oh-my-zsh already installed, skipping installation" >&2
fi

# Setup sudo helper function
if ! command -v sudo >/dev/null 2>&1; then
  if [ "${EUID:-$(id -u)}" -eq 0 ]; then
    sudo() {
      "$@"
    }
  else
    echo "sudo not available; cannot change default shell automatically" >&2
  fi
fi

# Switch default shell to zsh if zsh is installed and not already the default
if command -v zsh >/dev/null 2>&1; then
  current_shell="$(getent passwd "$(id -u)" | cut -d: -f7)"
  zsh_path="$(command -v zsh)"
  if [ "$current_shell" != "$zsh_path" ]; then
    if command -v chsh >/dev/null 2>&1; then
      echo "Switching default shell to zsh..." >&2
      if command -v sudo >/dev/null 2>&1 || [ "${EUID:-$(id -u)}" -eq 0 ]; then
        sudo chsh -s "$zsh_path" "$(id -un)" || echo "Warning: Failed to change default shell. You may need to run 'sudo chsh -s $(which zsh)' manually." >&2
      else
        echo "Warning: sudo not available; cannot change default shell. You may need to run 'sudo chsh -s $(which zsh)' manually." >&2
      fi
    else
      echo "chsh not available; cannot change default shell automatically" >&2
    fi
  else
    echo "zsh is already the default shell" >&2
  fi
fi

# Install zsh-autosuggestions plugin if not already installed
if [ ! -d "$HOME/.oh-my-zsh/custom/plugins/zsh-autosuggestions" ]; then
  git clone https://github.com/zsh-users/zsh-autosuggestions "$HOME/.oh-my-zsh/custom/plugins/zsh-autosuggestions"
else
  echo "zsh-autosuggestions plugin already installed, skipping" >&2
fi

# Install fast-syntax-highlighting plugin if not already installed
if [ ! -d "$HOME/.oh-my-zsh/custom/plugins/fast-syntax-highlighting" ]; then
  git clone https://github.com/zdharma-continuum/fast-syntax-highlighting.git "$HOME/.oh-my-zsh/custom/plugins/fast-syntax-highlighting"
else
  echo "fast-syntax-highlighting plugin already installed, skipping" >&2
fi

# Install zsh-wakatime plugin if not already installed
if [ ! -d "$HOME/.oh-my-zsh/custom/plugins/zsh-wakatime" ]; then
  git clone https://github.com/wbingli/zsh-wakatime.git "$HOME/.oh-my-zsh/custom/plugins/zsh-wakatime"
else
  echo "zsh-wakatime plugin already installed, skipping" >&2
fi

# Install powerlevel10k theme if not already installed
if [ ! -d "$HOME/.oh-my-zsh/custom/themes/powerlevel10k" ]; then
  git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$HOME/.oh-my-zsh/custom/themes/powerlevel10k"
else
  echo "powerlevel10k theme already installed, skipping" >&2
fi
