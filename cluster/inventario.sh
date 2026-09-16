#!/usr/bin/env bash
# Inventario del cluster para el proyecto del modelo hidrodinamico.
# Ejecutar EN EL NODO DE LOGIN:   bash inventario.sh > inventario_$(hostname -s).txt 2>&1
# y devolver el .txt. No lanza trabajos ni cambia nada.
set -u
sec(){ printf '\n===== %s =====\n' "$*"; }

sec "Maquina";            hostname -f; date; cat /etc/os-release 2>/dev/null | head -3
sec "Gestor de colas";    command -v sbatch qsub bsub 2>/dev/null; sbatch --version 2>/dev/null
sec "Clusters Slurm";     sacctmgr -n show cluster format=cluster 2>/dev/null
sec "Particiones";        sinfo -s 2>/dev/null
sec "Detalle particiones (tiempo maximo, nodos, memoria)"
scontrol show partition 2>/dev/null | grep -E 'PartitionName|MaxTime|MaxNodes|DefMemPerCPU|MaxMemPerNode|TotalCPUs|TotalNodes'
sec "Nodos por tipo (CPUs, memoria, features)"
sinfo -N -o '%P %c %m %f %G' 2>/dev/null | sort -u | head -40
sec "QOS y limites por usuario"
sacctmgr -n show qos format=name%20,maxwall,maxsubmitpu,maxjobspu,maxtrespu%40 2>/dev/null
sacctmgr -n show assoc user="$USER" format=cluster,account,partition,qos%30,maxjobs,maxsubmit,grptres%30 2>/dev/null
sec "Arrays de trabajos";  scontrol show config 2>/dev/null | grep -Ei 'MaxArraySize|MaxJobCount|OverSubscribe|SelectType'
sec "Almacenamiento y cuotas"
echo "HOME=$HOME"; env | grep -Ei '^(VSC_|SCRATCH|WORK|DATA|GLOBALSCRATCH|LOCALSCRATCH|CECI)' 2>/dev/null
( vsc-quota || my_quota || quota -s ) 2>/dev/null
df -h "$HOME" ${VSC_SCRATCH:-} ${GLOBALSCRATCH:-} 2>/dev/null

sec "Modelos oceanicos ya instalados (module)"
for p in SCHISM schism TELEMAC telemac openTELEMAC Delft3D delft3d DFlowFM D-Flow ADCIRC ROMS FVCOM SHYFEM COHERENS SLIM; do
  module -t spider "$p" 2>&1 | grep -vi 'unable\|error\|^$' | sed "s/^/[$p] /"
done
sec "Contenedores (para Delft3D-FM oficial)"; command -v apptainer singularity 2>/dev/null
sec "Librerias necesarias para compilar"
for p in GCC intel iimpi foss OpenMPI impi MPICH netCDF netCDF-Fortran HDF5 ParMETIS METIS SCOTCH MUMPS PETSc CMake Python GDAL PROJ gmsh MED; do
  module -t spider "$p" 2>&1 | grep -vi 'unable\|error\|^$' | tail -3 | sed "s/^/[$p] /"
done
sec "Toolchains cargadas por defecto"; module list 2>&1
sec "Fin"
