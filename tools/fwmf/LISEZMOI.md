# Sang Froid - Patch FWMF

Fusionne Flat World Map Framework (carte papier) avec DynDOLOD.esp et Occlusion.esp.

Pour chaque monde que FWMF remplace et que DynDOLOD/Occlusion modifient, le patch
reprend la version DynDOLOD/Occlusion (noms FR, herbe de Blancherive, grands objets
de Solstheim, hauteurs) et n'y reporte que :
- ONAM (décalage de la carte papier) ;
- MNAM (caméra de carte) pour Tamriel et Solstheim ;
- NAM3 (eau LOD du correctif "Water for ENB") pour Tamriel et Solstheim.

Ordre des plugins (fin de liste) :
DynDOLOD.esp, Occlusion.esp, FWMF for Fantasy Paper Maps.esp, Lux patch for FWMF.esp,
Water for ENB - Patch - FWMF for Fantasy Paper Maps.esp, Sang Froid - Patch FWMF.esp

**À régénérer après chaque nouvelle passe DynDOLOD ou Occlusion :**

    LOADORDER="<loadorder.txt joint par |>" python3 build_fwmf_patch.py \
      "FWMF for Fantasy Paper Maps.esp" "Lux patch for FWMF.esp" \
      "Water for ENB - Patch - FWMF for Fantasy Paper Maps.esp" \
      DynDOLOD.esp Occlusion.esp "Sang Froid - Patch FWMF.esp"
