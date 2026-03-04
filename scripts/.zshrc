# Load pyenv automatically by appending
# the following to
# ~/.zprofile (for login shells)
# and ~/.zshrc (for interactive shells) :

export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - zsh)"


# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH
# Performance optimizations
DISABLE_AUTO_UPDATE="true"
DISABLE_MAGIC_FUNCTIONS="true"
DISABLE_COMPFIX="true"

# Cache completions aggressively
autoload -Uz compinit
if [ "$(date +'%j')" != "$(stat -f '%Sm' -t '%j' ~/.zcompdump 2>/dev/null)" ]; then
    compinit
else
    compinit -C
fi


# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time Oh My Zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
ZSH_THEME="spaceship"

SPACESHIP_PROMPT_ASYNC=true
SPACESHIP_PROMPT_ADD_NEWLINE=true
SPACESHIP_CHAR_SYMBOL="⚡"

SPACESHIP_TIME_SHOW=true
SPACESHIP_DIR_SHOW= true 

SPACESHIP_GIT_BRANCH_SHOW=true
SPACESHIP_GIT_COMMIT_SHOW=true
SPACESHIP_GIT_STATUS_SHOW=true

SPACESHIP_PROMPT_ORDER=(
	line_sep
    char
    time
    dir
    git
)

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in $ZSH/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment one of the following lines to change the auto-update behavior
# zstyle ':omz:update' mode disabled  # disable automatic updates
# zstyle ':omz:update' mode auto      # update automatically without asking
# zstyle ':omz:update' mode reminder  # just remind me to update when it's time

# Uncomment the following line to change how often to auto-update (in days).
# zstyle ':omz:update' frequency 13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS="true"

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# You can also set it to another string to have that shown instead of the default red dots.
# e.g. COMPLETION_WAITING_DOTS="%F{yellow}waiting...%f"
# Caution: this setting can cause issues with multiline prompts in zsh < 5.7.1 (see #5765)
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(
	git
	zsh-syntax-highlighting
  	zsh-autosuggestions
  	docker-compose
)

source $ZSH/oh-my-zsh.sh

# User configuration
SPACESHIP_PROMPT_ADD_NEWLINE=true

ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=#663399,standout"
ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE="20"
ZSH_AUTOSUGGEST_USE_ASYNC=1



# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='nvim'
# fi

# Compilation flags
# export ARCHFLAGS="-arch $(uname -m)"

# Set personal aliases, overriding those provided by Oh My Zsh libs,
# plugins, and themes. Aliases can be placed here, though Oh My Zsh
# users are encouraged to define aliases within a top-level file in
# the $ZSH_CUSTOM folder, with .zsh extension. Examples:
# - $ZSH_CUSTOM/aliases.zsh
# - $ZSH_CUSTOM/macos.zsh
# For a full list of active aliases, run `alias`.
#
# Example aliases
 alias zshconfig="mate ~/.zshrc"
 alias ohmyzsh="mate ~/.oh-my-zsh"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm

export PATH="$HOME/.yarn/bin:$HOME/.config/yarn/global/node_modules/.bin:$PATH"

# check running connections

alias redes='echo "Checking running connections (password required)  ... " && sudo lsof -iTCP -sTCP:LISTEN -P -n'

################################################################################
#                            Project Aliases                                   #
################################################################################

# Alias for AstroChat project
export ASTROCHAT_HOME='/Users/macnolo/Desktop/Code/AstroChat'

alias astro-start='cd $ASTROCHAT_HOME && netlify dev'
alias astro-build='cd $ASTROCHAT_HOME && netlify build'

# Supabase Alias

alias sup-start='npx supabase start'
alias sup-status='npx supabase status'
alias sup-stop='npx supabase stop'

alias sup-local='psql postgresql://postgres:postgres@127.0.0.1:54322/postgres'


#
# Alias for Orchestrator Agent project
export ORCHESTRATOR_HOME='/Users/macnolo/Desktop/Code/OrchestratorIva'

