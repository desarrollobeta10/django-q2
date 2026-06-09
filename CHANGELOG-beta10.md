# Cambios Beta10 sobre el fork de django-q2

Este fichero registra las revisiones propias de Beta10 sobre el fork de
`django-q2`. Es independiente del `CHANGELOG.md` (que pertenece al proyecto
original) para evitar conflictos al sincronizar con `upstream`.

## Convención de tags

Cada vez que se modifica algo del fork que deba llegar a producción se crea un
**tag anotado** con el nombre `rev-beta10-N` (N incremental: `rev-beta10-1`,
`rev-beta10-2`, …). El requisito en `beta10-api-interna/requirements/base.txt`
se fija a ese tag.

El requisito debe apuntar siempre a un tag fijo, nunca a `master`. Así cada
release usa una versión exacta y trazable del fork: si el requisito apuntara a
`master`, un cambio interno del fork no quedaría reflejado en la referencia y el
release no podría distinguir una versión de otra.

### Cómo sacar una revisión nueva

```bash
# 1. Crear el commit del cambio en el fork (rama master)
# 2. Actualizar este fichero con la entrada de la nueva revisión
# 3. Crear el tag anotado y subirlo
git tag -a rev-beta10-N -m "rev-beta10-N: <resumen> (GLP-XXXXX)"
git push origin master rev-beta10-N
# 4. En beta10-api-interna, fijar el requisito a la nueva referencia:
#    git+ssh://git@github.com/desarrollobeta10/django-q2@rev-beta10-N
```

## Revisiones

## rev-beta10-1 — 2026-06-09

Primera revisión etiquetada. Recoge los cambios propios de Beta10 acumulados
sobre el release `v1.10.0` del proyecto original:

- Cola de tareas: error al iniciar servicio en Windows (GLP-31684).
- Corregir worker death y chain en fallo (GLP-31365).
- Sincronización con los últimos cambios del repositorio original (GLP-31114).
- Warning incorrecto con un solo reintento y sin timeout (GLP-30831).
- Revisión de colas repetitivas que se reencolan y tareas que mueren por timeout (GLP-30736).
- Compatibilidad con Oracle y requisitos adicionales.
- Detener servicio en Windows (GLP-25311).
