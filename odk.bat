@echo off

set ODK_JAVA_OPTS=-Xmx20G

set "_path=%%cd%%"
for %%a in ("%_path%") do set "p_dir=%%~dpa"
docker run -v "%p_dir%\":/work -w /work -e 'ROBOT_JAVA_ARGS=%ODK_JAVA_OPTS%' -e 'JAVA_OPTS=%ODK_JAVA_OPTS%' --rm -ti obolibrary/odkfull %*