alias orchestrator='cd $ORCHESTRATOR_HOME && source .venv/bin/activate'
alias orchestrator-install='cd $ORCHESTRATOR_HOME && source .venv/bin/activate && ./scripts/install_requirements.sh'
alias orchestrator-start='cd $ORCHESTRATOR_HOME && source .venv/bin/activate && ./scripts/run_agent.sh'



# Alias for Rag agent project
#export RAG_HOME='/Users/macnolo/Desktop/Code/RagIvaconsulta'
export RAG_HOME='/Users/macnolo/Desktop/Code/VatDeep_local/rag'

alias rag='cd $RAG_HOME && source .venv/bin/activate'
alias rag-install='cd $RAG_HOME && source .venv/bin/activate && ./scripts/install_requirements.sh'
alias rag-format='cd $RAG_HOME && source .venv/bin/activate && ./scripts/format_code.sh'
alias rag-test='cd $RAG_HOME && source .venv/bin/activate && ./scripts/run_tests.sh'
alias rag-files='cd $RAG_HOME && source .venv/bin/activate && ./scripts/run_files_manager.sh'
alias rag-start='cd $RAG_HOME && source .venv/bin/activate && ./scripts/run_agent.sh'

# RagIvaconsulta - Force local database storage
export CREWAI_STORAGE_DIR="$HOME/Desktop/Code/RagIvaconsulta/db"
export CHROMA_DB_PATH="$HOME/Desktop/Code/RagIvaconsulta/db"

#Alias for IvaConsulta Wordpress project
export IVACONSULTA_HOME='opt/lampp/htdocs/ivaconsulta'
alias iva-repo='cd ../.. && cd $IVACONSULTA_HOME'

alias iva-stop='cd &&  sudo /opt/lampp/lampp stop'
alias iva-start='cd &&  sudo /opt/lampp/lampp start'
alias iva-status='cd &&  sudo /opt/lampp/lampp status'
alias iva-restart='cd  sudo /opt/lampp/lampp restart'



#Alias for SAP Rag agent project

export SAP_RAG_HOME='/Users/macnolo/Desktop/Code/SapRagTool'
alias sap-rag='cd $SAP_RAG_HOME && source .venv/bin/activate'
alias sap-rag-test='cd $SAP_RAG_HOME && source .venv/bin/activate && ./scripts/run_tests.sh'
alias sap-rag-format='cd $SAP_RAG_HOME && source .venv/bin/activate && ./scripts/format_code.sh'
alias sap-rag-install='cd $SAP_RAG_HOME && source .venv/bin/activate && ./scripts/install_requirements.sh'
alias sap-rag-start='cd $SAP_RAG_HOME && source .venv/bin/activate && ./scripts/run_agent.sh'
alias sap-rag-files='cd $SAP_RAG_HOME && source .venv/bin/activate && ./scripts/run_files_manager.sh'


# Alias for Acps agent project

# ACPS Project Environment
export ACPS_HOME="/home/lolou/ACPS"

# Quick navigation
alias acps='cd $ACPS_HOME && source .venv/bin/activate'

# Aliases using environment variable
alias acps-rag='cd $ACPS_HOME && source .venv/bin/activate && ./run_crewai.sh'
alias acps-orquestrator='cd $ACPS_HOME && source .venv/bin/activate && ./run_orquestrator.sh'
alias acps-smol='cd $ACPS_HOME && source .venv/bin/activate && ./run_smolagents.sh'
# Created by `pipx` on 2025-10-27 09:21:48
export PATH="$PATH:/Users/macnolo/.local/bin"

alias mysql=/Applications/MAMP/Library/bin/mysql80/bin


wsSvTEYarjroS2TJWnfcvs50xE1Tpz6uSuxGR0bwS8sa1ztiN9ACbBsNhNq2D4QQDNp9rltu8BpF8dNfZXm7lT4zdfqGCynMW5zcEzOkxzNHLTsjxK32Bf4OZ4TyjcsK
