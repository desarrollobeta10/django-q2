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
# 3. Subir master y esperar a que el workflow "Test django-q2 (Beta10)" salga en verde
git push origin master
# 4. Crear el tag anotado y subirlo
git tag -a rev-beta10-N -m "rev-beta10-N: <resumen> (GLP-XXXXX)"
git push origin rev-beta10-N
# 5. En beta10-api-interna, fijar el requisito a la nueva referencia:
#    git+ssh://git@github.com/desarrollobeta10/django-q2@rev-beta10-N
```

## Integración continua

`.github/workflows/test-beta10.yml` ejecuta la suite completa, con Redis y Mongo como servicios, con Python 3.12 y Django 5.2, que es lo que usan las dos líneas activas de Beta10 (producción y desarrollo; se comprueba en `https://actualizaciones.beta10.es/api/ramas` y en el `requirements/base.txt` de api-interna de cada `release/`). Va con `ubuntu-26.04` fija, no con `ubuntu-latest`. Si una línea vuelve a usar otra versión de Python o de Django, se añade como otro trabajo. Se lanza al subir a `master`, en los PR contra `master` y al subir una etiqueta `rev-beta10-*`.

Los workflows heredados del original se dejan en la repo para no tener conflictos al sincronizar. **`test.yml` hay que desactivarlo** en la pestaña *Actions* (o con `gh workflow disable tests --repo desarrollobeta10/django-q2`): lanza 14 combinaciones con `ubuntu-latest`, donde ya no hay Python 3.9, y sube la cobertura a Coveralls, así que dejaría en rojo cada subida a `master`. `release.yml` no hace falta tocarlo: su trabajo solo se ejecuta en `django-q2/django-q2`.

## Revisiones

## rev-beta10-4 — pendiente de etiquetar

- Cola de tareas: no se recupera si Oracle mata sus sesiones (GLP-32915).
  - Cerrar una conexión que la base de datos ya ha cerrado (`ORA-00028` o `ORA-03113` en Oracle, que oracledb da como `DPY-4011`) ya no aborta el centinela, el pusher, el monitor, los workers ni el programador: la conexión se descarta con un aviso en el log y la siguiente consulta abre otra. Los errores que no descartan la conexión se siguen propagando.
  - `qcluster` sale con código 1 si el centinela termina sin que se haya pedido la parada con una señal, para que el servicio de Windows lo trate como un fallo y lo reinicie. Una parada pedida sale con 0 aunque la misma señal haya terminado también el centinela.
  - Workflow propio de integración continua (`test-beta10.yml`).
  - Si el centinela muere antes de terminar de arrancar (por ejemplo, porque Oracle no responde), `Cluster.start()` lanza un error en lugar de esperar para siempre. Parte del cambio #305 del original, con dos diferencias: si la parada se ha pedido con una señal, termina sin error aunque esa señal haya terminado también el centinela, y lee `start_event` una sola vez, porque en Windows `stop()` lo pone a `None` desde otro hilo.

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
