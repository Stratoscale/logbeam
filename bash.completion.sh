_logbeam()
{
  _script_commands="upload webfrontend ftpserver"

  local cur prev
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  COMPREPLY=( $(compgen -W "${_script_commands}" -- ${cur}) )

  return 0
}
complete -o nospace -F _logbeam logbeam
